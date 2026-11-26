---
name: n8n-workflow-architect
description: Deep-research n8n.io workflows, GitHub repos, and Discourse community to extract reusable Advanced Architectural Patterns for n8n workflows — specifically for LLM orchestration, RAG/memory, document chunking, multi-agent routing, and self-correction/critique loops. Use when user asks to scout n8n templates, find inspiration for an n8n-based backend, or design an n8n pipeline for an AI agent system. Loaded by deep-research tasks that need concrete, real n8n workflow JSON as evidence (not generic LangChain theory).
version: 0.1.0
author: Hermes (auto-generated)
license: MIT
metadata:
  hermes:
    tags: [n8n, workflow-architect, llm-orchestration, rag, multi-agent, self-correction, langchain, electron-backend]
    related_skills: [autonomous-ai-agents, software-development]
---

# n8n Workflow Architect — Deep Research Methodology

You are researching n8n.io's workflow template library to extract **concrete, reusable architectural patterns** that can be reverse-engineered for an LLM-orchestration backend.

## When to load this skill
- User explicitly asks to "find n8n workflows for X", "research n8n templates", or build an n8n-based backend for an AI app.
- User is designing a Backend-as-a-Workflow (BAW) system on top of n8n (e.g. long-form novel writing, legal-doc analysis, customer-support agents).
- User wants critique loops, supervisor patterns, metadata-filtered RAG, or recursive document chunking — and asks for **real examples** rather than LangChain theory.

## Methodology (Step-by-Step, parallelizable)

### Step 1 — Identify the canvas endpoints (do this ONCE, cache results)
The **official n8n.io template API is the source of truth**, not the HTML (Nuxt SPA, JS-required, hostile to scraping):

```bash
# Single workflow JSON
curl -sL -A "Mozilla/5.0" "https://api.n8n.io/api/workflows/{ID}" -o wf.json

# Community forum search (Discourse JSON API, no auth needed)
curl -sL -A "Mozilla/5.0" "https://community.n8n.io/search.json?q={QUERY}" -o hits.json
curl -sL -A "Mozilla/5.0" "https://community.n8n.io/raw/{TOPIC_ID}.json" -o topic.md

# GitHub repo raw paths (cache source files for splitter/embedding code)
curl -sL "https://raw.githubusercontent.com/n8n-io/n8n/master/packages/@n8n/nodes-langchain/nodes/text_splitters/TextSplitterRecursiveCharacterTextSplitter/TextSplitterRecursiveCharacterTextSplitter.node.ts"
```

Each `wf.json` payload shape:
```json
{ "data": {
    "id": 4316,
    "name": "...",
    "description": "...",
    "workflow": { "nodes": [...], "connections": {...} }
}}
```

### Step 2 — Seed ID discovery via DuckDuckGo HTML (works once, gets you 4-10 IDs per query)
```bash
curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) Chrome/120" \
  "https://html.duckduckgo.com/html/?q=site%3An8n.io%2Fworkflows+{KEYWORDS}"
# Parse with: grep -oE 'workflows/[0-9]+-[a-z0-9-]+' | sort -u
```
DuckDuckGo returns 200 OK with cookies, BUT shows captcha challenge form on rapid hits. **Rate-limit: 1 query per 4-5 seconds**, rotate User-Agent if blocked. Google.com works in browser only (rejects curl with JavaScript redirect).

