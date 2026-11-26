---
name: n8n-workflow-research
description: Research and extract reusable architectural patterns from n8n community workflows. Use when the task involves searching n8n.io/workflows for templates by topic (RAG, agentic loops, document chunking, supervisor agents, self-correction), or downloading a workflow's full node graph (nodes + connections + parameters) for analysis, replication, or architectural distilling. Triggers on requests like research n8n templates for X, find workflows that do Y, extract the JSON of n8n workflow Z, reverse-engineer how a community workflow achieves some pattern, or survey n8n patterns for embedding into another system.
---

# n8n Workflow Research

Two public surfaces are enough to extract full n8n workflow graphs without scraping the Nuxt SPA or rendering JS-heavy Google results. Use them in combination.

## The two endpoints that actually work

### 1. Public workflow JSON endpoint
```
GET https://api.n8n.io/api/workflows/<id>
```
- Returns `{"data": {"id", "name", "description", "workflow": {"nodes": [...], "connections": {...}}, "nodes" count, "views", ...}}`
- Request the canonical page first (`https://n8n.io/workflows/<id>-<slug>/`) to confirm the ID is right and pull the human description. Then fetch the API for the full graph.
- `nodes[i].type` uses long prefixes (`@n8n/n8n-nodes-langchain.agent`, `n8n-mcp` etc.). Strip `@n8n/n8n-nodes-langchain.` and `@n8n/` for display, keep the dot-tail (`agent`, `lmChatOpenAi`, `toolWorkflow`, etc.) as the canonical short name.
- `connections` schema: `{"<sourceNode>": {"<channel>": [[ {"node": "<target>", "index": 0} ]]}}`. Channels are `main`, `ai_tool`, `ai_languageModel`, `ai_memory`, `ai_embedding`, `ai_document`, `ai_textSplitter`, `ai_reranker`, `ai_vectorStore`. Treat the inner list as a length-1-or-2 list of connection-arrays — index `connections[src][ch][0]` is usually the matrix.
- No filtering / sort params on this endpoint — query params are mostly ignored. Discover interesting IDs via search engines (`site:n8n.io/workflows <keyword>` gives the cleanest hit list and lands you on canonical pages with IDs).

### 2. Discourse search API for the community forum
```
GET https://community.n8n.io/search.json?q=<query>[&category=<slug>]
GET https://community.n8n.io/raw/<topic_id>.json
```
- `search.json` returns `posts[]` with blurb + topic_id — enough to triage. Default returns everything; add `&category=workflows` to filter to the workflows category.
- `raw/<id>.json` does NOT return JSON. It returns the post body in Discourse markdown-flavored format with a header `username | timestamp | #N`. Parse it as text and grep for embedded JSON blobs enclosed in triple backticks — many users paste their full workflow under "Please share the workflow". Combine adjacent posts to reconstruct a complete workflow. This is the primary vein for finding pattern-rich workflows that aren't published to the gallery yet.
- Topic IDs in URLs are `/t/<id>` (also visible as `#t<id>`); the `raw` endpoint uses the same integer.
- Rate limit: ≤5 requests in 30s; expect HTTP 429 if scrolled aggressively. Sleep 2-4s between calls.

## Discovery workflow (use this exact loop)

