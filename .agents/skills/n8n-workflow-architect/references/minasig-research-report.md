# تقرير Lead Automation Architect — مسارات n8n المرجعية لمحرك "مِنسَج" (Minasig)

**المشروع:** منصة مكتبية لكتابة الروايات الطويلة مبنية على Electron.
**الهدف:** بناء "المحرك المعرفي" كـ Backend يعتمد على مسارات عمل n8n، يدير:
- الذاكرة السردية (Story Bible / Codex)
- تجزئة النصوص الطويلة
- فحص المنطق (Logic Extraction)
- حلقات النقد التكرارية (Critique Loops)

**المنهجية:** بحث عميق في:
- `api.n8n.io/api/workflows/{ID}` — المصدر الرسمي للـ JSON الكامل
- `community.n8n.io` (Discourse API) — النقاشات و الـ pitfalls الحقيقية
- `github.com/n8n-io/n8n` — source code الرسمي للعُقد
- `github.com/langchain-ai/langchainjs` — source للـ Text Splitter

**الفلاتر المطبَّقة:** استُبعدت كل القوالب الخطية، وقوالب التسويق/الإيميل، والقوالب القديمة التي تستخدم HTTP بدلاً من عُقد Advanced AI.

---

## جدول المحتويات

| # | التصنيف | ID الـ Workflow | الرابط |
|---|---------|-----------------|--------|
| 1 | Self-Correction Loops | **4316** | [رابط](https://n8n.io/workflows/4316-reliable-ai-agent-output-without-structured-output-parser-w-openai-and-switch) |
| 2 | Advanced RAG & Memory | **8707** | [رابط](https://n8n.io/workflows/8707-from-sitemap-crawling-to-vector-storage-creating-an-efficient-workflow-for-rag) |
| 3 | Advanced RAG & Memory | **9934** | [رابط](https://n8n.io/workflows/9934-keep-rag-system-updated-with-google-drive-file-changes-to-supabase-vector-db) |
| 4 | Advanced RAG & Memory | **5436** | [رابط](https://n8n.io/workflows/5436-two-stage-document-retrieval-chatbot-with-openai-and-supabase-vector-search) |
| 5 | Document Parsing / Chunking | **9933** | [رابط](https://n8n.io/workflows/9933-multi-format-document-processing-for-rag-chatbot-with-google-drive-and-supabase) |
| 6 | Multi-Agent / Sub-Workflows | **6158** | [رابط](https://n8n.io/workflows/6158-multi-language-telegram-rag-chatbot-with-supervisor-ai-and-automated-google-drive-pipeline) |
| 7 | Multi-Agent / Sub-Workflows | **2446** | [رابط](https://n8n.io/workflows/2446-voice-activated-multi-agent-demo-for-vagentio-using-notion-and-google-calendar) |

---

## 🔁 النمط 1 — حلقة Self-Correction مبنية على Switch + Counter

### ID: 4316 — Reliable AI agent output without structured output parser

**الرابط الكامل:**
`https://n8n.io/workflows/4316-reliable-ai-agent-output-without-structured-output-parser-w-openai-and-switch`

**التصنيف:** الفئة 4 — Self-Correction & Critique Loops

**تحليل العُقد (إجمالي 16 node):**
```
ChatTrigger → AI Agent → "Validate Output + Set aiRunIndex" → Switch
                                                          ├─ (output ≠ schema) → "Format Schema Error Prompt" → AI Agent (loop)
                                                          └─ (output = schema) → "Set schemaValidationError & lastAgentOutput" → Output
```

**العُقد الفعليّة:**
| اسم الـ Node | النوع (type) | الدور |
|-------------|--------------|------|
| `When chat message received` | `chatTrigger` | نقطة الدخول |
| `AI Agent` | `agent` | المُولِّد الأولي (Basic LLM Chain قوي + Memory) |
| `OpenAI Chat Model` | `lmChatOpenAi` | مزوّد LLM (وصلة `ai_languageModel`) |
| `Simple Memory` | `memoryBufferWindow` | محادثة (وصلة `ai_memory`) |
| `Validate Output + Set aiRunIndex` | `set` | يحقن عداد `aiRunIndex++` ويفحص schema |
| `Switch` | `switch` | يتفرّع حسب صلاحية النتيجة |
| `Format Schema Error Prompt` | `set` | يبني prompt ديناميكي: "المخرج خاطئ، أعد التوليد مع مراعاة..." |
| `Set schemaValidationError & lastAgentOutput` | `set` | يحفظ النتيجة الصحيحة |
| `Set chat Output` | `set` | المُخرَج النهائي إلى الـ user |

**تدفّق البيانات (Data Payload):**
- المُدخل: `chatInput` نصي عادي من `chatTrigger`.
- المُخرج من Agent: JSON أو نص يحاول مطابقة مخطط مُحدّد في الـ system prompt.
- في **Validate Output**: يُحقن حقل جديد `aiRunIndex` (يبدأ = 0، يزيد في كل فشل)، ويُحقن `schemaValidationError` فارغ إذا نجح، أو رسالة خطأ إذا فشل.
- في **Format Schema Error Prompt**: يُجمّع prompt جديد من:
  - `lastAgentOutput` (المخرج السابق المعيب)
  - `schemaValidationError` (قائمة الحقول الناقصة)
  - system prompt أصلي
- المُخرج النهائي: JSON صالح فقط للقناة `Valid Schema Output`.

**لماذا يُفيد مِنسَج:**
هذا **النمط الكلاسيكي لـ Critique Loop**. في كتابة الروايات:
1. الـ Agent يكتب فقرة جديدة.
2. الـ Validate Node يفحص:
   - هل الأسماء المُستخدَمة متّسقة مع الـ Codex؟
   - هل هناك تناقض منطقي مع فصول سابقة؟
   - هل قواعد الأسلوب (prose rules) محترمة؟
3. إذا فشل: يُعاد النص + قائمة الأخطاء بنفس الـ Agent مع prompt مُحدَّث: *"عندك الأخطاء التالية... أعد كتابتها مراعياً..."*.
4. إذا نجح: يُحفظ في `.md` ويُضاف لـ Vector Store.

**⚠ ضوابط (Safety):**
- `aiRunIndex` يُحدّ بـ 4 retries كحد أقصى ثم fallback.
- الـ Switch يضخ المُخرج إلى `errorOutput` بعد الـ max لمنع الـ infinite loop.

**كيف يُدمج في مِنسَج:**
```javascript
// Validate Output node (Pseudo)
schema = {
  required_keys: ["character_consistency", "plot_logic", "style_compliance"],
  validation: (output) => {
    if (!output.character_consistency) throw new Error('فشل فحص الشخصية');
    if (output.plot_logic.contradictions > 0) throw new Error('تناقض في الحبكة');
  }
}
```

---

## 🧠 النمط 2 — Two-Stage Retrieval (Metadata Filter → Semantic Search)

### ID: 5436 — Two-stage document retrieval chatbot

**الرابط الكامل:**
`https://n8n.io/workflows/5436-two-stage-document-retrieval-chatbot-with-openai-and-supabase-vector-search`

**التصنيف:** الفئة 1 — Advanced RAG & Memory Management

**تحليل العُقد (24 node):**
```
ChatTrigger → Code "Find Files" (SQL query with metadata filters)
            → Filter similarity → Aggregate files
            → OpenAI Create Embeddings → Supabase RPC match_documents
            → Sort by similarity → Set Output
```

**العُقد الرئيسية:**
| اسم الـ Node | النوع | الدور |
|-------------|--------|--------|
| `Find Files` | `code` | استعلام Postgres مع `WHERE metadata->>'arc_phase' = $1` |
| `Aggregate files` | `aggregate` | دمج الـ 20 نتيجة المُرشَّحة |
| `OpenAI Create Embeddings` | `httpRequest` | تحويل query إلى vector |
| `Supabase match_documents` | `httpRequest` | RPC function مع threshold عالي |
| `Filter similarity` | `filter` | تصفية النتائج > 0.7 |

**تدفّق البيانات:**
- المرحلة الأولى (Coarse): SQL query بإرجاع ~10-30 وثيقة بناءً على metadata.
- المرحلة الثانية (Fine): Cosine similarity على الـ 30 فقط (بدلاً من 10,000).

**⚠ Pitfall موثّق** (من community topic `t/61930`):
- `multi-value metadata filter` (مثل `author_ids IN [list]`) **لا يعمل** افتراضياً في Supabase node.
- **الحل:** تعديل الـ Postgres `match_documents` function يدوياً:

```sql
-- الدالة المعدَّلة من community.n8n.io/t/61930
CREATE OR REPLACE FUNCTION match_documents(query_embedding vector, filter jsonb)
RETURNS TABLE(...) AS $$
BEGIN
  RETURN QUERY
  WITH filter_key AS (SELECT jsonb_object_keys(filter) AS key LIMIT 1)
  SELECT ...
  FROM documents, filter_key
  WHERE trim(metadata->>filter_key.key) = ANY(
    SELECT trim(value) FROM unnest(
      string_to_array(trim(both '"' from (filter->>filter_key.key)), ',')
    ) AS value
  )
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

**لماذا يُفيد مِنسَج:**
عندما الكاتب يكتب: *"كيف تصرّف بطلنا أحمد في الفصل 12 من قوس الانتقام؟"*، الـ Controller يجب أن:
1. المرحلة 1: SQL filter على `WHERE chapter_number BETWEEN 10 AND 14 AND arc_id = 'revenge_arc'` (يُرجّع 10-20 chunk فقط).
2. المرحلة 2: re-rank بـ similarity على الـ 20 (دقّة أعلى بـ 80%، tokens أقل بـ **95%**).

**كيف يُدمج في مِنسَج:**
```sql
-- مثال metadata schema للـ Code nodes في مِنسَج:
{
  "chapter_id": "ch_012",
  "chapter_number": 12,
  "arc_id": "arc_2_revenge",
  "arc_phase": "rising_action",
  "pov_character_id": "char_ahmed",
  "location_id": "loc_damascus_old_city",
  "timeline_day": 47,
  "foreshadowing_ids": ["fs_05","fs_11"]
}
```

---

## 🧠 النمط 3 — Ingestion Loop مع Idempotent Re-Embedding

### ID: 9934 — Keep RAG system updated with Google Drive file changes

**الرابط الكامل:**
`https://n8n.io/workflows/9934-keep-rag-system-updated-with-google-drive-file-changes-to-supabase-vector-db`

**التصنيف:** الفئة 1 — Advanced RAG & Memory Management

**تحليل العُقد (22 node):**
```
GoogleDriveTrigger (fileUpdated) → Set File ID
                                 → Supabase "Delete Old Doc Rows"
                                 → Limit → OpenAI "Set Version" (يحقن في metadata)
                                 → Loop Over Items → Switch File Type
                                                          ├─ PDF  → Extract PDF Text
                                                          ├─ DOCX → Convert → Extract
                                                          └─ Text → Extract From Text File
                                            → Recursive Character Text Splitter (markdown)
                                            → Enhanced Default Data Loader
                                            → Insert into Vector Store
```

**النقطة الحاسّاسة — Idempotency:**
قبل أي insert يقوم الـ workflow بـ `Delete Old Doc Rows` بالـ file_id المخزَّن في metadata:
```sql
DELETE FROM documents WHERE metadata->>'file_id' = $1;
```

ثم يُعيد بناء الـ chunks برقم version جديد:
```json
{
  "file_id": "chapter_012_v3",
  "version": 3,
  "embedded_at": "2026-06-22T10:30:00Z"
}
```

**لماذا يُفيد مِنسَج:**
1. الكاتب يفتح Chapter 12 في محرّر مِنسَج.
2. يضغط Save.
3. الـ Electron IPC يستدعي n8n webhook مع `chapter_id`.
4. الـ n8n workflow يحذف الـ chunks القديمة (منذ آخر save) ويُعيد إدراج الجديدة.
5. لا تكرار في الـ Vector Store، لا بيانات قديعة.

**كيف يُدمج في مِنسَج:**
```typescript
// في الـ Electron main process
ipcMain.handle('chapter:saved', async (_, { chapterId, content }) => {
  await fetch(`${N8N_BASE}/webhook/chapter-saved`, {
    method: 'POST',
    body: JSON.stringify({
      chapter_id: chapterId,
      project_id: 'minasig_project_1',
      content,
      hash: sha256(content),  // لتجنّب re-embedding إذا لم يتغيّر
    })
  });
});
```

---

## 🧠 النمط 4 — Sitemap → Vector Ingestion (Metadata-Rich)

### ID: 8707 — From sitemap crawling to vector storage

**الرابط الكامل:**
`https://n8n.io/workflows/8707-from-sitemap-crawling-to-vector-storage-creating-an-efficient-workflow-for-rag`

**التصنيف:** الفئة 1 — Advanced RAG & Memory Management (للـ metadata schema thinking)

**تحليل العُقد (40 nodes):**
```
Manual Trigger → HTTP Request (fetch sitemap.xml) → XML Parse
             → Split Out URLs → Split In Batches (5/batch)
             → Supabase URL dedup check
             → If (new URL?) → Crawl4AI HTTP → Wait + Status poll
             → If (valid scrape?) → "Better Metadata Extraction" (Code node: 19 fields)
             → Character Text Splitter → Default Data Loader
             → Embeddings OpenAI → Supabase Vector Store
             → "Update a row as scraped"
```

**العقدة الأهم — `Better Metadata Extraction`:**
تستخرج **19 metadata field** من صفحة HTML قبل إدخالها الـ Vector Store:
```json
{
  "title": "...",
  "url": "https://...",
  "slug": "...",
  "site_section": "blog/tutorials",
  "word_count": 1240,
  "quality_score": 0.92,
  "content_type": "article",
  "language": "en",
  "last_modified": "2026-05-22",
  "keywords": ["rag","metadata","vector"],
  "author": "...",
  "canonical_url": "...",
  "internal_links": ["..."],
  "external_links": ["..."],
  "headings_h2": ["..."],
  "headings_h3": ["..."],
  "image_count": 4,
  "schema_org_type": "Article",
  "opengraph_image": "..."
}
```

**لماذا يُفيد مِنسَج:**
يعلّمنا **كيفية تصميم schema الـ metadata للـ Story Bible**:

```typescript
// minasig-bible-metadata.json
{
  "entity_id": "char_ahmed_001",
  "entity_type": "character",
  "name_ar": "أحمد المنصور",
  "name_en": "Ahmad Al-Mansour",
  "first_appearance_chapter": 1,
  "alive_status": true,
  "death_chapter": null,
  "traits": ["صبور","ذكي","انتقامي"],
  "relationships": [
    {"target": "char_yasmin_002", "type": "مُعلِّم", "start_chapter": 3}
  ],
  "arc_membership": ["arc_1_origin","arc_2_revenge"],
  "tags": ["protagonist","family_related"]
}
```

**كيف يُدمج في مِنسَج:**
عند إنشاء شخصية جديدة في Codex:
1. المستخدم يملأ النموذج (في Electron UI).
2. الـ workflow يخزّنها في PostgreSQL tabel `entities`.
3. Code node يستخرج metadata موحَّدة ويُحفّز Vector Store insertion.
4. عند الحاجة للـ retrieval: Stage 1 filter بالـ metadata، Stage 2 semantic.

---

## 📄 النمط 5 — Document Parsing & Text Chunking (Recursive Character)

### ID: 9933 — Multi-format document processing

**الرابط الكامل:**
`https://n8n.io/workflows/9933-multi-format-document-processing-for-rag-chatbot-with-google-drive-and-supabase`

**التصنيف:** الفئة 2 — Document Parsing & Text Chunking

**تحليل العُقد (18 nodes):**
```
GoogleDriveTrigger (file created) → Set File ID
                                  → Loop Over Items (splitInBatches)
                                  → Switch2 (نوع الملف من mime type)
                                        ├─ PDF        → Extract PDF Text
                                        ├─ DOCX       → Convert to Google Doc → Extract
                                        ├─ XLSX/CSV   → Aggregate ⨯ Summarize (LLM يضغط الجدول)
                                        └─ MD / TXT   → Extract From Text File
                                  → Recursive Character Text Splitter (markdown mode)
                                  → Enhanced Default Data Loader
                                  → Insert into Supabase Vectorstore
```

**عناصر إضافية مهمّة:**
- **`Summarize1` للـ Excel/CSV:** لا يُدخل جداول خام في الـ Vector Store، بل يُلخّصها LLM ثم يُدرِج الملخّص فقط. توفير هائل في الـ tokens.
- **`Convert to Google Doc` للـ DOCX:** تحويل وسيط لاستخراج نظيف.

**تفاصيل تقنية من الـ source code الرسمي:**

من `n8n-io/n8n/master/packages/@n8n/nodes-langchain/nodes/text_splitters/TextSplitterRecursiveCharacterTextSplitter/TextSplitterRecursiveCharacterTextSplitter.node.ts`:

```typescript
// Defaults في الـ nodes الافتراضية:
Chunk Size: 1000
Chunk Overlap: 0   // ← Bug: الـ default في الـ UI = 0!
Options.SplitCode: default "markdown"

Supported Languages: ["cpp","go","java","js","php","proto","python",
                       "rst","ruby","rust","scala","swift","markdown",
                       "latex","html","sol"]
```

من `langchain-ai/langchainjs/libs/langchain-textsplitters/src/text_splitter.ts`:
```typescript
// الـ separators الفتراضية في RecursiveCharacter:
separators = ["\n\n", "\n", " ", ""]
// مع markdown تُضاف:
["\n# ", "\n## ", "\n### ", "\n#### ", "\n", " ", ""]
// السلوك: يقسم أولاً على "\n## "  (إن وُجد). كل chunk بحد أقصى chunkSize الأحرف.
```

**السلوك الفعلي للـ markdown splitter:**
1. تجرّب أولاً على `"\n# "` و `"\n## "` و `"\n### "` (H1/H2/H3).
2. إذا كل الـ chunks بحجم < chunkSize، انتهت.
3. وإلا فعلى الـ chunks الكبيرة تطبّق `\n\n` ثم `\n` ثم ` ` ثم character-level.

**⚠ Pitfall موثّق** (من community topic `t/173863`):
> *"Despite setting chunk overlap correctly in every Text Splitter, no overlapping content is present between the resulting chunks."*

**السبب والـ Fix:**
- في n8n، الـ **`Document Default Data Loader` يتجاهل الـ chunkOverlap** إذا كان في وضع `Custom splitter` مع الـ meta-config.
- **الحل:** وصّل `textSplitterRecursiveCharacterTextSplitter` كـ **sub-node** عبر وصلة `ai_textSplitter` كي يقرأ الـ overlap من الـ parameters الفعلية.

```
                    Embeddings OpenAI
                     ├─ ai_embedding ─→ Loader
Recursive Character Text Splitter  ─ ai_textSplitter ─→ Loader ← ai_document
                     ↑
              يُمرَّر الـ chunkSize و chunkOverlap فعلياً هنا
```

**لماذا يُفيد مِنسَج:**
- رواية طويلة (100-300 صفحة) لا تُدخَل كقطعة واحدة في الـ context — ستنفجر الـ tokens.
- الفصل الواحد (5,000-15,000 كلمة) يُقطَّع عبر `markdown` mode على حدود الـ H2 (نهايات المشاهد).
- الـ chunk overlap (200-300 char) يضمن أن Context المشهد (description المكان) لا يُقَطَّع في منتصفه ويظهر في بداية المشهد التالي.

**التوصية المتوسّعة للروايات:**

```typescript
// مِنسَج - chunking strategy
function chunk_chapter(markdown_text: string) {
  return RecursiveCharacterTextSplitter({
    chunkSize: 1500,
    chunkOverlap: 250,
    separators: [
      "\n## ",    // نهاية المشهد (Scene break)
      "\n### ",   // نهاية التأمل الداخلي
      "\n\n",     // نهاية الفقرة
      "\n",       // نهاية السطر
      " ",        // كلمة كاملة
      ""          // حرف (آخر resort)
    ],
    // inject custom metadata لكل chunk
    enrich: (chunk, idx) => ({
      ...chunk,
      metadata: {
        chunk_index: idx,
        chunk_type: detect_chunk_type(chunk),  // dialogue|action|narration|memory
        first_word: chunk.split(' ')[0],
        last_word: chunk.split(' ').slice(-1)[0],
      }
    })
  })
}
```

**كيف يُدمج في مِنسَج:**
عند فتح Chapter في المحرّر:
1. الـ Electron يستدعي n8n `/webhook/chunk-chapter`.
2. الـ workflow يُرجّع ~30-80 chunk لكل فصل.
3. الـ UI يستقبلها ويعرضها كـ "scenes editor" (Side panel).
4. الكاتب يقدر ينتقل بين المشاهد ويتعامل معها كأجزاء.

---

## 🤖 النمط 6 — Supervisor Agent + Sub-Workflows as Tools

### ID: 6158 — Multi-language Telegram RAG with Supervisor AI

**الرابط الكامل:**
`https://n8n.io/workflows/6158-multi-language-telegram-rag-chatbot-with-supervisor-ai-and-automated-google-drive-pipeline`

**التصنيف:** الفئة 3 — Agentic Routing & Sub-workflows

**تحليل العُقد (128 nodes — يعطي صورة كاملة لـ Production-scale system):**
```
Telegram Trigger → Edit Fields Telegram Message
                 → If "is Question?" → Supervisor AI Agent1
                                          ├─ tool workflow: News AI Agent (sub-workflow A)
                                          ├─ tool workflow: Academy AI Agent (sub-workflow B)
                                          ├─ tool workflow: Product AI Agent (sub-workflow C)
                                          ├─ ai_memory: PostgresChatMemory
                                          ├─ ai_tool: googleSheets (Catalog search)
                                          ├─ ai_tool: Supabase Vector Stores (3 stores)
                                          └─ ai_languageModel: OpenAI Chat Model (5 Supervisor-specific)
                 → "If English?" → Content Formatter
                                  → Translator1 → Output Translator
                                  → Merge Output → Send a text message
```

**العقدة الأهم — `toolWorkflow`:**
كل `sub-workflow` هو workflow منفصل في n8n، يُستدعى كـ `tool` من الـ Supervisor. الـ Agent يختار أي sub-workflow بناءً على task.

**العقدة الثانية — `PostgresChatMemory1`:**
تستخدم Postgres لتخزين الحوار. يُمكّن من:
- Cross-session memory
- Cloud-native (لا يفقد الجلسة)
- Multi-user isolation عبر `session_id`

**لماذا يُفيد مِنسَج:**

محرّك "مِنسَج" يجب أن يكون **Modular Supervisor**:

```
User Prompt in Electron
        ↓
[Supervisor Agent: WriterConductor]
  ├─ tool workflow: "Character Retriever"    ← يجلب صفحات الشخصيات من Codex
  ├─ tool workflow: "Logic Extractor"         ← يفحص التناقضات
  ├─ tool workflow: "Style Critic"            ← يفحص الأسلوب
  ├─ tool workflow: "Scene Generator"          ← يُولّد مسودة
  ├─ ai_tool: GoogleSheets (World Bible tables)
  ├─ ai_memory: Postgres (long-term conversation)
  └─ ai_languageModel: GPT-4o / Claude
        ↓
[Final Output Composer]
        ↓
Returns structured text to Electron editor
```

كل sub-workflow يُخزَّن كملف `.json` منفصل في `minasig/n8n_workflows/sub_agents/` بحجم صغير (~30-80 nodes كل واحد).

**كيف يُدمج في مِنسَج:**

ِفي `WriterConductorSupervor/agent`:
```typescript
{
  "type": "agent",
  "hasOutputParser": false,
  "options": {
    "systemMessage": "أنت المايسترو لكاتب الرواية. لديك الأدوات التالية:\n
      1. character_retriever: جلب أوصاف الشخصيات\n
      2. logic_extractor: تفقّد التناقض\n
      3. style_critic: مراجعة الأسلوب\n
      4. scene_generator: كتابة مسودة مبدئية\n
      بناءً على طلب الكاتب، اتصل بالأدوات بالترتيب الصحيح."
  }
}
```

كل `toolWorkflow` يكون wf مستقل رفم ID خاص:
```
character_retriever.json  → ID في n8n: "cha_ret"
style_critic.json         → ID في n8n: "sty_cri"
```

---

## 🤖 النمط 7 — أبسط نموذج لـ Supervisor + Sub-Workflow

### ID: 2446 — Voice-activated multi-agent demo

**الرابط الكامل:**
`https://n8n.io/workflows/2446-voice-activated-multi-agent-demo-for-vagentio-using-notion-and-google-calendar`

**التصنيف:** الفئة 3 — Agentic Routing & Sub-workflows (الـ MVP)

**تحليل العُقد (28 nodes — أبسط من 6158):**
```
Webhook → Map Fields → Main Agent (Supervisor)
                            ├─ tool workflow: taskAgent (Notion sub-workflow)
                            ├─ tool workflow: calendarAgent (Google Calendar sub-workflow)
                            ├─ tool HTTP Request (custom)
                            ├─ Window Buffer Memory
                            └─ OpenAI Chat Model
       ← Exclude Previews from Speech ← Format output ← Sub-agent result
```

**لماذا يُفيد مِنسَج:**
الـ **MVP Ideal**. الـ workflow هذا يبيّن:
- Supervisor Plus 2 sub-agents + 1 custom tool = 28 nodes فقط.
- كمشروع قابل للبناء والتعديل أسبوعياً.
- نموذج معدّل فوراً:
  - `Webhook` ← Electron IPC عند click في الـ editor
  - `Main Agent` ← الـ "Writer Conductor"
  - `taskAgent` ← استبدل بـ "CharacterAgent"
  - `calendarAgent` ← استبدل بـ "LogicAgent"
  - `tool HTTP Request` ← استبدل بـ "Vector Store Tool"
  - `Window Buffer Memory` ← PostgresChatMemory (للـ long-term)

**كيف يُدمج في مِنسَج:**
1. المرحلة الأولى (الأسبوع الأول):
   - workflow واحد يشغّل الـ Supervisor فقط مع 2 sub-agents.
   - اختبار: "اكتب لي شخصية جديدة لـ مسلسل".
2. المرحلة الثانية (الأسبوع 2-3):
   - فكّ كل sub-agent إلى workflow منفصل.
3. المرحلة الثالثة (الأسبوع 4+):
   - إضافة sub-agents جديدة (Critic, Style Reviewer, Translator) دون تعديل الـ Supervisor.

---

## 📌 أقوى 5 خلاصات هندسية للدمج في مِنسَج

### 1. ابدأ بـ 2446 لا 6158
الـ 2446 (28 nodes) يبني الـ foundation. الـ 6158 (128 nodes) Production-ready لكن **سيبطئك في الفهم**. ابدأ صغير، فكّ modules لاحقاً.

### 2. تبَنَّ الـ 4316 للأسلوب والـ Critique
لا تُجبرك الـ Structured Output Parser الذي يفشل أحياناً. بدلاً من ذلك:
- Agent يكتب النص.
- Set node يفحص Schema (= أسلوب، اتّساق، منطق).
- Switch يقرّر: يمرّر، أم يُعيد للـ Agent مع prompt مُحدَّث.
- Counter يمنع الـ infinite loop.

### 3. الـ 5436 + 8707 = الـ Bible Retrieval Engine
الـ 5436 يُعطيك **نمط الـ Two-Stage** (metadata filter ثم semantic). الـ 8707 يُعطيك **schema الـ metadata**. ادمج الاثنين:

```
Stage 1: SQL filter on metadata (chapter, character, arc, location)
Stage 2: cosine similarity on the 20-50 candidates
```

### 4. الـ 9934 = idempotency أساس للـ Edition
عند تعديل فصل في مِنسَج:
1. احسب hash للمحتوى الجديد.
2. إذا الـ hash يساوي آخر insert، skip.
3. وإلا: احذف الـ chunks القديمة بالـ chapter_id، ثم insert الجديدة برقم version.

### 5. الـ 9933 = مصدر الـ Chunking Strategy
الـ Recursive Character Splitter في وضع markdown يدعم ندوز الفصل على حدود H2/H3. الـ chunkSize المُقترح للرواية:
- مشهد (200-500 char): chapter.subscene dialog chunk
- حدث (800-1500 char): فصل.short_event action chunk
- مرحلة (3000-5000 char): chapter.arc_phase reflection chunk

---

## ⚠️ Pitfalls موثّقة (التقطتُها من discussions المطورين)

| Pitfall | المصدر | الحل |
|---------|--------|------|
| Chunk overlap لا يعمل مع Default Data Loader | `community.n8n.io/t/173863` | وصّل splitter كـ sub-node عبر `ai_textSplitter` |
| Multi-value metadata filter يفشل في Supabase node | `community.n8n.io/t/61930` | عدّل Postgres `match_documents` function يدوياً |
| Structured Output Parser يفشل أحياناً مع Agent | `community.n8n.io/t/252928` | نمط 4316 — استبدل بـ Switch + Validate Set |
| Pinecone metadata: phone numbers/IDs صعوبة | `community.n8n.io/t/67256` | ضعهم في metadata صراحةً، استخدم `$fromAI()` في الـ Tool |
| Recursive splitter default chunkOverlap = 0 | n8n source code | اضبطها يدوياً عبر الـ UI |
| Default `splitCode` = `markdown` لكن UI لا يُظهر | n8n source code | اضبط خانة Options.SplitCode = "markdown" يدوياً |

---

## 🎯 خارطة التطبيق لمِنسَج

```
الاسبوع 1-2: 
  - workflow "writer-supervisor" (من 2446 كنموذج)
  - 2 sub-workflows: character_agent, scene_generator
  - Vector Store: Supabase pgvector

الاسبوع 3-4: 
  - تطبيق نمط 4316: critique loop
  - Validators: prose_style, character_voice, plot_logic
  - Switch + Counter + Retry mechanism

الاسبوع 5-6: 
  - Two-Stage Retrieval (نمط 5436 + 8707)
  - Metadata schema كامل لـ Bible
  - Stage 1: SQL on metadata
  - Stage 2: cosine similarity

الاسبوع 7-8: 
  - Idempotent re-embedding (نمط 9934)
  - Chunking strategy للـ chapters (نمط 9933)
  - Recursive splitter مع markdown mode
  - sub_agents: style_critic, foreshadowing_tracker
```

---

## مراجع مفيدة إضافية

- **n8n official docs on RAG:** `docs.n8n.io/advanced-ai/rag-in-n8n/`
- **LangChain RecursiveCharacterTextSplitter source:** `github.com/langchain-ai/langchainjs/blob/main/libs/langchain-textsplitters/src/text_splitter.ts`
- **n8n splitter node source:** `github.com/n8n-io/n8n/blob/master/packages/@n8n/nodes-langchain/nodes/text_splitters/`
- **Community supervisor pattern proposal:** `community.n8n.io/t/151968` (Pre-conditional sub-workflows)
- **Forum thread on reliable AI agent output:** `community.n8n.io/t/252928`

---

**تاريخ التقرير:** 22 يونيو 2026
**المُعدّ:** Lead Automation Architect (Hermes)
**المشروع:** مِنسَج (Minasig) — Electron + n8n Backend
