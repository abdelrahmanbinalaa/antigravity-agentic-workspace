# Live Antigravity Models & Capability Routing

> Auto-synced: `2026-11-26T05:09:54+02:00` | Source: `agy models` + `models.md` (`docs_fetched=True`)
> Refresh command: `python "~/.skills-manager/sync_models.py"`

## 1. Two-Layer Addressing Rule

- **In-Session Tools (`invoke_subagent` / `run_workflow`):** Use abstract tiers (`"inherit"`, `"flash_lite"`, `"flash"`, `"pro"`).
- **`agy` CLI / `/swarm` (`models` & `model`) / `agy-delegate`:** Use exact `agy models` IDs below.

## 2. Active Role-Slot Recommendations

- **Heavy Planner / Deep OR / Synthesis:** `gemini-4-carbon-high, claude-opus-5-5-high, gemini-4-neon-high`
- **Long-Context Workhorse (up to 512K):** `gemini-4-neon-high`
- **Fast Parallel Executors / Sweeps:** `gemini-4-hydrogen-high, gemini-4-hydrogen-low, claude-sonnet-5-5-high, claude-sonnet-5-5-low`
- **Cross-Family Adversarial Critic (Loop 5 / Red-Team):** `gemini-4-carbon-high` ↔ `claude-opus-5-5-high`
- **Avoid Pinning (Leaving Soon):** `gemini-4-argon` (November 30, 2026), `gemini-3.8-flash` (November 30, 2026), `gpt-oss-120b` (November 30, 2026)

## 3. Live Family Matrix

| Family | Provider | Efforts | Context | Role | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `claude-opus-5-5` | `anthropic-claude` | `low,medium,high` | — | Planner | Active |
| `claude-sonnet-5-5` | `anthropic-claude` | `low,medium,high` | — | Executor | Active |
| `gemini-3.8-flash` | `google-gemini` | `high,medium,low` | — | General | Leaving November 30, 2026 |
| `gemini-4-argon` | `google-gemini` | `medium,high,low` | — | Planner | Leaving November 30, 2026 |
| `gemini-4-carbon` | `google-gemini` | `medium,high,low` | — | Planner | Active |
| `gemini-4-hydrogen` | `google-gemini` | `high,xhigh,medium,low` | — | Executor | Active |
| `gemini-4-neon` | `google-gemini` | `high,xhigh,medium,low` | 512K tokens | Planner | Active |
| `gpt-oss-120b` | `other` | `medium` | — | General | Leaving November 30, 2026 |
