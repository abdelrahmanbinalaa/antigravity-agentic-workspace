# Scientific, Systems & Quantitative Operational Modeling

## Table of Contents
- [1. Framework Selection Matrix](#1-framework-selection-matrix)
- [2. Structural & Innovation Frameworks (No-Fluff Usage)](#2-structural--innovation-frameworks-no-fluff-usage)
- [3. Quantitative Modeling via `dr_engine.py simulate`](#3-quantitative-modeling-via-dr_enginepy-simulate)
- [4. Model JSON Specifications](#4-model-json-specifications)

---

## 1. Framework Selection Matrix

Never force every framework onto every topic. Pick 1–2 structural frameworks + 1 quantitative model matching the problem geometry:

| Problem Type | Structural Framework(s) | Quantitative Engine (`dr_engine.py simulate`) |
| :--- | :--- | :--- |
| Market entry / product strategy / sizing | Bottom-Up TAM/SAM/SOM + **Wardley Mapping** + **Zwicky Box** | `monte-carlo` (unit economics & payback) + `pareto-mcda` (segment/channel ranking) |
| Operations, throughput, SLAs, supply chain | **Theory of Constraints (TOC)** + **Causal Loop Diagram** + **FMEA** | `lp-optimize` (allocation/routing/capacity) + `monte-carlo` (queue/SLA tail risk) |
| Engineering / build-vs-buy / architecture | **Wardley Mapping** + **TRIZ Separation** + Pre-Mortem | `pareto-mcda` (architecture trade-offs + weight-perturbation stability) |
| Pricing, procurement, tender, portfolio mix | Game-Theoretic Payoff Matrix + **Zwicky Box** | `lp-optimize` (MILP mix) + `monte-carlo` (margin sensitivity tornado) |

---

## 2. Structural & Innovation Frameworks (No-Fluff Usage)

Write the selected framework(s) to `<slug_dir>/models/<framework>.md` or `.json`:

1. **Systems Thinking (Stocks, Flows, Feedback Loops, Delays):**
   - Map core **Stocks** (inventory, cash, qualified leads, backlog, trust), **Reinforcing Loops (`R`)**, **Balancing Loops (`B`)**, and **Delays** (lead times, onboarding lag). Identify the top 2 **Meadows Leverage Points** (e.g., changing information feedback delay or incentive rule rather than pushing harder on a parameter).
2. **Theory of Constraints (TOC 5 Focusing Steps) + Little's Law:**
   - Apply $L = \lambda W$ (Work-in-Progress = Arrival Rate × Lead Time). Identify the **single system constraint**; do not optimize non-bottlenecks. Specify: *Identify → Exploit → Subordinate → Elevate → Repeat*.
3. **Morphological Analysis (Zwicky Box) for Solution Invention:**
   - Define 4–6 orthogonal problem dimensions (e.g., *Acquisition Channel*, *Delivery Mechanism*, *Pricing Model*, *Automation Boundary*, *Trust Proof*) with 3–5 concrete values each. Prune logically impossible pairs, then extract 3–5 non-obvious high-leverage combinations.
4. **TRIZ Contradiction Separation:**
   - Whenever two desirable goals clash (e.g., *high customization* vs *low labor cost*, or *strict QA* vs *fast turnaround*), refuse binary compromise and apply the 4 separation principles:
     - **In Time:** Automate/standardize during prep, customize only at final assembly.
     - **In Space / Segment:** High-touch only on top 20% edge cases, self-serve on 80% routine flow.
     - **Between Whole & Parts:** Modularize commodity core, differentiate the outer wrapper.
     - **By Condition:** Trigger strict verification only when confidence score < threshold.
5. **FMEA Pre-Mortem (`RPN = Severity × Occurrence × Detection`, 1–5 each):**
   - Score failure modes; any item with `RPN >= 27` or `Severity == 5` requires an engineered prevention or early-detection trigger.

---

## 3. Quantitative Modeling via `dr_engine.py simulate`

Prose arithmetic is forbidden for budgets, unit economics, probabilities, or optimization. Write a JSON spec file in `<slug_dir>/models/` and run:

```bash
python <skill_dir>/scripts/dr_engine.py simulate \
  --dir "<slug_dir>" \
  --name "<model_name>" \
  --type <monte-carlo|pareto-mcda|lp-optimize> \
  --spec "<slug_dir>/models/<spec_file>.json"
```

---

## 4. Model JSON Specifications

### A. `monte-carlo` (`<slug_dir>/models/mc_spec.json`)
Computes `mean`, `std`, `p10`, `p50`, `p90`, `prob_above_threshold`, and **Spearman rank-correlation tornado sensitivity**:
```json
{
  "trials": 10000,
  "seed": 42,
  "variables": {
    "monthly_leads": {"dist": "triangular", "low": 40, "mode": 80, "high": 150, "min": 10},
    "conv_rate": {"dist": "normal", "mean": 0.08, "std": 0.02, "min": 0.01, "max": 0.30},
    "gross_margin_per_deal": {"dist": "uniform", "low": 350, "high": 650},
    "fixed_cost": {"dist": "fixed", "value": 1800}
  },
  "formulas": {
    "monthly_net_profit": "monthly_leads * conv_rate * gross_margin_per_deal - fixed_cost"
  },
  "thresholds": {
    "monthly_net_profit": 0.0
  }
}
```
Supported distributions: `normal` (`mean`, `std`), `triangular` (`low`, `mode`, `high`), `uniform` (`low`, `high`), `lognormal` (`mean`, `sigma`), `fixed` (`value`), plus optional `min`/`max` clamping.

### B. `pareto-mcda` (`<slug_dir>/models/mcda_spec.json`)
Enforces `hard_limit` user constraints, extracts the exact non-dominated **Pareto frontier**, computes TOPSIS scores, and tests rank stability over 500 `±25%` weight perturbations:
```json
{
  "perturbation_trials": 500,
  "criteria": [
    {"name": "net_margin_pct", "weight": 0.35, "direction": "max", "hard_limit": 15},
    {"name": "setup_cost_usd", "weight": 0.25, "direction": "min", "hard_limit": 2000},
    {"name": "days_to_first_revenue", "weight": 0.25, "direction": "min"},
    {"name": "defensibility_score", "weight": 0.15, "direction": "max"}
  ],
  "options": [
    {"name": "Option A", "scores": {"net_margin_pct": 42, "setup_cost_usd": 400, "days_to_first_revenue": 14, "defensibility_score": 7}},
    {"name": "Option B", "scores": {"net_margin_pct": 55, "setup_cost_usd": 3500, "days_to_first_revenue": 60, "defensibility_score": 9}}
  ]
}
```

### C. `lp-optimize` (`<slug_dir>/models/lp_spec.json`)
Solves LP or MILP via `scipy.optimize` (HiGHS) and outputs an explicit **Solver Certificate** with binding constraints and slacks:
```json
{
  "sense": "max",
  "var_names": ["channel_a_units", "channel_b_units"],
  "c": [120, 180],
  "A_ub": [
    [20, 45],
    [1, 1]
  ],
  "b_ub": [900, 30],
  "constraint_names": {"ub": ["budget_cap", "ops_capacity_slots"]},
  "bounds": [[0, null], [0, null]],
  "integrality": [1, 1]
}
```
