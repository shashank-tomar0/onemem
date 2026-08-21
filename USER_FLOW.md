# oneMEM — Complete User Flow Guide

## Getting Started

oneMEM is your personal, local AI memory — a structured record of everything you
do, learn, decide, and notice over time. It lives in one SQLite file on your machine
and connects to your AI tools via MCP.

### First-Time Setup

```bash
# 1. Install (requires Python 3.11+)
uv tool install "onemem[all]"

# 2. Run the interactive setup
onemem init
```

`onemem init` walks you through 4 steps:

| Step | What it does |
|------|-------------|
| **1. Connect your LLM** | Choose a provider (OpenRouter, OpenAI, Anthropic, Gemini, Groq, xAI, Hugging Face, Ollama, or custom), paste your API key, pick a model |
| **2. Health check** | Verifies SQLite, sqlite-vec, LLM connectivity, and write path |
| **3. Auto-capture** | Installs a background service (macOS launchd / Linux systemd) that silently watches your Claude Code and Codex sessions |
| **4. Wire AI tools** | Detects Claude Code and Codex on your PATH and offers to register the MCP server |

After setup, your memory is ready. Everything stays under `~/.onemem/`:

```
~/.onemem/
├── onemem.db       # Your memory (one SQLite file — back it up by copying it)
├── config.toml     # Active provider, model, and runtime settings
└── .env            # API keys (only the active provider's key is read)
```

---

## Daily Use — The 5-Minute Flow

### 1. Add something to memory

```bash
onemem add "Chose SQLite because it needs zero operations and one-file backups."
```

oneMEM immediately:
- Stores the raw text as an event
- Sends it to your LLM to extract atomic facts and entities
- Embeds the facts locally for semantic search
- Returns how many facts were extracted

You can also pipe text in:

```bash
pbpaste | onemem add              # macOS clipboard
cat notes.md | onemem add         # from a file
echo "Quick thought" | onemem add  # from echo
```

Add a source tag for provenance:

```bash
onemem add --source "standup" "Discussed auth refactor with the team"
```

### 2. Ask your memory a question

```bash
onemem ask "What storage did I choose, and why?"
```

oneMEM:
1. Calls your LLM to convert the question into search parameters (topic + time range)
2. Retrieves matching facts deterministically (vector + keyword + entity search — no LLM)
3. Optionally calls your LLM to synthesize a natural answer from the facts
4. Returns the answer in a warm, conversational voice

**Flags:**
- `--json` — Skip synthesis; return raw structured facts (for piping or AI tools)
- `--limit N` — Cap the number of facts returned

```bash
onemem ask --json "auth decisions"           # raw facts, no synthesis
onemem ask --limit 5 "what did I do today?"  # max 5 facts
```

### 3. Watch your AI sessions (background capture)

If you enabled background capture during `onemem init`, it's already running. Otherwise:

```bash
onemem watch --start        # install and start the background service
onemem watch --stop         # stop and remove the service
```

The watcher silently tails Claude Code and Codex session transcripts, captures your
turns, and queues them for fact extraction in the background.

Manual one-shot capture:

```bash
onemem watch --catch-up --once     # capture existing history, then exit
onemem watch --catch-up --distill  # capture + extract facts (uses your LLM)
```

Continuous watching (foreground):

```bash
onemem watch                        # tail every 3 seconds
onemem watch --interval 10          # tail every 10 seconds
onemem watch --distill              # also extract facts as they arrive
onemem watch --dry-run              # show what would be captured, write nothing
```

### 4. Import files in bulk

```bash
onemem import ./my-notes/           # recursively import all .txt and .md files
onemem import ./project-docs.md     # import a single file
```

Bulk imports use parallel LLM calls (20 workers by default) and include a
**spend gate** that estimates the extraction cost before any API call. If it
exceeds `MAX_RUN_COST_USD` ($20 default), it aborts with an estimate:

```bash
# To override the spend gate:
ONEMEM_ALLOW_LARGE_RUN=1 onemem import ./huge-docs/
```

### 5. Process pending events

If events were captured without a model (or the model was unavailable), they sit
as "pending". Process them when ready:

```bash
onemem process
```

---

## Inspecting Your Memory

### System status

```bash
onemem status
```

Shows event/fact/entity counts, embedding coverage, and how long ago the last
event landed (with a stale-capture warning if > 24h).

### Browse events

```bash
onemem list events                          # latest 20 events
onemem list events --since 2026-01-15       # events from Jan 15 onward
onemem list events --until 2026-01-15       # events up to Jan 15
onemem list events --source cli             # only CLI-added events
onemem list events --limit 50               # show more
```

### Show a specific event

```bash
onemem show event 42
```

Displays the full event content, its entities, and which model extracted its facts
(with prompt version for reproducibility).

### Run raw SQL

```bash
onemem sql "SELECT COUNT(*) FROM facts"
onemem sql "SELECT text FROM facts ORDER BY created_at DESC LIMIT 5"
onemem sql "SELECT canonical_name, COUNT(*) AS cnt FROM entities GROUP BY canonical_name ORDER BY cnt DESC"
onemem tables                              # list all tables with row counts
```

Only read-only queries are allowed (SELECT, PRAGMA, EXPLAIN, WITH).

---

## Configuration

### Check your setup

```bash
onemem doctor
```

Reports: database path, sqlite-vec status, embedding config, LLM provider
connectivity, and a write-path probe (inserts + rolls back a test row).

