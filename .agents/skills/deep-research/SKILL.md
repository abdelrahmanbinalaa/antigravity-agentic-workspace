---
name: deep-research
description: 'Wide 360-degree, multi-loop deep research, scientific/operational modeling, and obstacle-busting solution design engine. Use for high-stakes market, product, competitor, technical, or operational research, idea/process modeling, feasibility stress-testing, and designing realistic workarounds adapted to user constraints (triggers: deep research, wide research, comprehensive analysis, operational research, model this process, feasibility, obstacle bypass, بحث عميق، بحث موسع، دراسة سوق، بحوث تشغيلية، نمذجة الأفكار، تجاوز العقبات). Differentiator: enforces closed verification loops via scripts/dr_engine.py, cross-domain lenses, quantitative simulation/optimization, and calibrated realism (zero sycophancy, zero defeatism) rather than one-shot summaries, quick lookups, or source-code auditing.'
---

# Deep Research — Wide, Multi-Loop Modeling & Solution Engine

Turn high-stakes questions into a **360° horizon-expanded, closed-loop, quantitatively modeled, and execution-ready investigation**.

## 1. Operating Stance (Non-Negotiable)

- **Calibrated Realism:** Zero sycophancy (never sugarcoat weak unit economics, missing demand, or hard laws) AND zero defeatism (never dump dead-end problems without engineering an asymmetric, constraint-fitting workaround).
- **Wide Horizon:** Never stay trapped inside one narrow discipline or industry. Always sweep across technical, economic, operational, behavioral, competitive, legal, and cross-industry lenses.
- **No Prose Math:** Use `scripts/dr_engine.py simulate` (or explicit Python scripts) for unit economics, uncertainty ranges, multi-criteria trade-offs, and resource optimization.
- **Zero Fabrication:** Never invent URLs, quotes, or statistics. Unreachable or single-source claims are labeled honestly as uncorroborated or inference.

## 2. Depth Scaling & Agent Orchestration

| Mode | When to Use | Loop Rigor Bar |
| :--- | :--- | :--- |
| `lite` | Bounded decision, quick stress-test | ≥3 lenses, ≥3 sources (≥2 types), ≥1 framework, ≥1 calibrated obstacle |
| `standard` | Default for market, product, strategy, operations | ≥5 lenses, ≥6 sources (≥3 types), ≥1 structural + ≥1 `simulate` model, ≥2 obstacles |
| `exhaustive` | High-capital bets, tenders, deep OR, full landscapes | ≥5 lenses (sweep all 8), ≥12 sources (≥3 types), multi-model `simulate`, fresh critic loop |

**Orchestration Auto-Detection:**
- **In Antigravity:** Prefer `run_workflow` using [agy_workflow_template.py](scripts/agy_workflow_template.py) (or parallel `invoke_subagent` calls; or `/swarm` only if the user explicitly invoked `/swarm`).
- **In Claude / Cowork / OpenCode / Hermes:** Fan out parallel subagents for Loop 2 waves and run an isolated fresh-context review pass for Loop 5.
- **Live Antigravity Model Specs:** Read [live-models.md](references/live-models.md) for current `Gemini 4` (`Neon`/`Carbon`/`Hydrogen`) and `Claude 5.5` (`Opus`/`Sonnet`) role-slot routing, cross-family critique pairing, and active deprecation alerts; refresh anytime via `python ~/.skills-manager/sync_models.py`.

## 3. Setup & State Initialization

Set `SKILL_DIR` to this skill's directory and scaffold `{SLUG_DIR}` (`<research_root>/<slug>/`):

```bash
python "{SKILL_DIR}/scripts/dr_engine.py" init \
  --root "{RESEARCH_ROOT}" --slug "{SLUG}" \
  --question "{ORIGINAL_QUESTION}" \
  --decision "{REFRAMED_DECISION}" \
  --mode standard \
  --constraints "{USER_CONSTRAINTS}"
```

Every loop ends with `dr_engine.py gate-check`. **Exit code `2` (`LOOP_BACK_REQUIRED`) means you must loop back and close `blocking_gaps` before advancing.**

## 4. The 5 Closed Loops

### Loop 1: Reframing, User Context & 360° Horizon Expansion
Read [horizon-lenses.md](references/horizon-lenses.md) before starting.
1. Reframe the ask into a concrete decision (`reframed_decision`) and capture realistic `user_constraints` (budget, team size, timeline, access/assets — infer sensible bounds or ask at most 2 sharp questions if critically ambiguous).
2. Formulate `>= 2` falsifiable hypotheses.
3. Sweep the **8 Specialist Lenses**, abstract the core mechanism into **cross-domain structural analogues**, and log **unknown-unknown blind spots** via `dr_engine.py update-horizon`.
4. **Gate:**
   ```bash
   python "{SKILL_DIR}/scripts/dr_engine.py" gate-check --dir "{SLUG_DIR}" --loop 1
   ```

