# Briefing Contracts, Isolation & 3-Runtime Dispatch

## Table of Contents
- [1. Zero-Context Worker Briefs & Blackboard Discipline](#1-zero-context-worker-briefs--blackboard-discipline)
- [2. File Ownership & Worktree Isolation](#2-file-ownership--worktree-isolation)
- [3. Dispatching Across Your 3 Runtimes](#3-dispatching-across-your-3-runtimes)
- [4. Calibrated Conflict Resolution](#4-calibrated-conflict-resolution)

---

## 1. Zero-Context Worker Briefs & Blackboard Discipline

Workers start blind — they do **not** see the coordinator's prior chat history or loaded skills. `swarm_coordinator.py add-task` writes a self-contained brief at `<swarm_dir>/briefs/<task_id>.md`.

**Anti-Context-Bloat Rule:**
- Workers write full logs, code notes, evidence tables, or source extracts to `<swarm_dir>/artifacts/<task_id>.md`.
- Workers pass only a **concise summary (`<= 1200` chars)** plus key decisions/risks to `swarm_coordinator.py submit-result`.
- Downstream workers and verifiers read `artifacts/<upstream_id>.md` directly instead of the coordinator copy-pasting long messages.

---

## 2. File Ownership & Worktree Isolation

| Scenario | `--isolation` Flag | Behavior |
| :--- | :--- | :--- |
| Research, audits, reviews | `read_only` | Zero edits; safe unlimited concurrency |
| Parallel code edits on non-overlapping files | `disjoint_paths` | `swarm_coordinator.py` enforces non-overlapping `--owned-paths` across concurrent tasks |
| Parallel edits that may touch shared files/configs | `worktree_share` | Antigravity `Workspace="share"` (or git worktree); author commits to branch, coordinator merges after verification |
| Competing implementations of the same module | `worktree_branch` | Fully isolated clone (`Workspace="branch"`); winner merged, losers discarded |

---

## 3. Dispatching Across Your 3 Runtimes

### A. Antigravity — Default (`run_workflow` / `invoke_subagent`)
1. Initialize the blackboard and tasks with `swarm_coordinator.py`, and pass `gate-check --stage plan`.
2. Execute waves cleanly using Antigravity's `run_workflow` with [agy_swarm_runner.py](../scripts/agy_swarm_runner.py) (or parallel `invoke_subagent` calls when 3–4 simple workers suffice).
3. Sync outcomes into `swarm_coordinator.py`, run `gate-check --stage final`.

### B. Antigravity — Native `/swarm` Board (Only When User Invoked `/swarm`)
Never call the `swarm` tool unprompted outside an active `/swarm` request. When `/swarm` **is** active:
1. Map each `swarm_coordinator.py` task to a named worker (`swarm{action:"add", name:"pricing_maker", workspace:"share", brief:"Read briefs/T01.md..."}`) and add 1 `@verifier` per 2–4 workers.
2. Write the `swarm_pane` overview (`plan.json`) if active, and reference earlier board messages by `#seq` number (`@verifier check #4`) without copy-pasting.
3. Use `swarm_wait` (zero-token sleep) instead of polling `read_board`. Land worktree branches before calling `swarm{action:"kill"}`.

### C. Claude Cowork / Claude Code / OpenCode / Hermes / Pi
1. Run `swarm_coordinator.py init` and `add-task` to generate `briefs/<id>.md` and verify `gate-check --stage plan`.
2. Launch Wave 1 workers in parallel via `Task` (or native subagent tool), pointing each strictly to `briefs/<id>.md` and instructing it to write `artifacts/<id>.md`.
3. Collect concise results (`submit-result`), launch independent verifiers (`verify-task` with `verifier_id != worker_id`), run rework if `changes_requested`, resolve conflicts (`log-conflict`), and pass `gate-check --stage final`.

---

## 4. Calibrated Conflict Resolution

When two workers disagree (e.g., Growth wants rapid rollout; Risk wants 6-month compliance lock):
1. **Never average contradictions** into mushy advice. Log the exact clash via `swarm_coordinator.py log-conflict`.
2. **Test or Separate:**
   - If empirical: run a targeted verification check or quantitative simulation (`dr_engine.py simulate`).
   - If structural trade-off: design a `--bypass-wedge` (e.g., narrow pilot scope, deterministic gate on high-risk outputs, or partner piggybacking) that honors the hard constraint **without** paralyzing execution.
3. Audit final synthesis for **anti-groupthink**, **anti-sycophancy**, and **anti-defeatism** before `finalize`.
