# Sourcing Waterfall, Triangulation & Delta-Refresh Protocol

## Table of Contents
- [1. Dynamic Tool-Routing Waterfall](#1-dynamic-tool-routing-waterfall)
- [2. Evidence Hierarchy & Triangulation Rules](#2-evidence-hierarchy--triangulation-rules)
- [3. Opposition & Disconfirmation Hunting](#3-opposition--disconfirmation-hunting)
- [4. Upstream Statistical Catalog & Refresh Targets](#4-upstream-statistical-catalog--refresh-targets)

---

## 1. Dynamic Tool-Routing Waterfall

Always check what is active in the current environment before running searches; escalate down the waterfall only when earlier layers fail or lack depth:

1. **Web Search (`search_web` / native search):** Fast discovery of primary docs, pricing pages, changelogs, papers, regulatory filings, and opposing views.
2. **Multi-Platform Social & Forum Reality (`agent-reach`):** Run `agent-reach doctor --json` first; use for practitioner complaints, Reddit/X/YouTube/GitHub discussions, and real-world failure stories (never cite social chatter alone as `T1`/`T2` proof).
3. **Structured Crawling & Anti-Bot Extraction (`scrapling-official` / `firecrawl`):**
   - Check `firecrawl --status` if `FIRECRAWL_API_KEY` is configured.
   - Use `scrapling` (`--ai-targeted` on CLI) for JS-heavy pages, Cloudflare-protected pricing/catalogs, or concurrent multi-page crawls.
4. **Live Browser Inspection (`browser` subagent / `playwright` MCP):** Use when content sits behind interactive UI, tabs, pagination, or calculators.
5. **External Datasets & Analytics MCPs (when configured):** `kaggle`, `huggingface`, `datacloud_bigquery_remote`, `brightdata`, `apify`, `dataforseo`, `research-toolkit`, or `searxNcrawl`.

**Zero-Fabrication Rule:** If a page cannot be fetched or returns empty content, record `--unreachable` with empty quote or omit the claim. Never invent a URL, quote, or market-share percentage.

---

## 2. Evidence Hierarchy & Triangulation Rules

Assign every claim in `claims.jsonl` one strict tier:

| Tier | Definition | Allowed Usage |
| :--- | :--- | :--- |
| `T1_PRIMARY` | Official docs, SEC/regulatory filings, peer-reviewed studies, live scraped pricing/specs, reproducible local benchmarks | Core facts & hard constraints |
| `T2_CORROBORATED` | Corroborated across `>= 3` independent sources spanning `>= 2` distinct `source_type`s (`primary_doc`, `academic`, `market_data`, `code_benchmark`, `practitioner`, `regulatory`) | Core strategic theses |
| `T3_SINGLE_PRACTITIONER` | Single practitioner report, case study, blog post, or non-triangulated vendor claim | Directional signal only; explicitly labeled uncorroborated |
| `T4_INFERENCE` | Logical deduction, cross-industry transfer, or model projection | Marked explicitly as *Inference / Hypothesis* |

`dr_engine.py add-claim` and `gate-check --loop 2` automatically enforce that any `--core-thesis` marked `T1`/`T2` without `>= 3` sources across `>= 2` source types is downgraded to `T3_SINGLE_PRACTITIONER`.

---

## 3. Opposition & Disconfirmation Hunting

Every investigation (even `lite`) must run dedicated counter-evidence queries before Loop 2 can pass (`--disconfirming` in `add-source` or `--contradicts` in `add-claim`):
- Search `"<topic/product> failure" OR "post-mortem" OR "why failed" OR "unit economics problem"`
- Search `"<vendor/method> complaints" OR "hidden cost" OR "churn" OR "lawsuit" OR "ban"`
- Search `"<assumption> debunked" OR "counterexample"`

---

## 4. Upstream Statistical Catalog & Refresh Targets

For specialized macroeconomic, statistical, and validated public API registries, consult the upstream catalog at:
`https://github.com/Socialpranker/claude-deep-research` (`references/channels.md`, `references/stat_sources/`, `references/api_sources/`).

### `refresh_targets.md` Specification
Every completed run writes `<slug_dir>/refresh_targets.md` listing:
1. Key dynamic numbers/prices/laws that age quickly (with current value, source ID, and check frequency).
2. Falsification triggers for each hypothesis (`"Re-run if competitor X drops price below $Y"` or `"Re-run if regulation Z takes effect"`).
3. Delta command: on follow-up, only re-check listed targets and write `diffs/YYYY-MM-DD_delta.md`.
