# Curated n8n workflow references for LLM orchestration / long-form writing engines

Each entry: workflow ID on n8n.io, name, category pattern, why it matters for an n8n-backed writing engine.

## Quick links

| ID | Name | Pattern |
|---|---|---|
| 4316 | Reliable AI Agent Output w/o Structured Output Parser | 4 (self-correction) |
| 5436 | Two-stage document retrieval (OpenAI + Supabase) | 1 (RAG with metadata filter) |
| 8707 | Sitemap crawling → vector storage | 1 (ingestion loop) |
| 6345 | RAG with Supabase, OpenAI, Cohere reranker | 1+3 (RAG + metadata sub-agent) |
| 9934 | Keep RAG updated with Google Drive file changes | 1+2 (chunking + loop over items) |
| 9933 | Multi-format document processing for RAG | 2 (recursive splitter) |
| 6158 | Multi-language Telegram RAG with supervisor AI (128 nodes) | 3 (supervisor + sub-workflow tools) |
| 6186 | Jarvis AI personal assistant (214 nodes) | 3 (multi-agent network) |
| 2446 | Voice activated multi-agent demo | 3 (supervisor w/ toolWorkflow sub-agents) |

API: `https://api.n8n.io/api/workflows/<id>` — `data.workflow.nodes`, `data.workflow.connections`. Channel names: `main | ai_tool | ai_languageModel | ai_memory | ai_embedding | ai_document | ai_textSplitter | ai_reranker | ai_vectorStore`.

## 4316 — Self-correction loop (canonical for output validation)

Topology (only the main edges; sticky notes omitted):

```
chatTrigger ─main─> AI Agent ─main─> [Set: Validate Output + aiRunIndex] ─main─> Switch
                                                       Switch ─main(invalid)─> [Set: Format Schema Error Prompt]
                                                                                              └─main─> AI Agent (loop back)
                                                       Switch ─main(valid)─>   [Set: Valid Schema Output] ─main─> [Set: chat Output]
OpenAI Chat Model ─ai_languageModel─> AI Agent
Simple Memory (Buffer Window) ─ai_memory─> AI Agent
```

The one-page writeup by Jim_Le and the canonical 4316 template both confirm `aiRunIndex` (in a Set node) is the retry counter; default cap is 4 retries. **This is the exact pattern you want for "logic extraction → critique → re-extract" loops where the LLM must produce machine-parseable output (e.g. a ChapterState JSON) and a bad parse should not break the pipeline.**

To extend to multi-step outputs (like a 4-field Codex update), keep `aiRunIndex` per-output, not global, and split into parallel validation paths with separate Switch nodes — one per field — each capped at 3 retries. Otherwise a single failure rotates through the global budget and burns its allocation.

Specific lesson for fiction-writing agents: include a `formatSchemaError` payload from the Switch's first branch into the AI Agent prompt as `{{ $json.schemaValidationError }}` — re-using `n8n`'s `($json).error` syntax lets the model see *what* it got wrong, not just *that* it failed.

## 5436 — Two-stage retrieval (metadata filter → similarity)

Topology (excerpt):

```
chatTrigger ─main─> [Code: Find Files]
                              └─main─> [Supabase: GetFile] ─main─> [HTTPRequest: OpenAI CreateEmbeddings]
                                                                              └─main─> [Supabase: UpdateEmbedding]
manualTrigger ─main─> Supabase GetFile ─main─> (same embedding chain)

(Connect ChatTrigger's "Find Files" chain delivers candidate filenames only — these are returned as ["fileIds"] via Aggregate.)
                                                                              network: \
                       [VectorStoreSearch] ─main─> [Filter similarity] ─main─> [Aggregate files] ─main─> [OpenAI]
                                              [Tool: Database retrieval1] ─ai_tool─> [OpenAI agent node]
```

This two-pass architecture is the textbook approach for codex-style agents. Pass 1 narrows by hard constraints (chapter, POV character, time-period metadata), Pass 2 ranks by semantic closeness. Don't try to fuse them into one query — Postgres pgvector's `IN` filter on metadata + vector similarity in same WHERE clause does not always push down to the same index scan, and worst-case you'll re-rank chunks that aren't relevant.

For "mِنسَج": the "Find Files" stage is a perfect place to inject project-level metadata derived from the Story Bible — `{chapter, pov, era, characters: [<list>]}` — and constrain retrieval before semantic search sees the query. This keeps the context window far smaller.

## 8707 — Long-form document ingestion with metadata extraction (40 nodes)

Pipeline: Manual trigger → HTTP Sitemap Fetch → XML → Split Out → Split In Batches (loop!)
  → Code (de-duplicate URLs in Supabase)
  → HTTP Crawl4ai Scrape → Wait (poll) → Quality Filter → Content-Type Detection → Better Metadata Extraction (LLM)
  → Supabase Vector Store (Document Default Data Loader + Recursive Character Text Splitter)
  → Update row in scrape_queue

The lesson is the **barrier pattern**: a `better_metadata_extraction` Code-or-LLM node sits between text extraction and the vector store insertion. Plain curl→text→embed produces chunks that are semantically rich but not categorically. Adding even a cheap LLM call to produce `{topic, era, pov, characters}` metadata per document makes future simple SQL queries (chapter=X supplement) dramatically more selective than re-running similarity search.

