#!/usr/bin/env python3
"""
dr_engine.py — Deterministic Loop Controller, Ledger Manager & Quantitative Modeling Engine
for the deep-research skill.

Uses Python 3.10+ stdlib plus numpy and scipy.optimize (HiGHS) when installed.
All file I/O and console streams force UTF-8 so Arabic/Unicode paths and text work cleanly on Windows.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Force UTF-8 on Windows consoles
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

SPECIALIST_LENSES = [
    "first_principles_science",
    "technical_architecture",
    "market_unit_economics",
    "operations_supply_chain",
    "behavioral_incentives",
    "competitive_game_theory",
    "legal_regulatory_tail_risk",
    "cross_domain_analogues",
]

SOURCE_TYPES = {
    "primary_doc",
    "academic",
    "market_data",
    "code_benchmark",
    "practitioner",
    "regulatory",
}

CLAIM_TIERS = {
    "T1_PRIMARY",
    "T2_CORROBORATED",
    "T3_SINGLE_PRACTITIONER",
    "T4_INFERENCE",
}

BARRIER_TYPES = {
    "hard_law",
    "resource_limit",
    "market_friction",
    "technical_bottleneck",
    "operational_sla",
    "adoption_inertia",
}

BYPASS_PATTERNS = {
    "wedge",
    "piggyback",
    "scope_slice",
    "inversion",
    "automation",
    "partnership",
    "triz_separation",
    "legal_pivot",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


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
# Subcommand: init
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    slug_dir = Path(args.root).expanduser().resolve() / args.slug
    slug_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("sources", "models", "findings", "diffs"):
        (slug_dir / sub).mkdir(parents=True, exist_ok=True)

    brief = {
        "slug": args.slug,
        "created_at": now_iso(),
        "mode": args.mode,
        "original_question": args.question,
        "reframed_decision": args.decision or "",
        "user_constraints": parse_constraints_arg(args.constraints),
        "hypotheses": [],
        "stop_criteria": [],
    }
    horizon_map = {
        "lenses": {
            lens: {
                "applicable": True,
                "status": "pending",
                "key_questions": [],
                "findings_summary": "",
            }
            for lens in SPECIALIST_LENSES
        },
        "blind_spots": [],
        "analogues": [],
    }
    obstacles = {"obstacles": []}
    critique_gate = {
        "reviewed_at": None,
        "independent_context": False,
        "anti_sycophancy_passed": False,
        "anti_defeatism_passed": False,
        "triangulation_passed": False,
        "modeling_passed": False,
        "horizon_passed": False,
        "findings_audited": 0,
        "open_defects": [],
    }

    write_json(slug_dir / "brief.json", brief)
    write_json(slug_dir / "horizon_map.json", horizon_map)
    write_jsonl(slug_dir / "sources.jsonl", [])
    write_jsonl(slug_dir / "claims.jsonl", [])
    write_json(slug_dir / "obstacles.json", obstacles)
    write_json(slug_dir / "critique_gate.json", critique_gate)

    return emit({"ok": True, "slug_dir": str(slug_dir), "mode": args.mode})


# ---------------------------------------------------------------------------
# Subcommand: update-horizon
# ---------------------------------------------------------------------------

def cmd_update_horizon(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    brief_path = slug_dir / "brief.json"
    horizon_path = slug_dir / "horizon_map.json"
    if not brief_path.exists() or not horizon_path.exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    brief = read_json(brief_path)
    horizon = read_json(horizon_path)

    if args.decision is not None:
        brief["reframed_decision"] = args.decision
    if args.constraints is not None:
        brief["user_constraints"] = parse_constraints_arg(args.constraints)
    if args.hypotheses_json is not None:
        hyps = parse_json_arg(args.hypotheses_json)
        if not isinstance(hyps, list):
            return fail("--hypotheses-json must be a JSON list")
        brief["hypotheses"] = hyps
    if args.stop_criteria_json is not None:
        sc = parse_json_arg(args.stop_criteria_json)
        if not isinstance(sc, list):
            return fail("--stop-criteria-json must be a JSON list")
        brief["stop_criteria"] = sc

    if args.lens is not None:
        if args.lens not in horizon["lenses"]:
            return fail(f"Unknown lens '{args.lens}'. Valid: {SPECIALIST_LENSES}")
        if args.status is None:
            return fail("--status is required when updating --lens")
        lens_obj = horizon["lenses"][args.lens]
        lens_obj["status"] = args.status
        lens_obj["applicable"] = args.status != "not_applicable"
        if args.summary is not None:
            lens_obj["findings_summary"] = args.summary
        if args.key_questions_json is not None:
            kq = parse_json_arg(args.key_questions_json)
            if not isinstance(kq, list):
                return fail("--key-questions-json must be a JSON list")
            lens_obj["key_questions"] = kq

    if args.analogues_json is not None:
        analogues = parse_json_arg(args.analogues_json)
        if not isinstance(analogues, list):
            return fail("--analogues-json must be a JSON list")
        horizon["analogues"] = analogues

    if args.blind_spots_json is not None:
        bs = parse_json_arg(args.blind_spots_json)
        if not isinstance(bs, list):
            return fail("--blind-spots-json must be a JSON list")
        horizon["blind_spots"] = bs

    write_json(brief_path, brief)
    write_json(horizon_path, horizon)
    return emit({
        "ok": True,
        "covered_lenses": sum(1 for v in horizon["lenses"].values() if v.get("status") == "covered"),
        "analogues": len(horizon["analogues"]),
        "blind_spots": len(horizon["blind_spots"]),
        "hypotheses": len(brief["hypotheses"]),
    })


# ---------------------------------------------------------------------------
# Subcommand: add-source
# ---------------------------------------------------------------------------

def cmd_add_source(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    sources_jsonl = slug_dir / "sources.jsonl"
    if not (slug_dir / "brief.json").exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    if args.type not in SOURCE_TYPES:
        return fail(f"Invalid --type '{args.type}'. Valid: {sorted(SOURCE_TYPES)}")
    if not (1 <= args.credibility <= 5):
        return fail("--credibility must be between 1 and 5")

    quote = (args.quote or "").strip()
    if not quote and not args.unreachable:
        return fail("Anti-fabrication rule: --quote cannot be empty unless --unreachable is set")

    body_text = ""
    if args.body_file:
        bf = Path(args.body_file)
        if not bf.exists():
            return fail(f"Body file not found: {bf}")
        body_text = bf.read_text(encoding="utf-8")

    record = {
        "id": args.id,
        "title": args.title,
        "url": args.url,
        "type": args.type,
        "credibility": args.credibility,
        "recency": args.recency,
        "quote": quote,
        "unreachable": bool(args.unreachable),
        "disconfirming": bool(args.disconfirming),
        "added_at": now_iso(),
    }

    rows = [r for r in read_jsonl(sources_jsonl) if r.get("id") != args.id]
    rows.append(record)
    write_jsonl(sources_jsonl, rows)

    md_lines = [
        f"# {args.id}: {args.title}",
        "",
        f"- **URL:** {args.url}",
        f"- **Type:** `{args.type}`",
        f"- **Credibility:** {args.credibility}/5",
        f"- **Recency:** {args.recency}",
        f"- **Disconfirming / Opposition:** {bool(args.disconfirming)}",
        f"- **Unreachable:** {bool(args.unreachable)}",
        "",
        "## Verbatim Quote",
        "",
        f"> {quote if quote else '[UNREACHABLE SOURCE — NO VERBATIM EXTRACT]'}",
    ]
    if body_text:
        md_lines.extend(["", "## Extracted Notes / Body", "", body_text])
    (slug_dir / "sources" / f"{args.id}.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return emit({"ok": True, "source_id": args.id, "total_sources": len(rows)})


# ---------------------------------------------------------------------------
# Subcommand: add-claim
# ---------------------------------------------------------------------------

def cmd_add_claim(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    brief_path = slug_dir / "brief.json"
    sources_jsonl = slug_dir / "sources.jsonl"
    claims_jsonl = slug_dir / "claims.jsonl"
    if not brief_path.exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    if args.tier not in CLAIM_TIERS:
        return fail(f"Invalid --tier '{args.tier}'. Valid: {sorted(CLAIM_TIERS)}")

    brief = read_json(brief_path)
    mode = brief.get("mode", "standard")
    sources = {r["id"]: r for r in read_jsonl(sources_jsonl)}
    src_ids = [s.strip() for s in args.sources.split(",") if s.strip()]
    if not src_ids:
        return fail("--sources must list at least one source ID")
    missing = [s for s in src_ids if s not in sources]
    if missing:
        return fail(f"Referenced source IDs do not exist in sources.jsonl: {missing}")

    distinct_types = {sources[s]["type"] for s in src_ids}
    effective_tier = args.tier
    warning = None
    if (
        args.core_thesis
        and mode in ("standard", "exhaustive")
        and args.tier in ("T1_PRIMARY", "T2_CORROBORATED")
        and (len(src_ids) < 3 or len(distinct_types) < 2)
    ):
        effective_tier = "T3_SINGLE_PRACTITIONER"
        warning = (
            f"Core thesis '{args.id}' downgraded from {args.tier} to {effective_tier}: "
            f"has {len(src_ids)} sources across {len(distinct_types)} source types "
            "(requires >=3 independent sources across >=2 distinct source types)."
        )

    record = {
        "id": args.id,
        "statement": args.statement,
        "requested_tier": args.tier,
        "tier": effective_tier,
        "sources": src_ids,
        "distinct_source_types": sorted(distinct_types),
        "core_thesis": bool(args.core_thesis),
        "confidence": args.confidence,
        "contradicts": args.contradicts or "",
        "added_at": now_iso(),
    }

    rows = [r for r in read_jsonl(claims_jsonl) if r.get("id") != args.id]
    rows.append(record)
    write_jsonl(claims_jsonl, rows)

    out: dict[str, Any] = {
        "ok": True,
        "claim_id": args.id,
        "tier": effective_tier,
        "total_claims": len(rows),
    }
    if warning:
        out["warning"] = warning
    return emit(out)


# ---------------------------------------------------------------------------
# Subcommand: add-obstacle
# ---------------------------------------------------------------------------

def cmd_add_obstacle(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    obs_path = slug_dir / "obstacles.json"
    if not obs_path.exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    if args.barrier_type not in BARRIER_TYPES:
        return fail(f"Invalid --barrier-type '{args.barrier_type}'. Valid: {sorted(BARRIER_TYPES)}")
    if args.bypass_pattern not in BYPASS_PATTERNS:
        return fail(f"Invalid --bypass-pattern '{args.bypass_pattern}'. Valid: {sorted(BYPASS_PATTERNS)}")

    honest = (args.honest_reality or "").strip()
    wedge = (args.path_a_wedge or "").strip()
    core = (args.path_b_core or "").strip()
    moat = (args.path_c_moat or "").strip()

    if len(honest) < 20:
        return fail(
            "Anti-sycophancy gate: --honest-reality must be at least 20 characters explaining "
            "the real constraint and failure trigger without sugarcoating."
        )
    if not wedge:
        return fail(
            "Anti-defeatism gate: --path-a-wedge is required. Never dump a dead-end obstacle "
            "without an actionable low-friction wedge."
        )

    data = read_json(obs_path)
    items = [o for o in data.get("obstacles", []) if o.get("id") != args.id]
    items.append({
        "id": args.id,
        "title": args.title,
        "barrier_type": args.barrier_type,
        "honest_reality": honest,
        "bypass_pattern": args.bypass_pattern,
        "path_a_wedge": wedge,
        "path_b_core": core,
        "path_c_moat": moat,
        "added_at": now_iso(),
    })
    data["obstacles"] = items
    write_json(obs_path, data)
    return emit({"ok": True, "obstacle_id": args.id, "total_obstacles": len(items)})


# ---------------------------------------------------------------------------
# Subcommand: simulate (Monte Carlo, Pareto-MCDA, LP/MILP HiGHS)
# ---------------------------------------------------------------------------

_SAFE_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Compare,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.Eq,
    ast.NotEq,
)
_SAFE_FUNCS = {"minimum", "maximum", "where", "sqrt", "log", "exp", "abs", "clip"}


def _eval_formula(expr: str, env: dict[str, Any]) -> Any:
    import numpy as np

    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _SAFE_AST_NODES):
            raise ValueError(f"Disallowed AST node in formula: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_FUNCS:
                raise ValueError(f"Disallowed function call in formula: {ast.dump(node.func)}")
        if isinstance(node, ast.Name):
            if node.id not in env and node.id not in _SAFE_FUNCS:
                raise ValueError(f"Unknown variable '{node.id}' in formula '{expr}'")

    safe_ns: dict[str, Any] = {
        "minimum": np.minimum,
        "maximum": np.maximum,
        "where": np.where,
        "sqrt": np.sqrt,
        "log": np.log,
        "exp": np.exp,
        "abs": np.abs,
        "clip": np.clip,
    }
    safe_ns.update(env)
    return eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, safe_ns)


def _spearman_corr(x: Any, y: Any) -> float:
    import numpy as np

    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = float(np.sqrt((rx * rx).sum() * (ry * ry).sum()))
    if denom <= 1e-12:
        return 0.0
    return float((rx * ry).sum() / denom)


def _run_monte_carlo(spec: dict[str, Any]) -> dict[str, Any]:
    import numpy as np

    trials = int(spec.get("trials", 10000))
    seed = int(spec.get("seed", 42))
    rng = np.random.default_rng(seed)
    variables = spec.get("variables", {})
    formulas = spec.get("formulas", {})
    thresholds = spec.get("thresholds", {})

    if not variables or not formulas:
        raise ValueError("monte-carlo spec requires non-empty 'variables' and 'formulas'")

    samples: dict[str, Any] = {}
    for name, cfg in variables.items():
        dist = cfg.get("dist", "fixed")
        if dist == "normal":
            arr = rng.normal(float(cfg["mean"]), float(cfg["std"]), size=trials)
        elif dist == "triangular":
            arr = rng.triangular(float(cfg["low"]), float(cfg["mode"]), float(cfg["high"]), size=trials)
        elif dist == "uniform":
            arr = rng.uniform(float(cfg["low"]), float(cfg["high"]), size=trials)
        elif dist == "lognormal":
            arr = rng.lognormal(float(cfg["mean"]), float(cfg["sigma"]), size=trials)
        elif dist == "fixed":
            arr = np.full(trials, float(cfg["value"]))
        else:
            raise ValueError(f"Unsupported distribution '{dist}' for variable '{name}'")
        if "min" in cfg:
            arr = np.maximum(arr, float(cfg["min"]))
        if "max" in cfg:
            arr = np.minimum(arr, float(cfg["max"]))
        samples[name] = arr

    env = dict(samples)
    outputs: dict[str, Any] = {}
    for out_name, expr in formulas.items():
        val = np.asarray(_eval_formula(expr, env), dtype=float)
        if val.ndim == 0:
            val = np.full(trials, float(val))
        env[out_name] = val
        thr = float(thresholds.get(out_name, 0.0))
        tornado = []
        for var_name, var_arr in samples.items():
            if float(np.std(var_arr)) <= 1e-12:
                continue
            r = _spearman_corr(var_arr, val)
            tornado.append({"variable": var_name, "spearman_r": round(r, 4), "abs_r": round(abs(r), 4)})
        tornado.sort(key=lambda d: d["abs_r"], reverse=True)
        outputs[out_name] = {
            "formula": expr,
            "mean": round(float(np.mean(val)), 4),
            "std": round(float(np.std(val)), 4),
            "p10": round(float(np.percentile(val, 10)), 4),
            "p50": round(float(np.percentile(val, 50)), 4),
            "p90": round(float(np.percentile(val, 90)), 4),
            "threshold": thr,
            "prob_above_threshold": round(float(np.mean(val > thr)), 4),
            "tornado_sensitivity": tornado,
        }

    return {
        "model_type": "monte-carlo",
        "trials": trials,
        "seed": seed,
        "outputs": outputs,
    }


def _run_pareto_mcda(spec: dict[str, Any]) -> dict[str, Any]:
    import numpy as np

    criteria = spec.get("criteria", [])
    options = spec.get("options", [])
    trials = int(spec.get("perturbation_trials", 500))
    seed = int(spec.get("seed", 42))
    if not criteria or not options:
        raise ValueError("pareto-mcda spec requires non-empty 'criteria' and 'options'")

    eliminated = []
    feasible = []
    for opt in options:
        reasons = []
        for crit in criteria:
            cname = crit["name"]
            val = float(opt["scores"][cname])
            if "hard_limit" in crit and crit["hard_limit"] is not None:
                lim = float(crit["hard_limit"])
                if crit["direction"] == "max" and val < lim:
                    reasons.append(f"{cname}={val} < hard_limit {lim}")
                elif crit["direction"] == "min" and val > lim:
                    reasons.append(f"{cname}={val} > hard_limit {lim}")
        if reasons:
            eliminated.append({"name": opt["name"], "reasons": reasons})
        else:
            feasible.append(opt)

    if not feasible:
        return {
            "model_type": "pareto-mcda",
            "feasible_count": 0,
            "eliminated": eliminated,
            "pareto_frontier": [],
            "ranking": [],
        }

    # Exact non-dominated Pareto frontier
    pareto = []
    for i, a in enumerate(feasible):
        dominated = False
        for j, b in enumerate(feasible):
            if i == j:
                continue
            ge_all = True
            gt_one = False
            for crit in criteria:
                cname = crit["name"]
                va = float(a["scores"][cname])
                vb = float(b["scores"][cname])
                if crit["direction"] == "max":
                    if vb < va:
                        ge_all = False
                        break
                    if vb > va:
                        gt_one = True
                else:
                    if vb > va:
                        ge_all = False
                        break
                    if vb < va:
                        gt_one = True
            if ge_all and gt_one:
                dominated = True
                break
        if not dominated:
            pareto.append(a["name"])

    # Normalized matrix for Weighted Sum + TOPSIS
    n_opt = len(feasible)
    n_crit = len(criteria)
    raw = np.zeros((n_opt, n_crit), dtype=float)
    weights = np.array([float(c["weight"]) for c in criteria], dtype=float)
    weights = weights / weights.sum()

    for j, crit in enumerate(criteria):
        vals = np.array([float(o["scores"][crit["name"]]) for o in feasible], dtype=float)
        vmin, vmax = float(vals.min()), float(vals.max())
        if vmax - vmin <= 1e-12:
            norm = np.ones(n_opt, dtype=float)
        elif crit["direction"] == "max":
            norm = (vals - vmin) / (vmax - vmin)
        else:
            norm = (vmax - vals) / (vmax - vmin)
        raw[:, j] = norm

    def score_topsis(w: Any) -> Any:
        weighted = raw * w
        ideal_best = weighted.max(axis=0)
        ideal_worst = weighted.min(axis=0)
        d_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
        d_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))
        denom = d_best + d_worst
        return np.where(denom > 1e-12, d_worst / denom, 0.5)

    wsum = raw @ weights
    topsis = score_topsis(weights)

    rng = np.random.default_rng(seed)
    rank1_counts = np.zeros(n_opt, dtype=int)
    for _ in range(trials):
        pw = weights * rng.uniform(0.75, 1.25, size=n_crit)
        pw = pw / pw.sum()
        winner = int(np.argmax(score_topsis(pw)))
        rank1_counts[winner] += 1

    ranking = []
    for i, opt in enumerate(feasible):
        ranking.append({
            "name": opt["name"],
            "on_pareto_frontier": opt["name"] in pareto,
            "weighted_score": round(float(wsum[i]), 4),
            "topsis_score": round(float(topsis[i]), 4),
            "rank_1_stability_pct": round(100.0 * float(rank1_counts[i]) / trials, 2),
        })
    ranking.sort(key=lambda r: (r["topsis_score"], r["weighted_score"]), reverse=True)

    return {
        "model_type": "pareto-mcda",
        "feasible_count": len(feasible),
        "eliminated": eliminated,
        "pareto_frontier": pareto,
        "perturbation_trials": trials,
        "ranking": ranking,
    }


def _run_lp_optimize(spec: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, linprog, milp

    sense = spec.get("sense", "min").lower()
    c_raw = np.array(spec["c"], dtype=float)
    c = c_raw if sense == "min" else -c_raw
    n_vars = len(c)
    var_names = spec.get("var_names") or [f"x{i}" for i in range(n_vars)]

    A_ub = np.array(spec["A_ub"], dtype=float) if spec.get("A_ub") else None
    b_ub = np.array(spec["b_ub"], dtype=float) if spec.get("b_ub") is not None else None
    A_eq = np.array(spec["A_eq"], dtype=float) if spec.get("A_eq") else None
    b_eq = np.array(spec["b_eq"], dtype=float) if spec.get("b_eq") is not None else None

    raw_bounds = spec.get("bounds")
    if raw_bounds is None:
        lb = np.zeros(n_vars, dtype=float)
        ub = np.full(n_vars, np.inf, dtype=float)
    else:
        lb = np.array([(-np.inf if b[0] is None else float(b[0])) for b in raw_bounds], dtype=float)
        ub = np.array([(np.inf if b[1] is None else float(b[1])) for b in raw_bounds], dtype=float)

    integrality = spec.get("integrality")
    is_milp = bool(integrality and any(int(v) != 0 for v in integrality))

    if is_milp:
        constraints = []
        if A_ub is not None and b_ub is not None:
            constraints.append(LinearConstraint(A_ub, -np.inf, b_ub))
        if A_eq is not None and b_eq is not None:
            constraints.append(LinearConstraint(A_eq, b_eq, b_eq))
        res = milp(
            c=c,
            integrality=np.array(integrality, dtype=int),
            bounds=Bounds(lb, ub),
            constraints=constraints if constraints else None,
        )
    else:
        bounds_tuples = list(zip(lb.tolist(), ub.tolist()))
        res = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds_tuples,
            method="highs",
        )

    constraint_names = spec.get("constraint_names") or {}
    ub_names = constraint_names.get("ub") or ([f"ub_{i}" for i in range(len(b_ub))] if b_ub is not None else [])
    eq_names = constraint_names.get("eq") or ([f"eq_{i}" for i in range(len(b_eq))] if b_eq is not None else [])

    if not res.success or res.x is None:
        return {
            "model_type": "lp-optimize",
            "solver": "scipy-highs",
            "is_milp": is_milp,
            "success": False,
            "status": int(res.status),
            "message": str(res.message),
            "sense": sense,
            "optimal_value": None,
            "variables": {},
            "binding_constraints": [],
            "constraint_slacks": [],
            "verified_feasible": False,
        }

    x = np.asarray(res.x, dtype=float)
    opt_val = float(np.dot(c_raw, x))
    feasible = True
    slacks = []
    binding = []

    if A_ub is not None and b_ub is not None:
        ub_slack = b_ub - (A_ub @ x)
        if np.any(ub_slack < -1e-6):
            feasible = False
        for idx, sv in enumerate(ub_slack.tolist()):
            cname = ub_names[idx] if idx < len(ub_names) else f"ub_{idx}"
            is_bind = abs(sv) <= 1e-6
            slacks.append({"constraint": cname, "type": "ub", "slack": round(float(sv), 6), "binding": is_bind})
            if is_bind:
                binding.append(cname)

    if A_eq is not None and b_eq is not None:
        eq_err = (A_eq @ x) - b_eq
        if np.any(np.abs(eq_err) > 1e-6):
            feasible = False
        for idx, ev in enumerate(eq_err.tolist()):
            cname = eq_names[idx] if idx < len(eq_names) else f"eq_{idx}"
            slacks.append({"constraint": cname, "type": "eq", "residual": round(float(ev), 6), "binding": True})
            binding.append(cname)

    if np.any(x < lb - 1e-6) or np.any(x > ub + 1e-6):
        feasible = False

    return {
        "model_type": "lp-optimize",
        "solver": "scipy-highs",
        "is_milp": is_milp,
        "success": True,
        "status": int(res.status),
        "message": str(res.message),
        "sense": sense,
        "optimal_value": round(opt_val, 6),
        "variables": {var_names[i]: round(float(x[i]), 6) for i in range(n_vars)},
        "binding_constraints": binding,
        "constraint_slacks": slacks,
        "verified_feasible": feasible,
    }


def cmd_simulate(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    if not (slug_dir / "brief.json").exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    spec_path = Path(args.spec).expanduser().resolve()
    if not spec_path.exists():
        return fail(f"Spec file not found: {spec_path}")
    spec = read_json(spec_path)

    try:
        if args.type == "monte-carlo":
            result = _run_monte_carlo(spec)
        elif args.type == "pareto-mcda":
            result = _run_pareto_mcda(spec)
        elif args.type == "lp-optimize":
            result = _run_lp_optimize(spec)
        else:
            return fail(f"Unknown simulation type: {args.type}")
    except Exception as exc:
        return fail(f"Simulation '{args.name}' failed: {exc}")

    result["name"] = args.name
    result["generated_at"] = now_iso()
    out_path = slug_dir / "models" / f"{args.name}_result.json"
    write_json(out_path, result)
    return emit({"ok": True, "result_path": str(out_path), "result": result})


# ---------------------------------------------------------------------------
# Subcommand: update-critique
# ---------------------------------------------------------------------------

def cmd_update_critique(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    cg_path = slug_dir / "critique_gate.json"
    if not cg_path.exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    cg = read_json(cg_path)
    cg["reviewed_at"] = now_iso()
    for field in (
        "independent_context",
        "anti_sycophancy_passed",
        "anti_defeatism_passed",
        "triangulation_passed",
        "modeling_passed",
        "horizon_passed",
    ):
        val = getattr(args, field, None)
        if val is not None:
            cg[field] = bool(val)
    if args.findings_audited is not None:
        cg["findings_audited"] = int(args.findings_audited)
    if args.defects_json is not None:
        d = parse_json_arg(args.defects_json)
        if not isinstance(d, list):
            return fail("--defects-json must be a JSON list")
        cg["open_defects"] = d

    write_json(cg_path, cg)
    return emit({"ok": True, "critique_gate": cg})


# ---------------------------------------------------------------------------
# Subcommand: gate-check
# ---------------------------------------------------------------------------

def _check_loop_1(brief: dict[str, Any], horizon: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    mode = brief.get("mode", "standard")
    gaps: list[str] = []
    min_lenses = 3 if mode == "lite" else 5
    min_analogues = 1 if mode == "lite" else 2
    min_blind_spots = 1 if mode == "lite" else 3

    if not str(brief.get("reframed_decision", "")).strip():
        gaps.append("brief.reframed_decision is empty")
    hyps = brief.get("hypotheses") or []
    if len(hyps) < 2:
        gaps.append(f"Need >= 2 falsifiable hypotheses (found {len(hyps)})")
    uc = brief.get("user_constraints")
    if not (uc and (isinstance(uc, (dict, list)) and len(uc) > 0 or str(uc).strip())):
        gaps.append("brief.user_constraints is empty — record user budget/team/time/reality limits")

    covered = sum(1 for v in horizon.get("lenses", {}).values() if v.get("status") == "covered")
    if covered < min_lenses:
        gaps.append(f"Need >= {min_lenses} covered specialist lenses for mode={mode} (found {covered})")

    analogues = horizon.get("analogues") or []
    if len(analogues) < min_analogues:
        gaps.append(f"Need >= {min_analogues} cross-domain analogues (found {len(analogues)})")

    blind_spots = horizon.get("blind_spots") or []
    if len(blind_spots) < min_blind_spots:
        gaps.append(f"Need >= {min_blind_spots} blind-spot questions (found {len(blind_spots)})")

    return gaps, {
        "covered_lenses": covered,
        "hypotheses": len(hyps),
        "analogues": len(analogues),
        "blind_spots": len(blind_spots),
    }


def _check_loop_2(brief: dict[str, Any], sources: list[dict[str, Any]], claims: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    mode = brief.get("mode", "standard")
    gaps: list[str] = []
    min_sources = {"lite": 3, "standard": 6, "exhaustive": 12}.get(mode, 6)
    min_types = 2 if mode == "lite" else 3

    if len(sources) < min_sources:
        gaps.append(f"Need >= {min_sources} sources for mode={mode} (found {len(sources)})")

    distinct_types = {s.get("type") for s in sources if s.get("type")}
    if len(distinct_types) < min_types:
        gaps.append(f"Need >= {min_types} distinct source types (found {len(distinct_types)}: {sorted(distinct_types)})")

    src_map = {s["id"]: s for s in sources}
    bad_theses = []
    for c in claims:
        if c.get("core_thesis") and c.get("tier") in ("T1_PRIMARY", "T2_CORROBORATED"):
            sids = c.get("sources") or []
            stypes = {src_map[sid]["type"] for sid in sids if sid in src_map}
            if len(sids) < 3 or len(stypes) < 2:
                bad_theses.append(c["id"])
    if bad_theses:
        gaps.append(
            f"Core thesis claims {bad_theses} claim T1/T2 without >=3 sources across >=2 types; "
            "add corroboration or downgrade to T3_SINGLE_PRACTITIONER / T4_INFERENCE"
        )

    has_opposition = any(s.get("disconfirming") for s in sources) or any(str(c.get("contradicts", "")).strip() for c in claims)
    if not has_opposition:
        gaps.append("Need >= 1 disconfirming source (--disconfirming) or contradiction claim (--contradicts)")

    return gaps, {
        "sources": len(sources),
        "distinct_source_types": len(distinct_types),
        "claims": len(claims),
        "has_opposition": has_opposition,
    }


def _check_loop_3(brief: dict[str, Any], slug_dir: Path) -> tuple[list[str], dict[str, Any]]:
    mode = brief.get("mode", "standard")
    models_dir = slug_dir / "models"
    all_files = [p for p in models_dir.glob("*") if p.is_file()] if models_dir.exists() else []
    sim_results = [p for p in all_files if p.name.endswith("_result.json")]
    structural = [p for p in all_files if not p.name.endswith("_result.json") and p.suffix.lower() in (".md", ".json")]

    gaps: list[str] = []
    if len(structural) < 1:
        gaps.append("Need >= 1 structural framework file (.md or .json) in models/ (e.g. causal_loop.md, zwicky_box.json, toc_analysis.md)")
    if mode in ("standard", "exhaustive") and len(sim_results) < 1:
        gaps.append(f"Mode={mode} requires >= 1 quantitative simulation result (*_result.json) in models/ via dr_engine.py simulate")

    return gaps, {
        "structural_models": [p.name for p in structural],
        "simulation_results": [p.name for p in sim_results],
    }


def _check_loop_4(brief: dict[str, Any], obstacles_data: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    mode = brief.get("mode", "standard")
    min_obs = 1 if mode == "lite" else 2
    obs = obstacles_data.get("obstacles") or []
    gaps: list[str] = []

    if len(obs) < min_obs:
        gaps.append(f"Need >= {min_obs} calibrated obstacles in obstacles.json (found {len(obs)})")
    for o in obs:
        if len(str(o.get("honest_reality", "")).strip()) < 20:
            gaps.append(f"Obstacle '{o.get('id')}' fails anti-sycophancy check (honest_reality < 20 chars)")
        if not str(o.get("path_a_wedge", "")).strip() or not str(o.get("bypass_pattern", "")).strip():
            gaps.append(f"Obstacle '{o.get('id')}' fails anti-defeatism check (missing path_a_wedge or bypass_pattern)")

    return gaps, {"obstacles": len(obs)}


def _check_loop_5(slug_dir: Path, cg: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    gaps: list[str] = []
    required_flags = (
        "independent_context",
        "anti_sycophancy_passed",
        "anti_defeatism_passed",
        "triangulation_passed",
        "modeling_passed",
        "horizon_passed",
    )
    false_flags = [f for f in required_flags if not cg.get(f)]
    if false_flags:
        gaps.append(f"critique_gate.json has unverified flags: {false_flags}")
    defects = cg.get("open_defects") or []
    if defects:
        gaps.append(f"critique_gate.json still has open_defects: {defects}")

    for req_file in ("final_report.md", "refresh_targets.md"):
        p = slug_dir / req_file
        if not p.exists() or len(p.read_text(encoding="utf-8").strip()) == 0:
            gaps.append(f"Missing or empty deliverable: {req_file}")

    return gaps, {"critique_flags_ok": not false_flags, "open_defects": len(defects)}


def cmd_gate_check(args: argparse.Namespace) -> int:
    slug_dir = Path(args.dir).expanduser().resolve()
    brief_path = slug_dir / "brief.json"
    if not brief_path.exists():
        return fail(f"Not an initialized research directory: {slug_dir}")

    brief = read_json(brief_path)
    horizon = read_json(slug_dir / "horizon_map.json")
    sources = read_jsonl(slug_dir / "sources.jsonl")
    claims = read_jsonl(slug_dir / "claims.jsonl")
    obstacles = read_json(slug_dir / "obstacles.json")
    cg = read_json(slug_dir / "critique_gate.json")

    loop = args.loop
    all_gaps: list[str] = []
    metrics: dict[str, Any] = {}

    if loop == "1":
        g, m = _check_loop_1(brief, horizon)
        all_gaps.extend(g)
        metrics["loop_1"] = m
    elif loop == "2":
        g, m = _check_loop_2(brief, sources, claims)
        all_gaps.extend(g)
        metrics["loop_2"] = m
    elif loop == "3":
        g, m = _check_loop_3(brief, slug_dir)
        all_gaps.extend(g)
        metrics["loop_3"] = m
    elif loop == "4":
        g, m = _check_loop_4(brief, obstacles)
        all_gaps.extend(g)
        metrics["loop_4"] = m
    elif loop in ("5", "final"):
        for idx, fn in (
            ("loop_1", lambda: _check_loop_1(brief, horizon)),
            ("loop_2", lambda: _check_loop_2(brief, sources, claims)),
            ("loop_3", lambda: _check_loop_3(brief, slug_dir)),
            ("loop_4", lambda: _check_loop_4(brief, obstacles)),
            ("loop_5", lambda: _check_loop_5(slug_dir, cg)),
        ):
            g, m = fn()
            all_gaps.extend(g)
            metrics[idx] = m
    else:
        return fail(f"Invalid --loop '{loop}'. Valid: 1, 2, 3, 4, 5, final")

    passed = len(all_gaps) == 0
    return emit(
        {
            "passed": passed,
            "status": "PASS" if passed else "LOOP_BACK_REQUIRED",
            "loop": loop,
            "mode": brief.get("mode", "standard"),
            "metrics": metrics,
            "blocking_gaps": all_gaps,
        },
        code=0 if passed else 2,
    )


# ---------------------------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dr_engine.py",
        description="Deterministic loop controller, evidence ledger, and quantitative OR/modeling engine for deep-research.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # init
    s = sub.add_parser("init", help="Initialize a deep-research workspace folder")
    s.add_argument("--root", required=True, help="Parent directory for research projects")
    s.add_argument("--slug", required=True, help="Short project slug folder name")
    s.add_argument("--question", required=True, help="Original user question")
    s.add_argument("--decision", default="", help="Reframed concrete decision")
    s.add_argument("--mode", choices=["lite", "standard", "exhaustive"], default="standard")
    s.add_argument("--constraints", default="", help="User constraints (text, JSON, or @file)")
    s.set_defaults(func=cmd_init)

    # update-horizon
    s = sub.add_parser("update-horizon", help="Update 360 horizon lenses, analogues, blind spots, and hypotheses")
    s.add_argument("--dir", required=True, help="Initialized slug directory")
    s.add_argument("--lens", help=f"One of: {', '.join(SPECIALIST_LENSES)}")
    s.add_argument("--status", choices=["covered", "not_applicable"])
    s.add_argument("--summary", help="Summary of findings for this lens")
    s.add_argument("--key-questions-json", help="JSON list of diagnostic questions for the lens")
    s.add_argument("--analogues-json", help="JSON list (or @file) of cross-domain structural analogues")
    s.add_argument("--blind-spots-json", help="JSON list (or @file) of unknown-unknown blind spots")
    s.add_argument("--hypotheses-json", help="JSON list (or @file) of falsifiable hypotheses")
    s.add_argument("--stop-criteria-json", help="JSON list (or @file) of stop criteria")
    s.add_argument("--decision", help="Updated reframed_decision")
    s.add_argument("--constraints", help="Updated user_constraints (text, JSON, or @file)")
    s.set_defaults(func=cmd_update_horizon)

    # add-source
    s = sub.add_parser("add-source", help="Add a grounded source with verbatim quote to sources.jsonl and sources/<id>.md")
    s.add_argument("--dir", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--url", required=True)
    s.add_argument("--type", required=True, choices=sorted(SOURCE_TYPES))
    s.add_argument("--credibility", required=True, type=int)
    s.add_argument("--recency", required=True, help="YYYY-MM")
    s.add_argument("--quote", default="")
    s.add_argument("--body-file", help="Optional path to extracted markdown/notes")
    s.add_argument("--unreachable", action="store_true", help="Mark source unreachable when no quote could be fetched")
    s.add_argument("--disconfirming", action="store_true", help="Mark as opposition / counter-evidence source")
    s.set_defaults(func=cmd_add_source)

    # add-claim
    s = sub.add_parser("add-claim", help="Add an evidence-linked claim to claims.jsonl with triangulation check")
    s.add_argument("--dir", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--statement", required=True)
    s.add_argument("--tier", required=True, choices=sorted(CLAIM_TIERS))
    s.add_argument("--sources", required=True, help="Comma-separated source IDs (e.g. S01,S02,S03)")
    s.add_argument("--core-thesis", action="store_true")
    s.add_argument("--confidence", type=float, default=0.7)
    s.add_argument("--contradicts", default="", help="Optional claim ID this contradicts")
    s.set_defaults(func=cmd_add_claim)

    # add-obstacle
    s = sub.add_parser("add-obstacle", help="Record an honest obstacle + asymmetric bypass + 3-path ladder")
    s.add_argument("--dir", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--barrier-type", required=True, choices=sorted(BARRIER_TYPES))
    s.add_argument("--honest-reality", required=True)
    s.add_argument("--bypass-pattern", required=True, choices=sorted(BYPASS_PATTERNS))
    s.add_argument("--path-a-wedge", required=True)
    s.add_argument("--path-b-core", default="")
    s.add_argument("--path-c-moat", default="")
    s.set_defaults(func=cmd_add_obstacle)

    # simulate
    s = sub.add_parser("simulate", help="Run Monte Carlo, Pareto-MCDA, or LP/MILP optimization model")
    s.add_argument("--dir", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--type", required=True, choices=["monte-carlo", "pareto-mcda", "lp-optimize"])
    s.add_argument("--spec", required=True, help="Path to JSON model specification")
    s.set_defaults(func=cmd_simulate)

    # update-critique
    s = sub.add_parser("update-critique", help="Update critique_gate.json after independent adversarial review")
    s.add_argument("--dir", required=True)
    s.add_argument("--independent-context", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--anti-sycophancy-passed", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--anti-defeatism-passed", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--triangulation-passed", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--modeling-passed", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--horizon-passed", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--findings-audited", type=int)
    s.add_argument("--defects-json", help="JSON list (or @file) of open defects")
    s.set_defaults(func=cmd_update_critique)

    # gate-check
    s = sub.add_parser("gate-check", help="Verify loop completion requirements (0=PASS, 2=LOOP_BACK_REQUIRED)")
    s.add_argument("--dir", required=True)
    s.add_argument("--loop", required=True, choices=["1", "2", "3", "4", "5", "final"])
    s.set_defaults(func=cmd_gate_check)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