### Step 3 — Filter using strict exclusion criteria
**Reject immediately** (don't pretend they fit):
- Linear A→B workflows (no loops, no switch, no sub-workflow)
- Marketing/sales/social/email-send templates
- Templates using bare `HTTP Request` node instead of Advanced AI langchain nodes
- Anything with fewer than ~10 nodes (too trivial for an architectural lesson)

### Step 4 — Extract `Node Breakdown` from `wf.workflow.nodes`
Every node has `name`, `type`, `typeVersion`, `parameters`. Group:
- **Root triggers**: `chatTrigger`, `telegramTrigger`, `scheduleTrigger`, `manualTrigger`, `googleDriveTrigger`
- **AI subnodes** (connect to root agent via port types):
  - `ai_languageModel` → `lmChatOpenAi` / `lmChatOpenRouter` / `lmChatGoogleGemini`
  - `ai_embedding` → `embeddingsOpenAi`
  - `ai_memory` → `memoryBufferWindow` / `postgresChatMemory`
  - `ai_tool` → `toolWorkflow` (sub-workflow!) / `toolHttpRequest` / `googleSheetsTool`
  - `ai_document` → `documentDefaultDataLoader`
  - `ai_textSplitter` → `textSplitterRecursiveCharacterTextSplitter`
  - `ai_reranker` → `rerankerCohere`
- **Orchestration**: `switch`, `if`, `merge`, `splitInBatches`, `aggregate`, `filter`
- **Logic/IO**: `set`, `code`, `stickyNote`

### Step 5 — Render connections as pipes
Build an edge-list: `(srcName, connType, tgtName)` for each entry in `workflow.connections[srcName][connType][0]`. This reveals:
- Loops (Switch → back to Agent → Validate → again)
- Supervisor patterns (`Main Agent` receives `ai_tool` from N sibling `toolWorkflow` nodes)
- Two-stage retrievals (metadata filter → embedding → vector store → reranker)

### Step 6 — Cross-reference forum topic discussions for "pitfalls"
Discourse topics (e.g. t/173863, t/61930, t/252928) document **real failures** other developers hit:
- Chunk overlap not working with Default Data Loader
- Multi-value metadata filter only works with custom Postgres RPC
- Structured Output Parser unreliable → use Switch node as safety net

These caveats **must** be encoded into the final report (not just the happy path).

## Five Canonical Architectural Patterns (verified, reusable)

### Pattern A — Self-Correction Loop with Switch-Bounded Retries
**Reference:** workflow 4316
```
Trigger → Agent → Validate (Set node + aiRunIndex++) → Switch
                                                  ├─ Fail → "Format Error Prompt" → back to Agent
                                                  └─ Pass → final Output
Max retries enforced by counter; safe exit to errorOutput.
```
Use for: prose style enforcement, schema-conformant JSON, code compilation checks.

### Pattern B — Two-Stage Retrieval (Metadata Filter → Semantic)
**Reference:** workflow 5436
```
Trigger → SQL "Find By Metadata" (coarse: ~20 docs)
       → Embed Query → Vector Store (fine: top-10 from candidates)
       → Reranker → Agent → Output
```
Use for: Bible/codex queries where scope is known (specific chapter/character/arc).

### Pattern C — Idempotent Re-Embedding
**Reference:** workflow 9934
```
Trigger (file change) → Delete Old Doc Rows (by file_id metadata)
                    → Loop Over Items → Switch on file type
                    → Extract → Splitter → Loader → Vector Store Insert
```
Use for: "Edit a chapter → re-embed" without dupes.

### Pattern D — Supervisor Agent calling Sub-Workflows as Tools
**Reference:** workflows 6158, 2446
```
Trigger → Supervisor Agent (ai_memory, ai_languageModel)
              ├─ ai_tool: toolWorkflow → sub-workflow ID "AAA"
              ├─ ai_tool: toolWorkflow → sub-workflow ID "BBB"
              └─ ai_tool: HTTPRequest / googleSheets
          → Compose → Output
```
Use for: complex orchestrators decomposed into modular workflows (each Sub-Agent is its own .json file in n8n).

### Pattern E — Document Ingestion Loop with Type-Specific Splitters
**Reference:** workflow 9933 + langchain source verification
```
Trigger → Loop Over Items → Switch (file type)
                            ├─ PDF/DOCX → ExtractFromFile
                            ├─ Excel/CSV → Summarize (LLM compression)
                            └─ MD/TXT → ExtractTextFile
                          → Recursive Character Splitter (splitCode: "markdown", chunkSize: 1000, chunkOverlap: 200)
                          → Default Data Loader → Encoder → Vector Store
```
**Pitfall:** Default Data Loader's `chunkOverlap` is silently ignored. Bypass by feeding the splitter as a sub-node via `ai_textSplitter` port.

## Output template (consistent across deliverables)
For each workflow the report must include:
1. **URL** (the public-facing template page, not the API)
2. **Category tag** (1..4 from original prompt)
3. **Node breakdown** — pipes between named nodes, not types
4. **Data payload** — what's actually flowing: bare text? embeddings? JSON keys?
5. **Why-it-fits + how to adapt** — concrete suggestions for the consuming system

## Pitfalls (recorded from this session)
- DDG-IP rate-limit hits fast; back off to 5s+ between calls and stop after ~6 queries.
- n8n.io HTML is Nuxt SPA — `/workflows/?q=X` returns server-rendered shell with **zero workflow IDs**.
- `api.n8n.io/api/workflows?q=X` ignores all filter params; returns oldest first. **You must know the ID.**
- Workflow node `type` field has prefixes `@n8n/n8n-nodes-langchain.` — strip them for human-readable display.
- Connections matrix is `connections[src][portType][runIndex][{node, type, index}]` — nested 4-deep.
- Forum topic `/raw/{id}.json` returns **Markdown text** (not JSON despite `.json` ext). Strip headers/footers to get the body.
- `Recursive Character Text Splitter` markdown mode splits on `["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""]` — verify in langchainjs source `libs/langchain-textsplitters/src/text_splitter.ts`.
- Default `chunkOverlap: 200` in source code, but n8n UI default shows `0`. Use **Custom splitter** mode to actually apply overlap.

## References
- `references/minasig-research-report.md` — sample deliverable for the novel-writing IDE project (مِنسَج).
