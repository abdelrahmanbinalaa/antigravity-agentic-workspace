---
name: agent-swarm
description: 'Orchestrate coordinated multi-agent swarms (3+ agents) with deterministic dependency DAGs, concurrent file-collision locks, orthogonal anti-groupthink personas, independent maker-checker verification, and calibrated conflict resolution across Antigravity, Claude, and other synced agents. Use for parallel multi-specialist investigations, multi-file engineering, red-vs-blue stress testing, or competing-hypothesis tournaments (triggers: agent swarm, multi-agent team, specialist council, parallel swarm, maker-checker, سرب وكلاء، فريق وكلاء، مجلس خبراء، عمل متوازي). Differentiator: use agent-swarm for 3+ coordinated agents with DAG waves, collision locking, and independent verifiers; use launch-subagent for 1-2 simple subtasks.'
---

# Agent Swarm — Multi-Topology Orchestration & Verification Engine

Coordinate 3–7 specialized agents using a **shared deterministic blackboard** (`scripts/swarm_coordinator.py`), strict **collision locks**, **independent maker-checker verification**, and **calibrated conflict resolution**.

## 1. Core Principles

- **Coordinator Orchestrates; Workers Execute:** Keep the coordinator focused on splitting work, resolving conflicts, and verifying gates — not drowning in raw implementation details.
- **No Echo Chambers:** Give specialists orthogonal `--cognitive-stance` mandates.
- **No Concurrent File Collisions:** Parallel writers must either hold non-overlapping `--owned-paths` under `disjoint_paths` or run in isolated `worktree_share` / `worktree_branch` workspaces.
- **Maker != Checker:** Self-verification is blocked programmatically (`verifier_id != worker_id`).
- **Calibrated Realism:** Resolve Red vs Blue clashes without sycophancy or defeatism — every real blocker must yield a viable, low-friction bypass wedge.

## 2. Setup & Blackboard Initialization

Set `SKILL_DIR` to this skill's directory, pick a topology from [swarm-topologies.md](references/swarm-topologies.md) (`map-reduce`, `specialist-council`, `competing-hypotheses`, `maker-checker-dag`, `red-blue-calibration`), check [live-models.md](references/live-models.md) for current Antigravity model role-slots & cross-family critic pairing (refresh with `python ~/.skills-manager/sync_models.py`), and initialize `{SWARM_DIR}`:

```bash
python "{SKILL_DIR}/scripts/swarm_coordinator.py" init \
  --root "{SWARM_ROOT}" --slug "{SLUG}" \
  --goal "{GOAL}" --topology "{TOPOLOGY}" \
  --constraints "{USER_CONSTRAINTS}" --gate-cmd "{OPTIONAL_TEST_CMD}"
```

Every stage ends with `swarm_coordinator.py gate-check`. **Exit code `2` (`LOOP_BACK_REQUIRED`) means you must loop back and close `blocking_gaps` before advancing.**

## 3. The 5-Stage Closed-Loop Swarm Workflow

### Stage 1: Topology, Sizing & Collision-Locked DAG
Read [swarm-topologies.md](references/swarm-topologies.md) and [briefing-and-contracts.md](references/briefing-and-contracts.md).
1. Partition the goal into 3–7 tasks with explicit `--depends-on`, `--cognitive-stance`, `--isolation`, and `--owned-paths`:
   ```bash
   python "{SKILL_DIR}/scripts/swarm_coordinator.py" add-task \
     --dir "{SWARM_DIR}" --id T01 --role "Unit-Economics Hawk" \
     --cognitive-stance "cost_floor_skeptic" \
     --objective "..." --isolation read_only
   ```
2. **Gate:**
   ```bash
   python "{SKILL_DIR}/scripts/swarm_coordinator.py" gate-check --dir "{SWARM_DIR}" --stage plan
   ```

### Stage 2: Parallel Wave Execution
1. Dispatch ready tasks wave-by-wave using the active runtime:
   - **Antigravity (default):** Use `run_workflow` with [agy_swarm_runner.py](scripts/agy_swarm_runner.py) (or parallel `invoke_subagent`).
   - **Antigravity `/swarm` mode (only if user invoked `/swarm`):** Add workers on the board referencing `briefs/<id>.md` and wait via `swarm_wait`.
   - **Claude / OpenCode / Hermes / Pi:** Dispatch parallel `Task`/subagent calls pointing to `briefs/<id>.md`.
2. Record each worker's detailed output in `artifacts/<id>.md` and log a compact summary (`<= 1200` chars) via `submit-result`.
3. **Gate:**
   ```bash
   python "{SKILL_DIR}/scripts/swarm_coordinator.py" gate-check --dir "{SWARM_DIR}" --stage execution
   ```

### Stage 3: Independent Maker-Checker Verification & Rework Loop
1. Assign 1 independent verifier per 2–3 tasks (`verifier_id != worker_id`). Verifiers inspect `artifacts/<id>.md`, workspace diffs, and `gate_cmd` outputs.
2. Record verdicts with `verify-task --verdict approved|changes_requested`.
3. Any `changes_requested` task loops back to rework (`submit-result` + re-verify) until `approved`.

### Stage 4: Conflict Resolution & Calibrated Synthesis
1. Log every contradiction or trade-off between workers via `log-conflict`, supplying an explicit `--resolution` and `--bypass-wedge` (never average opposites).
2. Write `{SWARM_DIR}/final_deliverable.md` (if pairing with `deep-research`, ensure `dr_engine.py` quantitative models & `Path A/B/C` ladders are integrated).
3. **Gate:**
   ```bash
   python "{SKILL_DIR}/scripts/swarm_coordinator.py" gate-check --dir "{SWARM_DIR}" --stage verification
   ```

### Stage 5: Final Calibration Gate
1. Run `finalize` confirming anti-groupthink, anti-sycophancy, anti-defeatism, and `gate_cmd` checks:
   ```bash
   python "{SKILL_DIR}/scripts/swarm_coordinator.py" finalize \
     --dir "{SWARM_DIR}" --verifier-id "independent_arbiter" \
     --summary "..." --anti-groupthink-passed --anti-sycophancy-passed --anti-defeatism-passed
   python "{SKILL_DIR}/scripts/swarm_coordinator.py" gate-check --dir "{SWARM_DIR}" --stage final
   ```
2. If running code tasks in `worktree_share`/`worktree_branch`, land/merge approved changes before closing worktrees.
