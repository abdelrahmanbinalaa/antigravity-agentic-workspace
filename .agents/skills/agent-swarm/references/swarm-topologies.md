# Swarm Topologies, Sizing & Anti-Groupthink Design

## Table of Contents
- [1. Choosing the Right Topology](#1-choosing-the-right-topology)
- [2. Optimal Swarm Sizing & Cost Discipline](#2-optimal-swarm-sizing--cost-discipline)
- [3. Anti-Groupthink Orthogonal Persona Design](#3-anti-groupthink-orthogonal-persona-design)
- [4. Pairing `agent-swarm` with `deep-research`](#4-pairing-agent-swarm-with-deep-research)

---

## 1. Choosing the Right Topology

Match the swarm shape to the actual dependency and risk geometry of the task:

| Topology ID | Structure | Best For | Mandatory Guardrail |
| :--- | :--- | :--- | :--- |
| `map-reduce` | `N` sharded collectors → dedup/synthesizer → verifier | Auditing 10+ files, scraping N competitors, multi-channel research sweeps | Shard cleanly so zero workers touch overlapping targets |
| `specialist-council` | 3–7 orthogonal domain experts → conflict log → calibrated arbiter | Market entry, architecture decisions, business/operational strategy | Must have `>= 2` distinct `cognitive_stance`s; never average contradictions |
| `competing-hypotheses` | 2–4 rival hypotheses or rival isolated implementations → rubric tournament | Hard debugging, competing technical designs, uncertain market theses | Keep rival workers isolated (`worktree_branch` for code); judge via tests/rubric |
| `maker-checker-dag` | Dependency waves (`T01,T02` → `T03`) + 1 independent verifier per 2–3 makers | Multi-file feature builds, pipeline migrations, structured deliverables | `worker_id != verifier_id`; concurrent writers need `disjoint_paths` or `worktree_share` |
| `red-blue-calibration` | Blue builder vs Red adversarial breaker → Calibrated Arbiter | Security/fraud audits, tender pricing stress-tests, fragile launches | Every Red attack must be met with a realistic diagnosis + low-friction `Path A` bypass |

---

## 2. Optimal Swarm Sizing & Cost Discipline

- **Sweet spot is 3–7 focused agents** (plus verifiers). Spawning 12–20 agents with vague roles creates duplicate findings, board chatter, and coordination tax that degrades quality.
- **Wave over chaos:** Use `depends_on` to sequence upstream contract/schema design (`Wave 1`) before parallel implementation (`Wave 2`) and integration (`Wave 3`).
- **Model tier matching:** Use cheap/fast models (`flash` / `haiku`) for high-fan-out read/search shards; use strong models (`inherit` / `opus` / `pro`) for architecture, red-teaming, verification, and final synthesis.

---

## 3. Anti-Groupthink Orthogonal Persona Design

Cloning 4 identical agents produces 4 copies of the same blind spot. Assign **uncorrelated incentives and failure priorities** via `--cognitive-stance`:

- **First-Principles / Unit-Economics Hawk:** Optimizes for irreducible cost floors, cash conversion, and physical/math limits.
- **Operational Bottleneck / SLA Realist:** Assumes messy inputs, edge-case queues, human error, and Day-2 maintenance drag.
- **Adversarial Red-Teamer / Skeptic:** Assumes the plan will fail in week 2; hunts regulatory traps, incumbent retaliation, and single points of failure.
- **Asymmetric Wedge / Innovation Architect:** Refuses dead-end defeatism; uses TRIZ separation, piggybacking, and narrow wedges to make constrained execution viable.

---

## 4. Pairing `agent-swarm` with `deep-research`

When running exhaustive market, product, or operational research:
1. Use `agent-swarm` (`specialist-council` or `map-reduce`) to execute `deep-research` **Loop 1–2** concurrently across specialist lenses and opposition hunting.
2. Feed collected sources/claims into `dr_engine.py` for quantitative simulation (`monte-carlo`, `pareto-mcda`, `lp-optimize`) in **Loop 3**.
3. Run `red-blue-calibration` in **Loop 4–5** so the final output passes both `dr_engine.py gate-check --loop final` and `swarm_coordinator.py gate-check --stage final`.