1. **Seed by topic search.** Send 4-6 different phrasings through DuckDuckGo HTML with `site:n8n.io/workflows`. Different verbs surface different rankings: e.g. for self-correction try `valid...retry`, `Switch node JSON schema` and `output validator` independently rather than just one.
2. **For each candidate ID, fetch the API.** One call = one workflow JSON. Don't waste time on Google's full-text snippets; trust the page title + description to decide if it's worth the API hit.
3. **Map the graph.** Build `{name: short_type}` from `nodes[]`, then iterate `connections` to get edges by channel. Print the topology as `[type] src --channel--> [type] tgt` — this surfaces loops, supervisor patterns (one agent's name appearing as `ai_tool` for many others), and the rare `toolWorkflow` (sub-workflow-as-tool) vs `executeWorkflowTrigger` (main workflow triggered by a sub-workflow).
4. **Cross-check on the forum.** `search.json` with terms pulled from the API workflow name (e.g. `"vector store" "metadata filter"`) often turns up users describing the exact same pattern with different shape variations — gold for architectural triangulation.

## Patterns to actively look for in connections

These channel signatures are how the architectural pattern announces itself at a glance:

| Pattern | Tell-tale signature |
|---|---|
| Supervisor / multi-agent | One `agent` node has many other `agent` or `toolWorkflow` nodes feeding into it via `ai_tool` |
| RAG retrieval | `vectorStoreXxx --ai_tool--> agent` plus `embeddingsXxxx --ai_embedding--> vectorStoreXxx` and `documentDefaultDataLoader --ai_document--> vectorStoreXxx` |
| Re-ranker | `rerankerCohere --ai_reranker--> vectorStoreSupabase` |
| Self-correction loop | `agent --main--> set (validate) --main--> switch --main--> set (format error) --main--> agent` (back-edge to Agent) — see references/example-self-correction-4316.md if available |
| Sub-workflow | Look for `toolWorkflow --ai_tool--> agent` (sub-workflow exposed as a tool) — or `Execute Workflow Trigger` node = entry point when this workflow is *called* by another |
| Long-text ingestion | `splitInBatches --main--> [extract+embed+vectorStore cluster]` then back to `splitInBatches` (a true loops, not Switch) |

## Pitfalls / things to NOT do

- The n8n.io search results page is server-rendered to an empty SPA shell — don't waste tokens `curl`-ing `/?q=...`. Only the canonical `/workflows/<id>-<slug>/` page renders real workflow info, and even those pages don't include the full graph (you need the API for that).
- `api.n8n.io/api/workflows` (the list endpoint) does NOT honor `?q=`, `?category=`, `?tags=`, `?integration=` — it always returns the first workflow. Use search engines to discover IDs, then the per-ID API to fetch.
- `community.n8n.io/raw/<id>.json` is misleadingly named — content-type is plain text, body is markdown. Don't try to `json.load` the response; read it as text and extract embedded workflow code blocks.
- Forum responses can include both report ("works fine") and helpful code. Scan for the first response from a `n8n` admin or from a 1+ like user — those usually contain the actual fix or pattern. The opening post is often vague.
- Filter shortlist by node count > 8 and by presence of: `switch`, `loop`, `splitInBatches`, `toolWorkflow`, `executeWorkflowTrigger`, `aggregate`, or any `agent` besides `lmChatOpenAi`. Skip small linear workflows (the user has probably already excluded those in the brief).
- Don't store 5MB workflow blobs in memory for many workflows — once you have the topology printed, drop the bodies and keep `{id, name, short_node_signature}` summary lines. Only re-fetch if you need a parameter detail.

## Working with the source code for parameter truth

When the marketing descriptions leave gaps on parameter behavior, read the actual node TypeScript:

```
https://raw.githubusercontent.com/n8n-io/n8n/master/packages/@n8n/nodes-langchain/nodes/<type>/<type>.node.ts
```

Specifically useful for:

- `text_splitters/TextSplitterRecursiveCharacterTextSplitter` — confirms `chunkSize` default 1000, `chunkOverlap` default 0, and that `options.splitCode` accepts `markdown|html|python|js|...`. When default chunking doesn't keep paragraphs together on long fiction, escalate to a custom `Code` node that runs `RecursiveCharacterTextSplitter` directly from `@langchain/textsplitters`.
- `vector_stores/VectorStoreSupabase` — confirms that metadata stored in `metadata` JSONB column is searchable via the node's `Metadata Filter` UI.
- `agents/Agent` — confirms the `hasOutputParser`, memory, tools slots, and `onError: 'continueRegularOutput'` setting — useful for self-correction loops where you want the agent to keep emitting text even when JSON parses broken.

## Deliverable shape for a "research & report" task

When asked to produce a curated list of pattern templates for a build:

1. 5-7 workflows total — not more. The user wants synthesis, not a directory listing.
2. For each: URL, category label, node breakdown (table-format), data payload (what crosses the edges), and a *specific* "how this applies to your project" paragraph. The last one is what the user is paying for.
3. If a workflow is huge (200+ nodes like `jarvis-ai-personal-assistant`), call that out — it's a reference architecture, not a template to ingest wholesale.
4. Always show the topology as `[type] src --channel--> tgt` — that line is the most informative compression of the graph.

## Curated reference for LLM-orchestration / long-form writing backends

See `references/workflows-for-novel-rag-engine.md` for a pre-distilled list of 9 community workflows (IDs 4316, 5436, 6158, 6186, 2446, 6345, 8707, 9933, 9934) covering all four architectural categories — self-correction, two-stage retrieval with metadata filters, recursive-character markdown chunking, and supervisor + sub-workflow multi-agent. Each entry includes the topology, the lesson, and how to apply it specifically inside a long-form writing engine. Start there when the user asks for pattern templates for a RAG + revision engine.