### Change provider/model

```bash
onemem config set      # interactive: re-pick provider, key, and model
onemem config show     # safe display (never shows the full API key)
```

### Manual config editing

`~/.onemem/config.toml` supports these sections:

```toml
[model]
provider = "openrouter"       # or openai, anthropic, gemini, groq, xai, huggingface, ollama, custom
model = "google/gemini-3.5-flash-lite"

# Only for provider = "custom":
# base_url = "https://vendor.example/v1"
# api_key_env = "MY_VENDOR_API_KEY"

[spend]
max_run_cost_usd = 20.0       # hard ceiling per batch import

[retrieval]
default_limit = 30            # max facts per recall
neighbour_max = 20            # neighbour facts gathered around a match

[ingestion]
concurrency = 20              # parallel LLM workers during bulk import
```

---

## AI Tool Integration (MCP)

oneMEM exposes exactly **two MCP tools** to any connected AI agent:

### `onemem_recall` — the single read entry point

The agent picks the operation by which argument it passes:

| Argument | Operation |
|----------|-----------|
| `query` | Topic/keyword search → matching facts + neighbours |
| `start` / `end` | Time-window filter (combine with query or use alone) |
| `around` | Reconstruct the session around a moment in time |
| `source_event` | Get the raw source text behind a specific fact |

### `onemem_log` — invisible background write

The agent logs every conversation silently — no announcement, no permission
request, no waiting.

### Manual MCP wiring

```bash
# Claude Code
claude mcp add --scope user onemem -- "$(command -v onemem-mcp)"

# Codex
codex mcp add onemem -- "$(command -v onemem-mcp)"

# Any other MCP client
# command: onemem-mcp
```

---

## The `onemem ask` Deep Dive

This is the most powerful command. Here's the full flow:

```
User question
      ↓
LLM converts to search params (topic + time range)
      ↓
Deterministic retrieval (vector + keyword + entity fusion)
      ↓
Adaptive cut (keeps facts scoring ≥ 50% of the top score)
      ↓
Source collapse (returns raw event when facts cost as much)
      ↓
LLM synthesizes a natural answer from the facts
      ↓
Answer in a warm, human voice
```

### What the synthesis LLM is instructed to do:

- Answer from the records only — never invent events, dates, or details
- Read the state of mind behind the question, not just literal content
- Surface patterns and offer grounded perspective
- Preserve the chronological sequence of facts
- Present disagreements across time as shifts, not contradictions
- Say honestly when the memory doesn't hold the answer

---

## Advanced: The Data Pipeline

### Ingestion stages

```
Raw text → Events (chunked, deduped, timestamped)
                ↓
         LLM distillation → Facts (atomic, self-contained claims)
                          → Entities (canonical, normalized, aliased)
                ↓
         Entity reconciliation → fact_entity_edges
                ↓
         Local embedding → fact_embeddings (768-d, sqlite-vec)
                        → facts_fts (FTS5 keyword index)
```

### Retrieval doors

```
Query → Vector door (cosine similarity)
      → Keyword door (FTS5 BM25)
      → Entity door (explicit match)
                ↓
      Fusion: 1 − (1 − W_VECTOR·v) · (1 − W_FTS·f) · (1 − W_ENTITY·e)
                ↓
      Adaptive cut on fused-score curve
                ↓
      Source collapse (raw event when facts don't save tokens)
```

### Append-only design

- Raw events are never overwritten or deleted
- Facts are only ever added
- Every fact traces back to its source event
- Corrections mean adding a new event, never mutating an old one

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `onemem init` | Complete interactive setup |
| `onemem add "text"` | Store one note or observation |
| `onemem ask "question"` | Retrieve facts + optional synthesis |
| `onemem watch` | Capture Claude Code / Codex sessions |
| `onemem watch --start` | Start background capture service |
| `onemem watch --stop` | Stop background capture service |
| `onemem import <path>` | Bulk-import files/directories |
| `onemem process` | Process pending events |
| `onemem doctor` | Check environment health |
| `onemem status` | Event/fact/entity counts |
| `onemem config set` | Change provider/model/key |
| `onemem config show` | Show active config safely |
| `onemem list events` | Browse stored events |
| `onemem show event N` | Full detail for event N |
| `onemem sql "SELECT..."` | Read-only SQL query |
| `onemem tables` | List DB tables with row counts |
| `onemem help` | Usage guide |

---

## Tips for Getting the Most out of oneMEM

1. **Log frequently, log small.** The more you capture, the better retrieval works.
   A quick `onemem add "decided to use X because Y"` is gold for future-you.

2. **Use natural language in `ask`.** The LLM handles time conversion — just say
   "what did I figure out about auth last week?" and it computes the dates.

3. **Check `onemem status` regularly.** If "Last event" shows days ago and you've
   been using AI tools, your background capture may have stopped.

4. **Back up `~/.onemem/onemem.db`.** It's one file. Copy it somewhere safe.

5. **Use `--json` for automation.** `onemem ask --json "topic"` returns structured
   facts you can pipe into other tools or feed to scripts.

6. **Bulk import your notes.** If you have existing markdown notes, docs, or chat
   exports, `onemem import` distills them all in one shot.

7. **Let the MCP tools work invisibly.** The best memory is one you don't have to
   think about. Your AI agents call `onemem_log` in the background and `onemem_recall`
   when they need context — you never see the machinery.
