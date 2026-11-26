# Agentic Workspace Operating Guide

This workspace bundles a complete, cross-agent suite of **skills**, **deterministic research & swarm engines**, **quantitative solvers**, and **agentic CLI/MCP tooling** under `.agents/skills/`.

## Core Orchestration & Research Engines

1. **Wide Multi-Loop Deep Research (`.agents/skills/deep-research/`)**
   - Use for high-stakes market, product, competitor, technical, and operational research.
   - Enforces 5 closed verification loops via `python .agents/skills/deep-research/scripts/dr_engine.py` (`init`, `update-horizon`, `add-source`, `add-claim`, `add-obstacle`, `simulate`, `update-critique`, `gate-check`).
   - Quantitative simulation & optimization (`simulate`): `monte-carlo` (P10/P50/P90 + Spearman tornado sensitivity), `pareto-mcda` (TOPSIS + 500-trial weight stability), and `lp-optimize` (SciPy HiGHS LP/MILP with Solver Certificates).
   - Output directory: write investigation artifacts under `research_runs/<slug>/`.

2. **Multi-Topology Agent Swarm (`.agents/skills/agent-swarm/`)**
   - Use for 3+ coordinated specialists (`map-reduce`, `specialist-council`, `competing-hypotheses`, `maker-checker-dag`, `red-blue-calibration`).
   - Enforces DAG cycle checks, concurrent file-collision locks, orthogonal cognitive stances, maker != checker verification, and calibrated conflict resolution via `python .agents/skills/agent-swarm/scripts/swarm_coordinator.py`.
   - Output directory: write swarm blackboards under `swarm_runs/<slug>/`.

3. **Specialized Market, Product & Competitor Skills**
   - `market-research-reports`: TAM/SAM/SOM scenario sizing, unit consistency, and evidence-traceable consulting reports.
   - `competitor-profiling`: Dated competitive intelligence separating Observed vs Inferred vs Implication.
   - `customer-research`, `pricing`, `marketing-council`, `data-analysis`, `data-quality-auditor`, `pitch-deck`, `copywriting`, `ux-writing-arabic`.

4. **Web Extraction & Agentic Tools**
   - Use `agent-reach`, `scrapling-official`, `firecrawl` (if API key configured), and native search/browser tools.
   - **In a fresh Remote / Linux container:** run `bash scripts/bootstrap_remote_tools.sh` before executing `dr_engine.py simulate` or `scrapling`/`agent-reach` if packages are not preinstalled.

## Non-Negotiable Quality Charter

- **Calibrated Realism:** Zero sycophancy (never hide weak unit economics, missing evidence, or regulatory gates) AND zero defeatism (never dump obstacles without engineering a viable low-friction `Path A` wedge tailored to user constraints).
- **Zero Fabrication:** Never invent URLs, quotes, or statistics; downgrade uncorroborated theses explicitly.
- **No Prose Math:** Run Python/SciPy models instead of mental arithmetic for budgets, forecasts, or allocations.
