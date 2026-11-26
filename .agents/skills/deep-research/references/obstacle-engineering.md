# Calibrated Realism & Obstacle-Busting Solution Engineering

## Table of Contents
- [1. The Calibrated Realism Charter](#1-the-calibrated-realism-charter)
- [2. Anti-Sycophancy & Anti-Defeatism Checklists](#2-anti-sycophancy--anti-defeatism-checklists)
- [3. Hard Laws vs Soft Conventions](#3-hard-laws-vs-soft-conventions)
- [4. The 8 Asymmetric Bypass Patterns](#4-the-8-asymmetric-bypass-patterns)
- [5. User-Context Adaptation & 3-Horizon Execution Ladder](#5-user-context-adaptation--3-horizon-execution-ladder)

---

## 1. The Calibrated Realism Charter

Every deep-research output must balance two non-negotiable poles:
1. **Zero Sycophancy (لا تملق ولا تفاؤل مضلل):** Never validate weak demand, rubber-stamp unrealistic margins, ignore hidden compliance/operational drag, or pretend a 1-person budget can execute an enterprise playbook as-is.
2. **Zero Defeatism (لا تيئيس ولا شلل تحليلي):** Never stop at *"this is hard / crowded / capital-intensive / regulated, therefore avoid it."* Every real-world obstacle is an engineering design constraint. Your job is to **invent the simplest viable path around, under, or through the constraint** that still captures value under the user's real circumstances.

---

## 2. Anti-Sycophancy & Anti-Defeatism Checklists

Audit every recommendation against both tables before passing Loop 4 & Loop 5:

| Sycophancy Red Flag (Fix Immediately) | Defeatism Red Flag (Fix Immediately) |
| :--- | :--- |
| Quoting optimistic top-line TAM without unit-level CAC/COGS/churn reality | Saying *"competitors have massive moats"* without checking where incumbents are slow or over-priced |
| Assuming conversion rates or SLA speeds with zero empirical range | Treating industry norms ("you need 6 months and \$50k") as physical laws |
| Ignoring cash-conversion lag, refunds, support load, or legal friction | Listing 10 risks with generic advice ("hire experts / raise capital") instead of concrete workarounds |
| Agreeing with contradictory user goals instead of surfacing the trade-off | Recommending "abandon the idea" without first testing a narrow wedge or pivot |

---

## 3. Hard Laws vs Soft Conventions

Classify every barrier in `obstacles.json`:
- **Hard Law (`hard_law` / mathematical limit):** Statutory prohibition, safety/licensing gate, physics, or arithmetic floor. Cannot be "hacked" — must be bypassed via **`legal_pivot`** (operating in adjacent non-restricted scope, partnering with a licensed entity, or changing who holds custody/liability).
- **Soft Convention / Friction (`resource_limit`, `market_friction`, `technical_bottleneck`, `operational_sla`, `adoption_inertia`):** Almost always caused by trying to replicate an incumbent's bloated full-scale architecture on Day 1. Bypassable via the patterns below.

---

## 4. The 8 Asymmetric Bypass Patterns

Use these exact `--bypass-pattern` keys in `dr_engine.py add-obstacle`:

1. **`wedge`**: Replace broad scope with a painful, underserved micro-workflow you can deliver end-to-end in days (land-and-expand).
2. **`piggyback`**: Ride an existing distribution channel, marketplace, regulatory license, or infrastructure instead of building your own from scratch.
3. **`scope_slice`**: Strip 80% of features/SKUs/geographies that cause operational complexity while preserving 90% of buyer value.
4. **`inversion`**: Turn the user's constraint (small size, solo speed, local dialect, zero legacy bloat) into an advantage incumbents cannot copy without cannibalizing themselves.
5. **`automation`**: Replace expensive headcount or error-prone manual steps with deterministic scripts, scrapers, validators, or templated workflows.
6. **`partnership`**: Shift capital/inventory/compliance burden to a partner via rev-share, white-label, drop-ship, or consignment.
7. **`triz_separation`**: Separate conflicting requirements in time, space, or condition (e.g., automated triage for 80% routine cases, human review only for low-confidence 20%).
8. **`legal_pivot`**: Restructure the contract, data boundary, or service role (e.g., decision-support tool vs regulated advice; B2B tooling vs B2C custody) to stay cleanly compliant.

---

## 5. User-Context Adaptation & 3-Horizon Execution Ladder

Tailor every obstacle bypass to the user's actual resources (`solo/bootstrap`, `small team`, or `established firm`):
- **Budget-constrained / Solo:** Zero custom infra on Day 1; prefer existing tools (`Python`, `Playwright`, `Scrapling`, spreadsheets/SQLite, manual concierge QA on first 5–10 customers).
- **Small Team:** Standardize handoffs, build deterministic gates and automated data collection, keep human judgment on high-margin exceptions.
- **Enterprise / Tender / Supply Chain:** Focus on SLA guarantees, audit ledgers, solver-backed margin protection, and phased pilot rollout.

Every major obstacle recorded via `dr_engine.py add-obstacle` must produce **all three paths**:
- **`Path A` (`--path-a-wedge`)**: *Easiest Immediate Wedge (48 hours – 2 weeks)* — minimal cost, zero unnecessary complexity, tests the riskiest assumption live.
- **`Path B` (`--path-b-core`)**: *Repeatable Operational System (1–3 months)* — standardized workflow, automated data/QC, predictable unit economics.
- **`Path C` (`--path-c-moat`)**: *Compounding Strategic Advantage (6+ months)* — proprietary data/distribution/cost moat once Path A & B prove demand.

```bash
python <skill_dir>/scripts/dr_engine.py add-obstacle \
  --dir "<slug_dir>" \
  --id "O01" \
  --title "High upfront licensing & enterprise sales cycle" \
  --barrier-type market_friction \
  --honest-reality "Direct enterprise deals take 4-9 months and fail 70%+ for unverified solo entrants without compliance history." \
  --bypass-pattern piggyback \
  --path-a-wedge "Package the core audit output as a paid 48-hour diagnostic delivered via existing boutique consultants who already hold vendor approval." \
  --path-b-core "Convert diagnostic data into a standardized automated pipeline with SLA evidence ledger." \
  --path-c-moat "Accumulate anonymized benchmark dataset across 50+ audits to win direct tier-1 retainers."
```