### Loop 2: Multi-Wave Evidence, Triangulation & Opposition Hunting
Read [sourcing-and-ledgers.md](references/sourcing-and-ledgers.md) for the live tool waterfall (`search_web`, `agent-reach`, `scrapling`, `firecrawl`, `browser`, `playwright`, Kaggle/BigQuery MCPs).
1. **Wave 1 (Parallel Fan-Out):** Search primary docs, academic/technical benchmarks, live pricing/market data, and practitioner feedback across covered lenses.
2. **Wave 2 (Opposition & Pre-Mortem):** Actively hunt disconfirming evidence, failure post-mortems, hidden cost floors, and regulatory blockers (`--disconfirming` or `--contradicts`).
3. Log every source with a verbatim quote (`add-source`) and map claims with `T1–T4` tiers (`add-claim`).
4. **Gate (Loop until `PASS`):**
   ```bash
   python "{SKILL_DIR}/scripts/dr_engine.py" gate-check --dir "{SLUG_DIR}" --loop 2
   ```

### Loop 3: Scientific, Systems & Quantitative Operational Modeling
Read [modeling-frameworks.md](references/modeling-frameworks.md) to pick the right frameworks.
1. Build `>= 1` structural model in `{SLUG_DIR}/models/` (`Systems Causal Loop`, `Theory of Constraints + Little's Law`, `Zwicky Morphological Box`, `TRIZ Separation`, `Wardley Map`, or `FMEA`).
2. In `standard` / `exhaustive` mode (and whenever numbers/allocations matter in `lite`), write a JSON spec and run `dr_engine.py simulate`:
   - `monte-carlo`: `P10 / P50 / P90` + Spearman tornado sensitivity.
   - `pareto-mcda`: constraint filtering + exact Pareto frontier + TOPSIS + weight stability.
   - `lp-optimize`: deterministic `scipy` HiGHS LP/MILP with verified Solver Certificate.
3. **Gate:**
   ```bash
   python "{SKILL_DIR}/scripts/dr_engine.py" gate-check --dir "{SLUG_DIR}" --loop 3
   ```

### Loop 4: Innovation & Constraint-Adaptive Obstacle Engineering
Read [obstacle-engineering.md](references/obstacle-engineering.md) to apply the **Calibrated Realism Charter**.
1. Separate **hard laws** (physics/statutory/math) from **soft conventions** (bloated incumbent habits).
2. For every real obstacle, engineer an asymmetric workaround (`wedge`, `piggyback`, `scope_slice`, `inversion`, `automation`, `partnership`, `triz_separation`, `legal_pivot`) and record it with `dr_engine.py add-obstacle`:
   - `--honest-reality`: blunt diagnosis & failure trigger (blocks sycophancy).
   - `--path-a-wedge`: easiest immediate low-friction entry fitting the user's real constraints (blocks defeatism).
   - `--path-b-core`: scalable repeatable operational system.
   - `--path-c-moat`: long-term defensible advantage.
3. **Gate:**
   ```bash
   python "{SKILL_DIR}/scripts/dr_engine.py" gate-check --dir "{SLUG_DIR}" --loop 4
   ```

### Loop 5: Independent Adversarial Critique & Final Gate
1. Spawn a **fresh-context critic** (new subagent / `run_workflow` auditor / separate review pass) to audit `brief.json`, `horizon_map.json`, `sources.jsonl`, `claims.jsonl`, `models/*`, `obstacles.json`, and draft `final_report.md` against:
   - Sycophancy or ungrounded optimism
   - Paralyzing defeatism or missing Path A wedges
   - Uncovered lenses or untriangulated core theses
   - Math, solver, or citation discrepancies
2. Loop back to Loops 2–4 to fix any defects, then update `critique_gate.json` via `dr_engine.py update-critique`.
3. Write `{SLUG_DIR}/final_report.md` and `{SLUG_DIR}/refresh_targets.md`, then verify:
   ```bash
   python "{SKILL_DIR}/scripts/dr_engine.py" gate-check --dir "{SLUG_DIR}" --loop final
   ```

## 5. Final Deliverable Structure (`final_report.md`)

1. **Calibrated Executive Verdict:** Clear Go / Conditional-Go / Pivot recommendation + confidence + the single biggest leverage point and single biggest kill-risk.
2. **360° Multi-Lens Insights & Cross-Industry Analogues:** Key findings across lenses + transferable mechanisms + resolved blind spots.
3. **Scientific & Quantitative Model Results:** Causal/TOC/Zwicky/TRIZ architecture + `P10/P50/P90`, tornado drivers, Pareto winner stability, or LP Solver Certificate.
4. **Honest Obstacles → Asymmetric Bypass Matrix:** Every barrier paired with its blunt reality, bypass pattern, and **3-Horizon Execution Ladder (`Path A` easiest wedge → `Path B` core ops → `Path C` moat)** tailored to user constraints.
5. **Evidence, Contradictions & Refresh Ledger:** Hypothesis outcomes (confirmed / refuted / undetermined), `T1–T4` claims table, unresolved uncertainty, and delta-refresh triggers.
