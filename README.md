# Antigravity Agentic Workspace

Portable multi-agent skills, deterministic research & swarm engines, quantitative operational research solvers, and tooling bootstraps designed for **Google Antigravity** (Local & Remote), **Claude Code / Cowork**, **OpenCode**, **Pi**, and **Hermes**.

## Highlights

- **Wide, Multi-Loop Deep Research (`.agents/skills/deep-research/`)**: 360° 8-lens horizon expansion, cross-domain structural analogues, `T1–T4` triangulated ledgers, opposition hunting, calibrated anti-sycophancy / anti-defeatism obstacle bypass ladders (`Path A -> B -> C`), and quantitative simulation (`Monte Carlo`, `Pareto-MCDA / TOPSIS`, `LP/MILP` via `SciPy HiGHS`).
- **Multi-Topology Agent Swarm (`.agents/skills/agent-swarm/`)**: `map-reduce`, `specialist-council`, `competing-hypotheses`, `maker-checker-dag`, and `red-blue-calibration` with DAG cycle checks, concurrent file-collision locks, orthogonal cognitive stances, and `maker != checker` gates.
- **Market, Competitor & Product Research Suite**: Includes `market-research-reports` (MIT, K-Dense), `competitor-profiling`, `customer-research`, `pricing`, `marketing-council` (MIT, Corey Haines), `data-analysis`, `data-quality-auditor`, `pitch-deck`, `copywriting`, and `ux-writing-arabic`.
- **Web & Social Extraction**: `agent-reach`, `scrapling-official`, `firecrawl`, `firecrawl-lead-research`, `agent-browser`, `browser-harness`.
- **Engineering, Workflows & Security Audits**: `launch-subagent`, `brainstorming`, `writing-plans`, `systematic-debugging`, `verification-before-completion`, `n8n-*`, `mantis-*`, `bigquery-*`, `gcp-*`, `tdd-*`, `git-worktree`.

## Quick Start (Antigravity Remote / Linux Container)

Attach this repository under **Remote > GitHub Repositories** in Antigravity. Everything bootstraps automatically:
- `.agents/hooks.json` runs `auto_session_init.py` on `SessionStart` to ensure output directories and Python packages are ready.
- `dr_engine.py simulate` also auto-installs `numpy`/`scipy` on demand if missing.
- Optional manual fallback: `bash scripts/bootstrap_remote_tools.sh`.

## Quick Start (Local Machine)

On Windows, `auto_sync_all.py` (scheduled monthly via Windows Task Scheduler `AntigravityAutoSync` and ready in Antigravity Automations) automatically updates live Antigravity model specs, syncs all 10 local agents via `skillsctl`, mirrors all skills into `.agents/skills/`, runs a secret-hygiene check, and commits/pushes updates to GitHub `main`.

## MCP Configuration

See [`configs/mcp_config.template.json`](configs/mcp_config.template.json) for a sanitized, zero-secret MCP configuration template (`playwright`, `searxncrawl`, `kaggle`, `huggingface`, plus optional free-tier `brightdata`, `firecrawl`, and `apify` placeholders). Official Marketplace plugins such as **Google Drive**, **Chrome DevTools**, **YouTube MCP**, and **Semrush** can be connected directly inside Antigravity's **Customizations > Marketplace / Apps** tab.