For "mِنسَج" a ChapterSeed could similarly run an LLM to derive metadata for each drafted chapter's vector store entry: `pov`, `scene_type`, `characters_present`, `timeline`, `foreshadowing_seeds` — many of these are later queried with hard filters when assembling a revision pass.

## 6345 — RAG with sub-agent dispatch (Metadata Agent → RAG Agent 2)

RAG Agent, RAG Agent 2, Metadata Agent are all separate `agent` nodes; Metadata Agent feeds into RAG Agent 2. **The sub-agent pattern here**: "given a user query, run one cheap call to extract metadata (the Metadata Agent), then pass those as a `where:` filter into a second agent that retrieves over the constrained slice". Importantly this is two separate agents, not one with multiple parser steps. Each agent has its own system prompt, model, and tools.

For "mِنسَج" critique/revision flows: the cheap "intent extractor" Agent (one model, low temp, just decides "what is the user asking for") feeds the "deep agent" (a larger model with access to write-tools). This pattern reduces hallucinated tool calls because the cheap pass narrows the tool list.

## 9934 / 9933 — Recursive Character Text Splitter with multi-format ingestion

Both workflows use this exact trio: `Recursive Character Text Splitter` (parameters: `chunkSize`, `chunkOverlap`, `options.splitCode = 'markdown'`) connected by `ai_textSplitter` to a `Default Data Loader` / `Enhanced Default Data Loader`, which is in turn connected by `ai_document` to a Supabase Vector Store. Insertion goes inside a `splitInBatches` loop so very large documents process one batch at a time without hitting embedding rate limits.

Concrete parameter tuning that worked in these workflows: `chunkSize = 1000`, `chunkOverlap = 200`, `splitCode = 'markdown'`. For Arabic narrative text: increase `chunkSize` to ~1400 chars and `chunkOverlap` to ~250 because Arabic prose tends to use longer paragraph runs. See also user-discussion #173863 for the known issue where chunk overlap can silently fail if `textSplittingMode` on the Default Data Loader is set to "auto" — force `custom` mode and connect the splitter before paginating.

## 6158 / 2446 — Supervisor AI Agent with `toolWorkflow` sub-agents (the multi-agent pattern that maps to microservices)

In 6158: `Supervisor AI Agent1` (agent node) connects via `ai_tool` to `toolWorkflow` nodes for News, Academy, Product AI Agents — these are each a separate workflow exported as a tool. The Supervisor's system prompt instructs "pick the right specialist" and the LangChain Agent runtime calls them.

In 2446: same idea, just two agents (`taskAgent`, `calendarAgent`) plus a `Main Agent` supervisor.

**This is the canonical separation for a microservice-style architecture in n8n**:

- Each sub-agent is a *separate workflow* (can be edited & versioned independently, runs in its own execution context).
- The Supervisor has only the names + descriptions of those tools — never the bodies.
- Sub-agents can be triggered standalone (via ChatTrigger in their own workflow) for dev/testing.

For "مِنسَج": map each phase of the writing engine onto a sub-workflow — `chapter-planner`, `continuity-checker`, `prose-polisher`, `critique-agent`, `lore-extractor` — and have a top-level `StoryArchitect` supervisor call them via `toolWorkflow`. The Supervisor only knows their tool descriptions; their bodies stay isolated and replaceable.

## Architectural synthesis (what to actually build in "مِنسَج")

A **unified master workflow** acting as the engine shell, with five sub-workflows exposed as tools to a `StoryArchitect` supervisor:

1. **Ingestion (workflow 8707 + 9934)**: split the drafted manuscript into markdown chunks (Recursive Splitter, splitCode='markdown', chunkSize 1400, overlap 250), extract metadata via cheap LLM call (`{chapter, scene_type, pov, characters, timeline}`), upsert into Qdrant/Supabase Vector Store.
2. **Retrieval (workflow 5436)**: when the AI Agent requests a Codex lookup, first a `Code` node derives hard metadata filters from the Story Bible active context, then a Supabase Vector Search with the `Metadata Filter` UI of `vectorStoreSupabase` applies them, then a Cohere (or local) reranker trims to top-K before the agent sees results.
3. **Generation (basic LLM Chain + AI Agent with Chat Memory)**: not the highlight, but the agent's system prompt must require output as JSON conforming to your `ChapterState` schema.
4. **Critique Loop (workflow 4316)**: validate the JSON via Code node, route via Switch on schema match, re-prompt with the specific schema error if invalid. Cap retries at 3 per field, not 3 globally.
5. **Sub-workflow Microservices (workflows 6158/2446 pattern)**: each specialist is a separate workflow file invoked via `toolWorkflow` from the Supervisor. Independently versioned, individually runnable, conversation-isolated.

The two endpoints to remember for future iteration:
- Workflow full JSON: `https://api.n8n.io/api/workflows/<id>`
- Forum story for non-published patterns: `https://community.n8n.io/raw/<topic_id>.json` (returns plain-text Discourse markdown, not JSON)
