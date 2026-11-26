"""
Antigravity run_workflow template for Wide, Multi-Loop Deep Research.

Invoke via Antigravity's `run_workflow` tool with Args:
  {
    "slug_dir": "<abs_path_to_initialized_slug_dir>",
    "question": "<user_question>",
    "reframed_decision": "<concrete_decision>",
    "user_constraints": "<constraints_summary>",
    "lenses": [
      "first_principles_science",
      "technical_architecture",
      "market_unit_economics",
      "operations_supply_chain",
      "behavioral_incentives",
      "competitive_game_theory",
      "legal_regulatory_tail_risk",
      "cross_domain_analogues"
    ]
  }
"""

import json
from pathlib import Path

slug_dir = args["slug_dir"]
question = args["question"]
decision = args.get("reframed_decision", question)
constraints = args.get("user_constraints", "Infer realistic resource bounds from brief.json")
lenses = args.get("lenses", [
    "first_principles_science",
    "technical_architecture",
    "market_unit_economics",
    "operations_supply_chain",
    "behavioral_incentives",
    "competitive_game_theory",
    "legal_regulatory_tail_risk",
    "cross_domain_analogues",
])

lens_schema = {
    "type": "object",
    "properties": {
        "lens": {"type": "string"},
        "findings_summary": {"type": "string"},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "type": {"type": "string"},
                    "credibility": {"type": "integer"},
                    "recency": {"type": "string"},
                    "quote": {"type": "string"},
                    "disconfirming": {"type": "boolean"},
                },
                "required": ["id", "title", "url", "type", "credibility", "recency", "quote"],
            },
        },
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "statement": {"type": "string"},
                    "tier": {"type": "string"},
                    "source_ids": {"type": "array", "items": {"type": "string"}},
                    "core_thesis": {"type": "boolean"},
                },
                "required": ["statement", "tier", "source_ids"],
            },
        },
        "blind_spots": {"type": "array", "items": {"type": "string"}},
        "analogues": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["lens", "findings_summary", "sources", "claims", "blind_spots"],
}

phase("Loop 1-2: Parallel Multi-Lens Evidence Sweep")
log(f"Starting 360 sweep across {len(lenses)} lenses for {slug_dir}")

async def inspect_lens(lens_name: str):
    prompt = (
        f"You are investigating the '{lens_name}' specialist lens for:\n"
        f"Question: {question}\n"
        f"Decision: {decision}\n"
        f"User Constraints: {constraints}\n\n"
        "Search live sources (search_web, agent-reach, scrapling, or primary docs). "
        "Collect verified sources with verbatim quotes (never fabricate URLs or quotes), "
        "surface unknown-unknown blind spots, and include disconfirming/failure evidence. "
        "Return strict JSON matching the schema via your finish tool."
    )
    return await agent(prompt=prompt, schema=lens_schema, role=f"Lens: {lens_name}", model="flash")

opposition_schema = {
    "type": "object",
    "properties": {
        "disconfirming_sources": lens_schema["properties"]["sources"],
        "failure_modes": {"type": "array", "items": {"type": "string"}},
        "hidden_cost_floors": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["disconfirming_sources", "failure_modes", "hidden_cost_floors"],
}

opposition_task = agent(
    prompt=(
        f"You are the Opposition & Pre-Mortem Hunter for:\n{question}\nDecision: {decision}\n"
        "Actively search for failure post-mortems, regulatory blockers, unit-economic traps, "
        "and reasons why standard advice fails. Return verified disconfirming sources with quotes."
    ),
    schema=opposition_schema,
    role="Opposition & Failure Hunter",
    model="flash",
)

lens_results = await parallel(lenses, inspect_lens)
opposition_result = await opposition_task
log(f"Collected {sum(len(r.get('sources', [])) for r in lens_results)} lens sources + opposition pass.")

phase("Loop 3-4: Formal Modeling & Calibrated Solution Engineering")
synth_schema = {
    "type": "object",
    "properties": {
        "frameworks_built": {"type": "array", "items": {"type": "string"}},
        "simulations_run": {"type": "array", "items": {"type": "string"}},
        "obstacles_engineered": {"type": "integer"},
        "draft_report_path": {"type": "string"},
    },
    "required": ["frameworks_built", "simulations_run", "obstacles_engineered", "draft_report_path"],
}

sweep_bundle = {"lenses": lens_results, "opposition": opposition_result}
Path(slug_dir, "models").mkdir(parents=True, exist_ok=True)
Path(slug_dir, "models", "_workflow_sweep_bundle.json").write_text(
    json.dumps(sweep_bundle, indent=2, ensure_ascii=False), encoding="utf-8"
)

synth_result = await agent(
    prompt=(
        f"Working inside {slug_dir}:\n"
        "1. Read models/_workflow_sweep_bundle.json and ingest sources/claims/horizon updates via dr_engine.py.\n"
        "2. Run `dr_engine.py gate-check --loop 1` and `--loop 2`; close any gaps.\n"
        "3. Build structural modeling files in models/ (Systems/TOC/Zwicky/TRIZ) AND run quantitative "
        "modeling via `dr_engine.py simulate` (monte-carlo / pareto-mcda / lp-optimize).\n"
        "4. Engineer every obstacle via `dr_engine.py add-obstacle` with blunt honest_reality + bypass_pattern + Path A/B/C.\n"
        "5. Draft final_report.md and refresh_targets.md and verify `gate-check --loop 3` and `--loop 4`."
    ),
    schema=synth_schema,
    role="Modeling & Solution Architect",
    model="inherit",
)
log("Modeling & obstacle engineering complete:", synth_result)

phase("Loop 5: Independent Adversarial & Calibration Gate")
critic_schema = {
    "type": "object",
    "properties": {
        "passed": {"type": "boolean"},
        "sycophancy_defects": {"type": "array", "items": {"type": "string"}},
        "defeatism_defects": {"type": "array", "items": {"type": "string"}},
        "evidence_gaps": {"type": "array", "items": {"type": "string"}},
        "modeling_defects": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["passed", "sycophancy_defects", "defeatism_defects", "evidence_gaps", "modeling_defects"],
}

critic_agent = agent(
    prompt=(
        f"You are an independent Calibration & Adversarial Auditor inspecting {slug_dir}. "
        "Audit brief.json, horizon_map.json, sources.jsonl, claims.jsonl, models/*, obstacles.json, and final_report.md. "
        "Flag: (1) sycophancy/wishful math/unverified claims, (2) defeatism/dead-end problems without viable Path A wedges, "
        "(3) missing specialist lenses or single-source core theses, (4) modeling/math discrepancies."
    ),
    role="Calibration & Adversarial Auditor",
    model="inherit",
)

critic_result = await critic_agent("Run full audit round 1.", critic_schema)
for round_idx in range(2):
    if critic_result["passed"]:
        break
    log(f"Critic rejected round {round_idx + 1}; running repair loop:", critic_result)
    await agent(
        prompt=(
            f"Fix all defects reported by the independent critic in {slug_dir}:\n"
            f"{json.dumps(critic_result, indent=2, ensure_ascii=False)}\n"
            "Re-run dr_engine.py gate-check --loop 1..4 and update final_report.md."
        ),
        schema={"type": "string"},
        role=f"Defect Repair Round {round_idx + 1}",
        model="inherit",
    )
    critic_result = await critic_agent(f"Re-audit after repair round {round_idx + 1}.", critic_schema)

del critic_agent
log("Final critic gate status:", critic_result)
print(json.dumps({"synth": synth_result, "critic": critic_result}, indent=2, ensure_ascii=False))
