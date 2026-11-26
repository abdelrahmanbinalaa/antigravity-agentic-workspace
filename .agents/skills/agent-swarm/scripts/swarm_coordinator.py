#!/usr/bin/env python3
"""
swarm_coordinator.py — Deterministic Blackboard, DAG Lock & Maker-Checker Gate Controller
for the cross-agent `agent-swarm` skill.

Python 3.10+ stdlib only. Forces UTF-8 on stdout, stderr, and all file I/O.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

TOPOLOGIES = {
    "map-reduce",
    "specialist-council",
    "competing-hypotheses",
    "maker-checker-dag",
    "red-blue-calibration",
}

ISOLATIONS = {
    "read_only",
    "disjoint_paths",
    "worktree_share",
    "worktree_branch",
}

STANCE_DIVERSE_TOPOLOGIES = {
    "specialist-council",
    "competing-hypotheses",
    "red-blue-calibration",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_json_arg(raw: str | None) -> Any:
    if raw is None:
        return None
    s = raw.strip()
    if s.startswith("@"):
        return json.loads(Path(s[1:]).read_text(encoding="utf-8"))
    return json.loads(s)


def parse_constraints_arg(raw: str | None) -> Any:
    if raw is None:
        return ""
    s = raw.strip()
    if not s:
        return ""
    if s.startswith("@"):
        s = Path(s[1:]).read_text(encoding="utf-8").strip()
    try:
        return json.loads(s)
    except Exception:
        return s


def emit(payload: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return code


def fail(msg: str, code: int = 1) -> int:
    return emit({"ok": False, "error": msg}, code=code)


# ---------------------------------------------------------------------------
# DAG & Path Collision Helpers
# ---------------------------------------------------------------------------

def _ancestors(task_id: str, task_map: dict[str, dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    stack = list(task_map.get(task_id, {}).get("depends_on", []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur in task_map:
            stack.extend(task_map[cur].get("depends_on", []))
    return seen


def _has_cycle(task_map: dict[str, dict[str, Any]]) -> list[str] | None:
    # 0=unvisited, 1=visiting, 2=done
    state: dict[str, int] = {}
    trail: list[str] = []

    def dfs(nid: str) -> list[str] | None:
        st = state.get(nid, 0)
        if st == 1:
            idx = trail.index(nid) if nid in trail else 0
            return trail[idx:] + [nid]
        if st == 2:
            return None
        state[nid] = 1
        trail.append(nid)
        for dep in task_map[nid].get("depends_on", []):
            if dep in task_map:
                cyc = dfs(dep)
                if cyc:
                    return cyc
        trail.pop()
        state[nid] = 2
        return None

    for tid in task_map:
        if state.get(tid, 0) == 0:
            cyc = dfs(tid)
            if cyc:
                return cyc
    return None


def _norm_pattern(pat: str) -> str:
    p = pat.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    p = p.strip("/")
    return p.lower()


def _base_prefix(norm_pat: str) -> str:
    parts: list[str] = []
    for seg in norm_pat.split("/"):
        if any(ch in seg for ch in ("*", "?", "[")):
            break
        parts.append(seg)
    return "/".join(parts)


def _paths_overlap(raw_a: str, raw_b: str) -> bool:
    a = _norm_pattern(raw_a)
    b = _norm_pattern(raw_b)
    if not a or not b:
        return False
    if a == b:
        return True
    if fnmatch.fnmatch(a, b) or fnmatch.fnmatch(b, a):
        return True

    pa = _base_prefix(a)
    pb = _base_prefix(b)
    if not pa or not pb:
        # Root wildcard (e.g. "*" or "*.py") overlaps anything unless disjoint ext
        return True

    if pa == pb:
        return True
    if pa.startswith(pb + "/") or pb.startswith(pa + "/"):
        return True
    if fnmatch.fnmatch(pa, b) or fnmatch.fnmatch(pb, a):
        return True
    return False


def _find_concurrent_collisions(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    task_map = {t["id"]: t for t in tasks}
    anc_cache = {tid: _ancestors(tid, task_map) for tid in task_map}
    collisions: list[dict[str, Any]] = []

    n = len(tasks)
    for i in range(n):
        ti = tasks[i]
        if ti.get("isolation") != "disjoint_paths" or not ti.get("owned_paths"):
            continue
        for j in range(i + 1, n):
            tj = tasks[j]
            if tj.get("isolation") != "disjoint_paths" or not tj.get("owned_paths"):
                continue
            # Concurrent iff neither depends transitively on the other
            if tj["id"] in anc_cache[ti["id"]] or ti["id"] in anc_cache[tj["id"]]:
                continue
            for pa in ti["owned_paths"]:
                for pb in tj["owned_paths"]:
                    if _paths_overlap(pa, pb):
                        collisions.append({
                            "task_a": ti["id"],
                            "path_a": pa,
                            "task_b": tj["id"],
                            "path_b": pb,
                        })
    return collisions


def _write_brief(slug_dir: Path, manifest: dict[str, Any], task: dict[str, Any], task_map: dict[str, dict[str, Any]]) -> Path:
    deps = task.get("depends_on", [])
    dep_lines = []
    for d in deps:
        dep_art = slug_dir / "artifacts" / f"{d}.md"
        dep_lines.append(f"- `{d}` ({task_map.get(d, {}).get('role', '?')}): read `{dep_art}` and summary in `tasks.json`.")
    if not dep_lines:
        dep_lines.append("- None (Wave 0 — starts immediately).")

    owned = ", ".join(f"`{p}`" for p in task.get("owned_paths", [])) or "NONE (read-only / isolated)"
    artifact_target = slug_dir / "artifacts" / f"{task['id']}.md"

    brief_md = "\n".join([
        f"# Worker Brief: {task['id']} — {task['role']}",
        "",
        f"- **Swarm Goal:** {manifest.get('goal', '')}",
        f"- **Topology:** `{manifest.get('topology', '')}`",
        f"- **Cognitive Stance / Mandate:** `{task.get('cognitive_stance', '')}`",
        f"- **Isolation Mode:** `{task.get('isolation', '')}`",
        f"- **Owned Paths (do NOT edit outside these):** {owned}",
        f"- **User Constraints:** `{json.dumps(manifest.get('user_constraints', ''), ensure_ascii=False)}`",
        "",
        "## Objective",
        "",
        task.get("objective", ""),
        "",
        "## Upstream Dependencies",
        "",
        *dep_lines,
        "",
        "## Output & Blackboard Contract",
        "",
        f"1. Write detailed findings, code notes, or evidence to `{artifact_target}`.",
        "2. Do NOT self-verify. An independent verifier will audit your output.",
        f"3. Submit a concise summary (<= 1200 chars) via `swarm_coordinator.py submit-result --task-id {task['id']}`.",
        "",
    ])
    out = slug_dir / "briefs" / f"{task['id']}.md"
    out.write_text(brief_md, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Subcommand Handlers
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    if args.topology not in TOPOLOGIES:
        return fail(f"Invalid topology '{args.topology}'. Valid: {sorted(TOPOLOGIES)}")

    slug_dir = Path(args.root).expanduser().resolve() / args.slug
    slug_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("briefs", "artifacts", "verifications"):
        (slug_dir / sub).mkdir(parents=True, exist_ok=True)

    manifest = {
        "slug": args.slug,
        "created_at": now_iso(),
        "goal": args.goal,
        "topology": args.topology,
        "user_constraints": parse_constraints_arg(args.constraints),
        "gate_cmd": (args.gate_cmd or "").strip(),
    }
    tasks = {"tasks": []}
    conflicts = {"conflicts": []}
    synthesis = {
        "finalized_at": None,
        "verifier_id": None,
        "summary": "",
        "anti_groupthink_passed": False,
        "anti_sycophancy_passed": False,
        "anti_defeatism_passed": False,
        "gate_cmd_passed": False,
        "unresolved": [],
    }

    write_json(slug_dir / "swarm_manifest.json", manifest)
    write_json(slug_dir / "tasks.json", tasks)
    write_json(slug_dir / "conflicts.json", conflicts)
    write_json(slug_dir / "synthesis.json", synthesis)
    return emit({"ok": True, "swarm_dir": str(slug_dir), "topology": args.topology})


def cmd_add_task(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    manifest_path = slug_dir / "swarm_manifest.json"
    tasks_path = slug_dir / "tasks.json"
    if not manifest_path.exists() or not tasks_path.exists():
        return fail(f"Not an initialized swarm directory: {slug_dir}")

    if args.isolation not in ISOLATIONS:
        return fail(f"Invalid --isolation '{args.isolation}'. Valid: {sorted(ISOLATIONS)}")

    manifest = read_json(manifest_path)
    data = read_json(tasks_path)
    existing = data.get("tasks", [])
    task_map = {t["id"]: t for t in existing}

    deps = [d.strip() for d in (args.depends_on or "").split(",") if d.strip()]
    unknown_deps = [d for d in deps if d not in task_map]
    if unknown_deps:
        return fail(f"Unknown --depends-on task IDs (add upstream tasks first): {unknown_deps}")
    if args.id in deps:
        return fail(f"Task '{args.id}' cannot depend on itself")

    raw_paths = (args.owned_paths or "").strip()
    if not raw_paths or raw_paths.upper() == "NONE":
        owned_paths: list[str] = []
    else:
        owned_paths = [p.strip() for p in raw_paths.split(",") if p.strip()]

    new_task = {
        "id": args.id,
        "role": args.role.strip(),
        "cognitive_stance": args.cognitive_stance.strip(),
        "objective": args.objective.strip(),
        "depends_on": deps,
        "owned_paths": owned_paths,
        "isolation": args.isolation,
        "status": "pending",
        "worker_id": None,
        "summary": "",
        "artifact_path": "",
        "decisions": [],
        "risks": [],
        "verification_status": "unverified",
        "verifier_id": None,
        "created_at": now_iso(),
    }

    candidate_tasks = [t for t in existing if t["id"] != args.id] + [new_task]
    cand_map = {t["id"]: t for t in candidate_tasks}

    cyc = _has_cycle(cand_map)
    if cyc:
        return fail(f"Dependency cycle detected: {' -> '.join(cyc)}")

    collisions = _find_concurrent_collisions(candidate_tasks)
    if collisions:
        return fail(
            "Concurrent disjoint_paths collision detected: "
            f"{json.dumps(collisions, ensure_ascii=False)}. "
            "Partition owned_paths cleanly, add --depends-on ordering, or switch to worktree_share / worktree_branch."
        )

    brief_path = _write_brief(slug_dir, manifest, new_task, cand_map)
    data["tasks"] = candidate_tasks
    write_json(tasks_path, data)
    return emit({
        "ok": True,
        "task_id": args.id,
        "brief_path": str(brief_path),
        "total_tasks": len(candidate_tasks),
    })


def cmd_submit_result(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    tasks_path = slug_dir / "tasks.json"
    if not tasks_path.exists():
        return fail(f"Not an initialized swarm directory: {slug_dir}")

    summary = (args.summary or "").strip()
    if not summary:
        return fail("Anti-empty-result rule: --summary cannot be empty")
    if len(summary) > 1200:
        return fail(
            f"Anti-context-bloat rule: --summary length is {len(summary)} chars (max 1200). "
            "Write full details to artifacts/<task_id>.md and pass a concise summary."
        )

    data = read_json(tasks_path)
    tasks = data.get("tasks", [])
    target = next((t for t in tasks if t["id"] == args.task_id), None)
    if target is None:
        return fail(f"Task '{args.task_id}' not found in tasks.json")

    art_path_str = ""
    if args.artifact_file:
        src_art = Path(args.artifact_file).expanduser().resolve()
        if not src_art.exists():
            return fail(f"Artifact file not found: {src_art}")
        dest_art = slug_dir / "artifacts" / f"{args.task_id}{src_art.suffix or '.md'}"
        if src_art != dest_art:
            shutil.copyfile(src_art, dest_art)
        art_path_str = str(dest_art)
    else:
        default_art = slug_dir / "artifacts" / f"{args.task_id}.md"
        if default_art.exists():
            art_path_str = str(default_art)

    decisions = parse_json_arg(args.decisions_json) if args.decisions_json else []
    risks = parse_json_arg(args.risks_json) if args.risks_json else []
    if not isinstance(decisions, list) or not isinstance(risks, list):
        return fail("--decisions-json and --risks-json must be JSON lists")

    target["worker_id"] = args.worker_id.strip()
    target["status"] = args.status
    target["summary"] = summary
    target["artifact_path"] = art_path_str
    target["decisions"] = decisions
    target["risks"] = risks
    target["submitted_at"] = now_iso()
    # Reset prior verification whenever rework is submitted
    target["verification_status"] = "unverified"
    target["verifier_id"] = None

    write_json(tasks_path, data)
    return emit({
        "ok": True,
        "task_id": args.task_id,
        "worker_id": target["worker_id"],
        "status": target["status"],
        "artifact_path": art_path_str,
    })


def cmd_verify_task(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    tasks_path = slug_dir / "tasks.json"
    if not tasks_path.exists():
        return fail(f"Not an initialized swarm directory: {slug_dir}")

    data = read_json(tasks_path)
    tasks = data.get("tasks", [])
    target = next((t for t in tasks if t["id"] == args.task_id), None)
    if target is None:
        return fail(f"Task '{args.task_id}' not found in tasks.json")

    worker_id = (target.get("worker_id") or "").strip()
    if not worker_id:
        return fail(f"Task '{args.task_id}' has no submitted worker result to verify yet")

    verifier_id = args.verifier_id.strip()
    if not verifier_id:
        return fail("--verifier-id cannot be empty")
    if verifier_id.lower() == worker_id.lower():
        return fail(
            f"Maker != Checker violation: self-verification forbidden "
            f"(verifier '{verifier_id}' == worker '{worker_id}')."
        )

    defects = parse_json_arg(args.defects_json) if args.defects_json else []
    if not isinstance(defects, list):
        return fail("--defects-json must be a JSON list")

    ver_record = {
        "task_id": args.task_id,
        "worker_id": worker_id,
        "verifier_id": verifier_id,
        "verdict": args.verdict,
        "notes": args.notes.strip(),
        "defects": defects,
        "verified_at": now_iso(),
    }
    safe_ver_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in verifier_id)
    ver_file = slug_dir / "verifications" / f"{args.task_id}_{safe_ver_id}.json"
    write_json(ver_file, ver_record)

    target["verifier_id"] = verifier_id
    target["verification_status"] = args.verdict
    if args.verdict == "approved":
        target["status"] = "verified"
    else:
        target["status"] = "rework_required"

    write_json(tasks_path, data)
    return emit({
        "ok": True,
        "task_id": args.task_id,
        "verdict": args.verdict,
        "task_status": target["status"],
        "verification_file": str(ver_file),
    })


def cmd_log_conflict(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    cf_path = slug_dir / "conflicts.json"
    if not cf_path.exists():
        return fail(f"Not an initialized swarm directory: {slug_dir}")

    between = [b.strip() for b in args.between.split(",") if b.strip()]
    if len(between) < 2:
        return fail("--between must list at least two comma-separated task IDs")

    data = read_json(cf_path)
    items = [c for c in data.get("conflicts", []) if c.get("id") != args.id]
    items.append({
        "id": args.id,
        "between": between,
        "issue": args.issue.strip(),
        "resolution": (args.resolution or "").strip(),
        "bypass_wedge": (args.bypass_wedge or "").strip(),
        "logged_at": now_iso(),
    })
    data["conflicts"] = items
    write_json(cf_path, data)
    return emit({"ok": True, "conflict_id": args.id, "total_conflicts": len(items)})


def cmd_finalize(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    syn_path = slug_dir / "synthesis.json"
    if not syn_path.exists():
        return fail(f"Not an initialized swarm directory: {slug_dir}")

    unresolved = parse_json_arg(args.unresolved_json) if args.unresolved_json else []
    if not isinstance(unresolved, list):
        return fail("--unresolved-json must be a JSON list")

    syn = read_json(syn_path)
    syn.update({
        "finalized_at": now_iso(),
        "verifier_id": args.verifier_id.strip(),
        "summary": args.summary.strip(),
        "anti_groupthink_passed": bool(args.anti_groupthink_passed),
        "anti_sycophancy_passed": bool(args.anti_sycophancy_passed),
        "anti_defeatism_passed": bool(args.anti_defeatism_passed),
        "gate_cmd_passed": bool(args.gate_cmd_passed),
        "unresolved": unresolved,
    })
    write_json(syn_path, syn)
    return emit({"ok": True, "synthesis": syn})


# ---------------------------------------------------------------------------
# Gate Checks
# ---------------------------------------------------------------------------

def _check_plan(manifest: dict[str, Any], tasks: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    gaps: list[str] = []
    if len(tasks) < 2:
        gaps.append(f"Need >= 2 tasks in swarm plan (found {len(tasks)})")

    task_map = {t["id"]: t for t in tasks}
    cyc = _has_cycle(task_map)
    if cyc:
        gaps.append(f"Dependency cycle in DAG: {' -> '.join(cyc)}")

    collisions = _find_concurrent_collisions(tasks)
    if collisions:
        gaps.append(f"Concurrent disjoint_paths collisions: {collisions}")

    stances = {t.get("cognitive_stance", "").strip().lower() for t in tasks if t.get("cognitive_stance", "").strip()}
    topology = manifest.get("topology", "")
    if topology in STANCE_DIVERSE_TOPOLOGIES and len(stances) < 2:
        gaps.append(
            f"Topology '{topology}' requires >= 2 distinct cognitive_stance values to prevent groupthink/clones "
            f"(found {len(stances)})"
        )

    return gaps, {
        "task_count": len(tasks),
        "distinct_stances": len(stances),
        "collisions": len(collisions),
    }


def _check_execution(tasks: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    gaps: list[str] = []
    incomplete = [
        t["id"]
        for t in tasks
        if t.get("status") not in ("done", "verified") or not str(t.get("summary", "")).strip()
    ]
    if incomplete:
        gaps.append(f"Tasks not completed with valid summary: {incomplete}")
    return gaps, {"completed_tasks": len(tasks) - len(incomplete), "total_tasks": len(tasks)}


def _check_verification(tasks: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    gaps: list[str] = []
    unverified = []
    self_verified = []
    rework = []
    for t in tasks:
        if t.get("status") == "rework_required" or t.get("verification_status") == "changes_requested":
            rework.append(t["id"])
        elif t.get("verification_status") != "approved":
            unverified.append(t["id"])
        elif (t.get("verifier_id") or "").strip().lower() == (t.get("worker_id") or "").strip().lower():
            self_verified.append(t["id"])

    if rework:
        gaps.append(f"Tasks still requiring rework: {rework}")
    if unverified:
        gaps.append(f"Tasks lacking approved independent verification: {unverified}")
    if self_verified:
        gaps.append(f"Tasks with invalid self-verification: {self_verified}")

    unresolved_conflicts = [c["id"] for c in conflicts if not str(c.get("resolution", "")).strip()]
    if unresolved_conflicts:
        gaps.append(f"Conflicts lacking explicit resolution: {unresolved_conflicts}")

    return gaps, {
        "approved_tasks": sum(1 for t in tasks if t.get("verification_status") == "approved"),
        "unresolved_conflicts": len(unresolved_conflicts),
    }


def _check_final(slug_dir: Path, manifest: dict[str, Any], syn: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    gaps: list[str] = []
    for flag in ("anti_groupthink_passed", "anti_sycophancy_passed", "anti_defeatism_passed"):
        if not syn.get(flag):
            gaps.append(f"synthesis.json flag '{flag}' is not true")
    if str(manifest.get("gate_cmd", "")).strip() and not syn.get("gate_cmd_passed"):
        gaps.append(f"Project gate_cmd '{manifest['gate_cmd']}' not marked passed (gate_cmd_passed=false)")

    deliv = slug_dir / "final_deliverable.md"
    if not deliv.exists() or len(deliv.read_text(encoding="utf-8").strip()) == 0:
        gaps.append("Missing or empty final_deliverable.md")

    return gaps, {"finalized": bool(syn.get("finalized_at")), "deliverable_exists": deliv.exists()}


def cmd_gate_check(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    manifest_path = slug_dir / "swarm_manifest.json"
    if not manifest_path.exists():
        return fail(f"Not an initialized swarm directory: {slug_dir}")

    manifest = read_json(manifest_path)
    tasks = read_json(slug_dir / "tasks.json").get("tasks", [])
    conflicts = read_json(slug_dir / "conflicts.json").get("conflicts", [])
    syn = read_json(slug_dir / "synthesis.json")

    stage = args.stage
    gaps: list[str] = []
    metrics: dict[str, Any] = {}

    if stage == "plan":
        g, m = _check_plan(manifest, tasks)
        gaps.extend(g)
        metrics["plan"] = m
    elif stage == "execution":
        for name, fn in (("plan", lambda: _check_plan(manifest, tasks)), ("execution", lambda: _check_execution(tasks))):
            g, m = fn()
            gaps.extend(g)
            metrics[name] = m
    elif stage == "verification":
        for name, fn in (
            ("plan", lambda: _check_plan(manifest, tasks)),
            ("execution", lambda: _check_execution(tasks)),
            ("verification", lambda: _check_verification(tasks, conflicts)),
        ):
            g, m = fn()
            gaps.extend(g)
            metrics[name] = m
    elif stage == "final":
        for name, fn in (
            ("plan", lambda: _check_plan(manifest, tasks)),
            ("execution", lambda: _check_execution(tasks)),
            ("verification", lambda: _check_verification(tasks, conflicts)),
            ("final", lambda: _check_final(slug_dir, manifest, syn)),
        ):
            g, m = fn()
            gaps.extend(g)
            metrics[name] = m
    else:
        return fail(f"Invalid --stage '{stage}'")

    passed = len(gaps) == 0
    return emit(
        {
            "passed": passed,
            "status": "PASS" if passed else "LOOP_BACK_REQUIRED",
            "stage": stage,
            "topology": manifest.get("topology", ""),
            "metrics": metrics,
            "blocking_gaps": gaps,
        },
        code=0 if passed else 2,
    )


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="swarm_coordinator.py",
        description="Deterministic blackboard, path-collision lock, and maker-checker gate controller for agent-swarm.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("init", help="Initialize a swarm blackboard workspace")
    s.add_argument("--root", required=True)
    s.add_argument("--slug", required=True)
    s.add_argument("--goal", required=True)
    s.add_argument("--topology", required=True, choices=sorted(TOPOLOGIES))
    s.add_argument("--constraints", default="")
    s.add_argument("--gate-cmd", default="")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("add-task", help="Add a task with DAG cycle check and concurrent path-collision lock")
    s.add_argument("--dir", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--role", required=True)
    s.add_argument("--cognitive-stance", required=True)
    s.add_argument("--objective", required=True)
    s.add_argument("--depends-on", default="")
    s.add_argument("--owned-paths", default="NONE")
    s.add_argument("--isolation", default="read_only", choices=sorted(ISOLATIONS))
    s.set_defaults(func=cmd_add_task)

    s = sub.add_parser("submit-result", help="Submit compact worker result and artifact pointer")
    s.add_argument("--dir", required=True)
    s.add_argument("--task-id", required=True)
    s.add_argument("--worker-id", required=True)
    s.add_argument("--status", required=True, choices=["done", "blocked", "failed"])
    s.add_argument("--summary", required=True)
    s.add_argument("--artifact-file", default="")
    s.add_argument("--decisions-json", default="")
    s.add_argument("--risks-json", default="")
    s.set_defaults(func=cmd_submit_result)

    s = sub.add_parser("verify-task", help="Independent maker!=checker task verification")
    s.add_argument("--dir", required=True)
    s.add_argument("--task-id", required=True)
    s.add_argument("--verifier-id", required=True)
    s.add_argument("--verdict", required=True, choices=["approved", "changes_requested"])
    s.add_argument("--notes", required=True)
    s.add_argument("--defects-json", default="")
    s.set_defaults(func=cmd_verify_task)

    s = sub.add_parser("log-conflict", help="Log or resolve a contradiction/trade-off between workers")
    s.add_argument("--dir", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--between", required=True, help="Comma-separated task IDs (e.g. T01,T02)")
    s.add_argument("--issue", required=True)
    s.add_argument("--resolution", default="")
    s.add_argument("--bypass-wedge", default="")
    s.set_defaults(func=cmd_log_conflict)

    s = sub.add_parser("finalize", help="Record calibrated final audit and gate results in synthesis.json")
    s.add_argument("--dir", required=True)
    s.add_argument("--verifier-id", required=True)
    s.add_argument("--summary", required=True)
    s.add_argument("--anti-groupthink-passed", action="store_true")
    s.add_argument("--anti-sycophancy-passed", action="store_true")
    s.add_argument("--anti-defeatism-passed", action="store_true")
    s.add_argument("--gate-cmd-passed", action="store_true")
    s.add_argument("--unresolved-json", default="")
    s.set_defaults(func=cmd_finalize)

    s = sub.add_parser("gate-check", help="Validate stage readiness (0=PASS, 2=LOOP_BACK_REQUIRED)")
    s.add_argument("--dir", required=True)
    s.add_argument("--stage", required=True, choices=["plan", "execution", "verification", "final"])
    s.set_defaults(func=cmd_gate_check)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
