"""
Antigravity run_workflow runner for the `agent-swarm` skill.

Executes topological dependency waves from `<swarm_dir>/tasks.json` in parallel,
routes into an independent Verifier Pool (1 verifier per 2-3 tasks) with up to 2
rework loops, and runs a Calibrated Synthesis & Conflict-Resolution Architect.

Invoke via Antigravity `run_workflow` with Args:
  {
    "swarm_dir": "<abs_path_to_initialized_swarm_dir>",
    "worker_model": "inherit",   # optional: "flash", "flash_lite", "inherit", "pro"
    "verifier_model": "inherit"  # optional
  }
"""

import json
from pathlib import Path

swarm_dir = Path(args["swarm_dir"])
worker_model = args.get("worker_model", "inherit")
verifier_model = args.get("verifier_model", "inherit")

manifest = json.loads((swarm_dir / "swarm_manifest.json").read_text(encoding="utf-8"))
tasks = json.loads((swarm_dir / "tasks.json").read_text(encoding="utf-8")).get("tasks", [])

# Build topological waves
remaining = {t["id"]: t for t in tasks}
completed = set()
waves = []
while remaining:
    ready = [
        t for t in remaining.values()
        if all(d in completed for d in t.get("depends_on", []))
    ]
    if not ready:
        raise RuntimeError(f"Unresolvable dependency cycle among tasks: {list(remaining.keys())}")
    waves.append(ready)
    for t in ready:
        completed.add(t["id"])
        del remaining[t["id"]]

worker_schema = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string"},
        "worker_id": {"type": "string"},
        "status": {"type": "string"},
        "summary": {"type": "string"},
        "artifact_path": {"type": "string"},
        "decisions": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["task_id", "worker_id", "status", "summary", "artifact_path"],
}

def _workspace_for(task: dict) -> str:
    iso = task.get("isolation", "read_only")
    if iso == "worktree_share":
        return "share"
    if iso == "worktree_branch":
        return "branch"
    return "inherit"

async def run_worker(task: dict):
    tid = task["id"]
    brief_path = swarm_dir / "briefs" / f"{tid}.md"
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else task["objective"]
    art_path = swarm_dir / "artifacts" / f"{tid}.md"
    prompt = (
        f"You are worker '{tid}_{task['role']}' in swarm '{manifest['slug']}'.\n"
        f"Swarm dir: {swarm_dir}\n\n"
        f"{brief_text}\n\n"
        f"Write full output/evidence to `{art_path}` and return concise JSON (<1200 chars summary)."
    )
    return await agent(
        prompt=prompt,
        schema=worker_schema,
        role=f"{tid}: {task['role']}",
        workspace=_workspace_for(task),
        model=worker_model,
    )

all_worker_outputs = {}
for idx, wave in enumerate(waves, start=1):
    phase(f"Swarm Wave {idx}/{len(waves)} ({len(wave)} parallel workers)")
    results = await parallel(wave, run_worker)
    for res in results:
        all_worker_outputs[res["task_id"]] = res
    log(f"Wave {idx} finished:", [r["task_id"] for r in results])

# Independent Verifier Pool (batches of up to 3 tasks per verifier)
verifier_schema = {
    "type": "object",
    "properties": {
        "verifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "verifier_id": {"type": "string"},
                    "verdict": {"type": "string"},
                    "notes": {"type": "string"},
                    "defects": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["task_id", "verifier_id", "verdict", "notes"],
            },
        },
        "detected_conflicts": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["verifications", "detected_conflicts"],
}

batches = [tasks[i:i + 3] for i in range(0, len(tasks), 3)]

async def verify_batch(batch_pair):
    b_idx, batch = batch_pair
    verifier_name = f"verifier_pool_{b_idx}"
    payload = [
        {"task": t, "worker_output": all_worker_outputs.get(t["id"], {})}
        for t in batch
    ]
    prompt = (
        f"You are '{verifier_name}' (independent checker, NOT the author).\n"
        f"Swarm dir: {swarm_dir}\n"
        f"Goal: {manifest['goal']}\n"
        f"Project gate_cmd: {manifest.get('gate_cmd', '')}\n\n"
        "Inspect each artifact file and workspace diff in your batch. Check for hallucinations, "
        "sycophancy, defeatism, constraint violations, or contradictions between workers.\n"
        f"Batch:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
    )
    return await agent(
        prompt=prompt,
        schema=verifier_schema,
        role=f"Independent Verifier #{b_idx}",
        model=verifier_model,
    )

phase("Independent Verification & Rework Loop")
for attempt in range(2):
    ver_batches = await parallel(list(enumerate(batches, start=1)), verify_batch)
    rework_needed = []
    for vb in ver_batches:
        for v in vb.get("verifications", []):
            if v.get("verdict") != "approved":
                rework_needed.append(v)
    if not rework_needed:
        log("All tasks approved by independent verifier pool.")
        break
    log(f"Rework round {attempt + 1} for:", [r["task_id"] for r in rework_needed])
    rework_tasks = [t for t in tasks if t["id"] in {r["task_id"] for r in rework_needed}]
    rework_res = await parallel(rework_tasks, run_worker)
    for res in rework_res:
        all_worker_outputs[res["task_id"]] = res

phase("Calibrated Synthesis & Conflict Resolution")
synth = await agent(
    prompt=(
        f"Working in swarm dir {swarm_dir}:\n"
        "1. Sync all worker results and verifier approvals into swarm_coordinator.py (submit-result / verify-task).\n"
        "2. Log and explicitly resolve every contradiction via log-conflict (with a low-friction bypass wedge).\n"
        "3. Write final_deliverable.md, call swarm_coordinator.py finalize, and pass gate-check --stage final."
    ),
    schema={"type": "string"},
    role="Calibrated Synthesis Architect",
    model="inherit",
)
log("Swarm complete:", synth)
print(json.dumps({"workers": list(all_worker_outputs.keys()), "synthesis": synth}, indent=2, ensure_ascii=False))
