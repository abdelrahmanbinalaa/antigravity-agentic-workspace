# 360° Horizon Expansion & Specialist Lenses

## Table of Contents
- [1. The 8 Specialist Lenses](#1-the-8-specialist-lenses)
- [2. Cross-Industry Structural Abstraction](#2-cross-industry-structural-abstraction)
- [3. Unknown-Unknowns Discovery Protocol](#3-unknown-unknowns-discovery-protocol)
- [4. Recording Horizon Updates via CLI](#4-recording-horizon-updates-via-cli)

---

## 1. The 8 Specialist Lenses

Every `standard` or `exhaustive` investigation must sweep across all 8 lenses (minimum 5 marked `covered`; minimum 3 in `lite` mode; mark irrelevant lenses explicitly as `not_applicable` with a reason rather than silently skipping them):

| Lens ID | Core Focus | Mandatory Diagnostic Questions |
| :--- | :--- | :--- |
| `first_principles_science` | Physics, math, thermodynamics, theoretical bounds | What are the irreducible physical/mathematical limits (latency, energy, yields, information theory, Little's Law)? What is true even if every current vendor disappears? |
| `technical_architecture` | Systems, data pipelines, tooling, failure recovery | Where are single points of failure, hidden integration glue, state corruption risks, and maintenance burden? What already exists off-the-shelf vs must be built? |
| `market_unit_economics` | Willingness-to-pay, CAC/LTV, margin floors, cash conversion | Who pays, out of which budget line, and why now? What is the true fully loaded unit cost at low vs medium volume? Where do cashflow gaps kill profitable ideas? |
| `operations_supply_chain` | Throughput, bottlenecks, SLAs, QA, staffing, handoffs | What happens at 1x, 5x, and 20x volume? Which step has the longest queue, highest defect rate, or human bottleneck? How do edge cases enter and get resolved? |
| `behavioral_incentives` | Principal-agent conflicts, adoption friction, trust | Who loses status, margin, or convenience if this succeeds—and how will they sabotage or ignore it? What is the user's actual switching cost in minutes and anxiety? |
| `competitive_game_theory` | Moats, incumbent retaliation, commoditization, substitutes | If this works, how fast can incumbents copy, bundle, or undercut? What makes the position defensible (distribution, data loop, switching cost, speed, trust)? |
| `legal_regulatory_tail_risk` | Compliance, contracts, IP, liability, concentration risk | Which licenses, data privacy rules, tax/customs duties, platform TOS bans, or single-supplier dependencies can halt the project overnight? |
| `cross_domain_analogues` | Proven mechanisms from unrelated industries | Which unrelated domain solved an isomorphic bottleneck years ago, and what exact mechanism can be transplanted directly? |

---

## 2. Cross-Industry Structural Abstraction

Never search only inside the user's named industry. Follow this 3-step transfer method:

1. **Strip Domain Nouns:** Replace industry-specific terms with abstract mechanism verbs.
   - *Example:* "Matching tender RFQs to supplier prices under tight SLAs" → *"Multi-constraint combinatorial matching under noisy unstructured documents and strict deadline penalties."*
2. **Map to Isomorphic Domains:** Check how at least 2–3 mature domains solve that exact mechanism:
   - **Aviation / Maritime:** Checklists, black-box audit trails, dual-path redundancy, maintenance intervals.
   - **Logistics / Cold-Chain:** Hub-and-spoke routing, cross-docking, buffer stock sizing, cutoff windows.
   - **Fintech / Underwriting:** Two-stage triage (fast deterministic rules + deep human/model review on edge cases), escrow, confidence scoring.
   - **Compiler / Software Engineering:** Deterministic verification gates, canary rollouts, idempotency, schema contracts.
   - **Hospital Triage / Emergency Ops:** Severity scoring, fast-track lanes, escalation SLAs.
3. **Extract & Adapt:** Record only mechanisms that fit the user's constraints (`budget`, `team_size`, `time_to_first_value`) in `horizon_map.json -> analogues`.

---

## 3. Unknown-Unknowns Discovery Protocol

Before exiting Loop 1, explicitly generate at least 3 blind-spot questions (1 in `lite`) covering:
1. **Second-Order Bottlenecks:** *"If we solve the primary bottleneck tomorrow, what immediately becomes the new constraint downstream?"*
2. **Complementor & Ecosystem Dependencies:** *"Which upstream API, supplier, payment rail, or platform rule could break our unit economics?"*
3. **Day-2 Lifecycle & Maintenance Drag:** *"Who maintains data freshness, disputes, refunds, exceptions, or drift in month 3?"*
4. **Non-Consumer / Hidden Decision Maker:** *"Who blocks the deal without being the primary user (finance, legal, procurement, IT security, spouse/operator)?"*

---

## 4. Recording Horizon Updates via CLI

Use `dr_engine.py update-horizon` so `brief.json` and `horizon_map.json` remain machine-verified:

```bash
python <skill_dir>/scripts/dr_engine.py update-horizon \
  --dir "<slug_dir>" \
  --decision "Concrete decision statement" \
  --constraints '{"budget_usd": 500, "team": "solo", "timeline_weeks": 4}' \
  --hypotheses-json '["H1: ...", "H2: ..."]' \
  --lens market_unit_economics \
  --status covered \
  --summary "Key unit-economics findings..." \
  --analogues-json '["Aviation pre-flight checklist -> ...", "Fintech 2-stage triage -> ..."]' \
  --blind-spots-json '["BS1: ...", "BS2: ...", "BS3: ..."]'
```
