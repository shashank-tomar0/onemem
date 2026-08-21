<div align="center">

<img src="docs/onemem-logo.png" width="100" alt="oneMEM Logo" />

# oneMEM

### One memory. Every AI. You own it.

Local, structured memory for AI agents — in one SQLite file on your machine.

[![PyPI](https://img.shields.io/pypi/v/onemem?label=PyPI&color=6C3AED&logo=pypi&logoColor=white)](https://pypi.org/project/onemem/)
[![Python](https://img.shields.io/pypi/pyversions/onemem?color=4DA6FF&logo=python&logoColor=white)](https://pypi.org/project/onemem/)
[![License: MIT](https://img.shields.io/badge/license-MIT-14B8A6?logo=open-source-initiative&logoColor=white)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/onemem?color=FF994D&logo=pipedown&logoColor=white)](https://pypi.org/project/onemem/)
[![Tests](https://img.shields.io/badge/tests-144%20passing-4DFF88?logo=pytest&logoColor=white)](https://github.com/shashank-tomar0/onemem)
[![MCP](https://img.shields.io/badge/MCP-compatible-a64dff?logo=modelcontextprotocol&logoColor=white)](https://modelcontextprotocol.io)
[![Claude](https://img.shields.io/badge/Claude%20Code-ready-ff4da6?logo=anthropic&logoColor=white)](https://docs.anthropic.com/en/docs/claude-code)

<br />

**oneMEM** gives AI tools a shared local memory. It distills useful context into
compact atomic facts and surfaces the **minimum amount of memory sufficient for a
query**. Every connected agent reads and writes the same SQLite file.

```text
AI agents ───┐
Code editors ┼── MCP ── oneMEM ── ~/.onemem/onemem.db
Local tools ─┘
```

</div>

---

## ✨ Why oneMEM?

| | What makes it different |
|---|---|
| 🔒 **Local & private** | One SQLite file on your machine. No server, no cloud, no account. Back it up by copying a file. |
| 🧠 **Deterministic retrieval** | No LLM in the read path. Same query → same result, always. Every ranking decision is inspectable with SQL. |
| 🔗 **Append-only** | Raw events are never overwritten. Facts are only ever added. Corrections mean new events, never mutations. |
| 🤖 **MCP-native** | Exactly two tools (`onemem_recall` + `onemem_log`) — minimal surface for AI agents. Works with Claude Code, Codex, Cursor, Windsurf. |
| 🌐 **BYOLLM** | Bring your own key. Works with OpenRouter, OpenAI, Anthropic, Gemini, Groq, xAI, Hugging Face, Ollama, or any OpenAI-compatible endpoint. |
| ⚡ **Local embeddings** | `bge-base-en-v1.5` (768-d) runs locally. No embedding API, no extra key, no latency. |

---

## 🚀 Quick Start

### Install

Requires **Python 3.11+** and an API key for any supported LLM provider. Embeddings run locally — no extra setup.

```bash
uv tool install "onemem[all]"
```

### Setup

```bash
onemem init
```

`onemem init` walks you through everything:

| Step | What happens |
|:----:|---|
| **1** | Choose your LLM provider + API key + model |
| **2** | Health check: SQLite, sqlite-vec, LLM connectivity |
| **3** | Install background capture (Claude Code / Codex sessions) |
| **4** | Wire MCP into detected AI tools |

### Try it

```bash
# Add something to memory
onemem add "Chose SQLite because it needs zero operations and one-file backups."

# Ask about it later
onemem ask "What storage did I choose, and why?"
```

---

## 📐 Architecture

```mermaid
graph TB
    subgraph "Inputs"
        CLI["🖥️ CLI<br/>onemem &lt;command&gt;"]
        MCP["🤖 MCP Server<br/>onemem-mcp"]
        API["🌐 HTTP API<br/>FastAPI /events"]
        WATCH["👁️ Watch<br/>Claude Code / Codex"]
    end

    subgraph "Write Path"
        INTAKE["① ingest_event()<br/>chunk → dedup → store"]
        EXTRACT["② extract_entities()<br/>LLM → facts + entities"]
        RECONCILE["③ reconcile + store<br/>entities → edges → facts"]
        EMBED_W["④ embed_facts()<br/>bge-base 768-d local"]
    end

    subgraph "SQLite — ~/.onemem/onemem.db"
        EVENTS[("events<br/>raw content")]
        FACTS[("facts<br/>atomic claims")]
        ENTITIES[("entities<br/>named things")]
        EDGES[("fact_entity_edges")]
        EMBED[("fact_embeddings<br/>sqlite-vec")]
        FTS[("facts_fts<br/>FTS5 keyword")]
    end

    subgraph "Read Path"
        PARAMS["① LLM param extraction<br/>question → topic + dates"]
        RETRIEVE["② Deterministic Retrieval"]
        VECTOR["Vector<br/>cosine sim"]
        KEYWORD["Keyword<br/>BM25 FTS5"]
        ENTITY_D["Entity<br/>fact edges"]
        FUSION["Fusion<br/>noisy-OR"]
        CUT["③ Adaptive Cut<br/>score-curve ratio"]
        SYNTH["④ LLM Synthesis<br/>(optional)"]
    end

    CLI --> INTAKE
    MCP --> INTAKE
    API --> INTAKE
    WATCH --> INTAKE

    INTAKE --> EVENTS
    EXTRACT --> FACTS
    EXTRACT --> ENTITIES
    RECONCILE --> EDGES
    EMBED_W --> EMBED

    EVENTS --> EXTRACT
    FACTS --> FTS

    CLI --> PARAMS
    MCP --> PARAMS

    PARAMS --> RETRIEVE
    RETRIEVE --> VECTOR
    RETRIEVE --> KEYWORD
    RETRIEVE --> ENTITY_D
    VECTOR --> FUSION
    KEYWORD --> FUSION
    ENTITY_D --> FUSION
    FUSION --> CUT
    CUT --> SYNTH

    EMBED --> VECTOR
    FTS --> KEYWORD
    EDGES --> ENTITY_D
```

---

## 🔄 User Flow

```mermaid
flowchart LR
    START([User has a thought])

    subgraph WRITE["✍️ Write"]
        ADD["onemem add<br/>'note'"]
        IMPORT["onemem import<br/>./docs/"]
        WATCH2["onemem watch<br/>(background)"]
        MCP_LOG["onemem_log<br/>(invisible)"]
    end

    subgraph PROCESS["⚙️ Process"]
        LLM_EXTRACT["LLM distills<br/>facts + entities"]
        LOCAL_EMBED["Local embedding<br/>768-d vectors"]
    end

    subgraph STORE["📦 Store"]
        SQLITE[("SQLite<br/>events → facts<br/>→ embeddings")]
    end

    subgraph READ["📖 Read"]
        ASK["onemem ask<br/>'question'"]
        MCP_RECALL["onemem_recall<br/>(AI agent)"]
        SQL["onemem sql<br/>'SELECT...'"]
    end

    START --> WRITE
    WRITE --> PROCESS
    PROCESS --> STORE
    STORE --> READ
    READ --> ANSWER([User gets answer])

    style WRITE fill:#1a2e1a,stroke:#4dff88,color:#fff
    style PROCESS fill:#1a2e1a,stroke:#4dff88,color:#fff
    style STORE fill:#2d2d1f,stroke:#ffd64d,color:#fff
    style READ fill:#1a2a3d,stroke:#4da6ff,color:#fff
```

---

## ⚡ All Commands — Visual Reference

<div align="center">

![oneMEM Command Flow](docs/command-flow.png)

</div>

---

## 📋 Command Reference

### Core Commands

| Command | What it does | Path |
|---|---|---|
| `onemem init` | Interactive setup wizard (provider, key, model, capture, MCP) | write |
| `onemem add "text"` | Store a note or observation directly | write |
| `onemem ask "question"` | Retrieve matching facts + optional LLM synthesis | read |
| `onemem import <path>` | Bulk-import `.txt` / `.md` files (parallel batch) | write |
| `onemem process` | Process all pending events (extract facts) | write |
| `onemem watch` | Capture Claude Code / Codex sessions in real-time | write |
| `onemem watch --start` | Start background capture service | write |
| `onemem watch --stop` | Stop background capture service | write |

### Inspection Commands

| Command | What it does |
|---|---|
| `onemem status` | Event / fact / entity counts + staleness detection |
| `onemem doctor` | Full health check (DB, sqlite-vec, LLM, write path) |
| `onemem list events` | Browse events with `--since`, `--until`, `--source`, `--limit` |
| `onemem show event N` | Full event detail with extraction provenance |
| `onemem sql "SELECT..."` | Read-only SQL query against the memory |
| `onemem tables` | List all DB tables with row counts |

### Configuration Commands

| Command | What it does |
|---|---|
| `onemem config set` | Interactively change provider, API key, and model |
| `onemem config show` | Show active config safely (never exposes full API key) |

### MCP Tools (for AI agents)

| Tool | Purpose |
|---|---|
| `onemem_recall` | **The ONE read entry passpoint** — topic search, time window, session reconstruction, or raw source lookup |
| `onemem_log` | **Invisible background write** — silently logs conversations. No announcement, no permission, no waiting. |

---

## 🔌 MCP Setup

oneMEM works with **any MCP client** that supports local `stdio` servers.

```bash
# Claude Code (recommended)
claude mcp add --scope user onemem -- "$(command -v onemem-mcp)"

# Codex
codex mcp add onemem -- "$(command -v onemem-mcp)"

# Any other MCP client
# command: onemem-mcp
```

`onemem init` automatically detects and wires Claude Code and Codex during setup.

---

## 🗂️ Where Data Lives

| Path | Contents |
|---|---|
| `~/.onemem/onemem.db` | Events, facts, entities, embeddings (one SQLite file — **back this up**) |
| `~/.onemem/config.toml` | Active provider, model, and runtime settings |
| `~/.onemem/.env` | Provider API keys (only the active provider's key is read) |

---

## 🔬 How Retrieval Works

```mermaid
graph TD
    Q["🔍 User Query"]

    subgraph DOORS["Three Retrieval Doors"]
        V["<b>Vector Door</b><br/>cosine similarity<br/>query embedding × fact embedding"]
        K["<b>Keyword Door</b><br/>FTS5 BM25<br/>OR-matched token search"]
        E["<b>Entity Door</b><br/>explicit entity match<br/>via fact_entity_edges"]
    end

    FUSION["<b>Fusion</b><br/>fused = 1 − (1−v)(1−f)(1−e)<br/>magnitude noisy-OR"]
    CUT["<b>Adaptive Cut</b><br/>keep facts ≥ 50% of top score<br/>bounded [10, limit]"]
    COLLAPSE["<b>Source Collapse</b><br/>if facts cost ≥ raw event<br/>return raw event instead"]

    Q --> V
    Q --> K
    Q --> E
    V --> FUSION
    K --> FUSION
    E --> FUSION
    FUSION --> CUT
    CUT --> COLLAPSE

    style V fill:#1a2e2e,stroke:#4dffff,color:#fff
    style K fill:#1a2e2e,stroke:#4dffff,color:#fff
    style E fill:#1a2e2e,stroke:#4dffff,color:#fff
    style FUSION fill:#2d1f4e,stroke:#a64dff,color:#fff
    style CUT fill:#1a2a3d,stroke:#4da6ff,color:#fff
    style COLLAPSE fill:#2d2d1f,stroke:#ffd64d,color:#fff
```

**Key properties:**
- **No LLM in the read path** — retrieval is a fixed formula, always deterministic
- **Adaptive cut** — sharp queries return tight sets; broad queries return more
- **Source collapse** — when distilled facts don't save tokens, the raw event is returned

---

## 📊 Benchmarks

Measured on a 100-instance stratified sample of [LongMemEval-S](https://arxiv.org/abs/2410.10813):

| Metric | Result |
|---|---:|
| Retrieval recall | **0.89** |
| Context reduction | **99.1%** |
| End-to-end answer accuracy | **72%** |

---

## 🏗️ Supported Providers

| Provider | Key Env Var | Notes |
|---|---|---|
| [OpenRouter](https://openrouter.ai) | `OPENROUTER_API_KEY` | One key, hundreds of models |
| [OpenAI](https://openai.com) | `OPENAI_API_KEY` | Direct GPT access |
| [Anthropic](https://anthropic.com) | `ANTHROPIC_API_KEY` | Native Claude API |
| [Google Gemini](https://ai.google.dev) | `GEMINI_API_KEY` | Direct Gemini access |
| [Groq](https://groq.com) | `GROQ_API_KEY` | Fast inference, open-weight models |
| [xAI](https://x.ai) | `XAI_API_KEY` | Grok access |
| [Hugging Face](https://huggingface.co) | `HF_TOKEN` | Open-weight models via Inference Providers |
| [Ollama](https://ollama.com) | *no key needed* | Free, runs locally |
| Custom | `base_url` + `api_key_env` | Any OpenAI-compatible endpoint |

Embeddings always use **`bge-base-en-v1.5`** (768-d) running locally. No API key needed.

---

## ⚙️ Configuration

Edit `~/.onemem/config.toml` (or use `onemem config set`):

```toml
[model]
provider = "openrouter"    # see provider table above
model = "google/gemini-3.5-flash-lite"

# Only for provider = "custom":
# base_url = "https://vendor.example/v1"
# api_key_env = "MY_VENDOR_API_KEY"

[spend]
max_run_cost_usd = 20.0    # hard ceiling per batch import

[retrieval]
default_limit = 30         # max facts returned per recall
neighbour_max = 20         # neighbour facts gathered around a match

[ingestion]
concurrency = 20           # parallel LLM workers during bulk import
```

---

## 🛠️ Development

```bash
# Clone
git clone https://github.com/shashank-tomar0/onemem.git
cd onemem

# Install with all extras
uv sync --all-extras

# Run tests (144 passing)
uv run pytest -q

# Run with dev home (isolated from your real memory)
./scripts/dev-onemem doctor
```

---

## 📁 Project Structure

```
onemem/
├── cli/              # Click CLI (init, add, ask, watch, ...)
├── api/              # FastAPI HTTP API
├── providers/        # LLM + embedding implementations
│   ├── openai_compat.py    # OpenAI-compatible endpoints
│   ├── anthropic.py        # Anthropic native API
│   └── local_embedding.py  # bge-base-en-v1.5
├── mcp_server.py     # MCP server (onemem_recall + onemem_log)
├── fact_retrieval.py # Deterministic hybrid search
├── pipeline.py       # Ingest + process orchestration
├── entity_extractor.py  # LLM-based entity + fact extraction
├── schema.sql        # SQLite schema
└── config.py         # All tunable settings
```

---

## 📜 License

MIT — Based on [Meniscus](https://github.com/magic-bubblez/meniscus) by magic_bubblez.

---

<div align="center">

**oneMEM** — Your memory, your machine, your AI.

[Get Started →](#-quick-start) · [Report Bug](https://github.com/shashank-tomar0/onemem/issues) · [View Design](DESIGN.md) · [PyPI](https://pypi.org/project/onemem/)

</div>
