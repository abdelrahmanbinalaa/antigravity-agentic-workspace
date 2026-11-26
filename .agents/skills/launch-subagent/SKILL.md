---
name: launch-subagent
description: 'Delegate a bounded sub-task to a subagent with proper isolation, runtime-accurate model tiers, and structured return contracts. Use for 1-2 independent subtasks, parallel read-only exploration, or isolated verification (triggers: launch subagent, spawn subagent, delegate subtask, parallel exploration, تفويض مهمة، إطلاق وكيل فرعي). Differentiator: use launch-subagent for 1-2 bounded subtasks; escalate to agent-swarm for 3+ coordinated workers, specialist councils, maker-checker DAGs, or adversarial red/blue swarms.'
---

# Launching Subagents Across Agent Runtimes

Use subagents to protect main context, parallelize independent reads, or isolate risky edits. Never invent non-existent model names or deprecated research tools.

## 1. Runtime-Accurate Model & Tool Selection

| Runtime | Primitive | Fast Sweep / Extraction / Browser | Synthesis / Coding / Verification | Hardest Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Antigravity** | `invoke_subagent` / `run_workflow` | `Model="flash"` or `"flash_lite"` (`browser` defaults to `"flash"`) | `Model="inherit"` (default) | `Model="pro"` (or `"inherit"`) |
| **Claude Code / Cowork** | `Task` tool | `haiku` | `sonnet` | `opus` |
| **OpenCode / Pi / Hermes / Qoder** | Native subagent / CLI | Active session default (unless user specifies) | Active session default | Active session default |

- **Antigravity `TypeName`s:** `"research"` (read-only), `"browser"` (live UI), `"self"` (full tools). Use `Workspace="share"` or `"branch"` whenever parallel `"self"` subagents edit files.
- **Live Antigravity Model Catalog:** Check [live-models.md](references/live-models.md) for current CLI/UI/`/swarm` model IDs (`Gemini 4 Neon`/`Carbon`/`Hydrogen`, `Claude Opus/Sonnet 5.5`), context limits, and active deprecation alerts (refresh via `python ~/.skills-manager/sync_models.py`).
- **When web/research tools are needed:** Instruct the subagent to use `agent-reach`, `scrapling-official`, `firecrawl`, or `deep-research`.

## 2. Core Isolation & Brief Rules

1. **Zero-Context Briefs:** Subagents start blind and do not inherit conversation history or loaded skill bodies. State the exact goal, file paths, constraints, tools/skills to load, and output schema in the prompt.
2. **Disjoint Ownership:** Two concurrent subagents must never edit the same file unless each runs in an isolated workspace/worktree.
3. **Compact Returns:** Have subagents write bulky logs, diffs, or source dumps to files and return only a concise summary + file paths + pass/fail status.
4. **Orchestrator Owns Verification:** Never trust a subagent's self-report blindly — inspect modified files and re-run test/lint gates yourself (or dispatch an independent verifier).
5. **Escalate at 3+ Agents:** If the work needs dependency waves, specialist debate, competing hypotheses, or maker-checker verification across 3+ workers, invoke **`agent-swarm`** instead.
