<div align="center">

<img src="docs/onemem-logo.png" width="90" alt="oneMEM Logo" />

# oneMEM

### One memory. Every AI. You own it.

Local, structured memory for AI agents — in one SQLite file on your machine.

[![PyPI](https://img.shields.io/pypi/v/onemem?label=PyPI&color=7C3AED&logo=pypi&logoColor=white)](https://pypi.org/project/onemem/)
[![Python](https://img.shields.io/pypi/pyversions/onemem?color=3B82F6&logo=python&logoColor=white)](https://pypi.org/project/onemem/)
[![License: MIT](https://img.shields.io/badge/license-MIT-10B981?logo=open-source-initiative&logoColor=white)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/onemem?color=F97316&logo=pipedown&logoColor=white)](https://pypi.org/project/onemem/)
[![Tests](https://img.shields.io/badge/tests-144%20passing-10B981?logo=pytest&logoColor=white)](https://github.com/shashank-tomar0/onemem)
[![MCP](https://img.shields.io/badge/MCP-compatible-7C3AED?logo=modelcontextprotocol&logoColor=white)](https://modelcontextprotocol.io)
[![Claude](https://img.shields.io/badge/Claude%20Code-ready-EC4899?logo=anthropic&logoColor=white)](https://docs.anthropic.com/en/docs/claude-code)

<br />

**oneMEM** gives AI tools a shared local memory. It distills useful context into
compact atomic facts and surfaces the **minimum memory sufficient for a query**.
Every connected agent reads and writes the same SQLite file.

```text
AI agents ───┐
Code editors ┼── MCP ── oneMEM ── ~/.onemem/onemem.db
Local tools ─┘
```

</div>

---

## ✨ Why oneMEM?

| | |
|---|---|
| 🔒 **Local & private** | One SQLite file. No server, no cloud, no account. Back it up by copying a file. |
| 🧠 **Deterministic retrieval** | No LLM in the read path. Same query → same result, always. Inspectable with SQL. |
| 🔗 **Append-only** | Events are never overwritten. Facts are only ever added. Corrections = new events. |
| 🤖 **MCP-native** | Two tools (`onemem_recall` + `onemem_log`) — works with Claude Code, Codex, Cursor, Windsurf. |
| 🌐 **BYOLLM** | OpenRouter, OpenAI, Anthropic, Gemini, Groq, xAI, Hugging Face, Ollama, or any OpenAI-compatible endpoint. |
| ⚡ **Local embeddings** | `bge-base-en-v1.5` (768-d) runs locally. No embedding API, no extra key, no latency. |

---

## 🚀 Quick Start

Requires **Python 3.11+** and an API key for any LLM provider. Embeddings run locally.

```bash
# Install
uv tool install "onemem[all]"

# Setup (walks you through provider, key, model, capture, MCP wiring)
onemem init

# Try it
onemem add "Chose SQLite because it needs zero operations and one-file backups."
onemem ask "What storage did I choose, and why?"
```

---

## 📐 How oneMEM Works

<div align="center">

![oneMEM Command Flow](docs/command-flow.png)

</div>

oneMEM receives unstructured text (chat turns, notes, imported files), distills it
into **atomic facts**, stores everything **append-only** in one SQLite file, and
makes it retrievable through a **deterministic hybrid search** — no LLM in the
read path. Any MCP-capable agent reads and writes the same memory.

### Write Path

| Step | What happens |
|:----:|---|
| **① Ingest** | Content is chunked, deduplicated by content hash, and stored as raw events |
| **② Extract** | An LLM reads each event and produces atomic facts + named entities |
| **③ Reconcile** | Entities are normalized, deduplicated, and linked to facts via edges |
| **④ Embed** | Each fact is embedded locally with `bge-base-en-v1.5` (768-d vectors) |
| **⑤ Store** | Facts, embeddings, and FTS5 indexes are written to SQLite |

### Read Path (Deterministic — No LLM)

| Step | What happens |
|:----:|---|
| **Query** | User question or agent request |
| **Three doors** | Vector (cosine similarity) + Keyword (FTS5 BM25) + Entity (fact edges) |
| **Fusion** | `fused = 1 − (1−v)(1−f)(1−e)` — magnitude noisy-OR |
| **Adaptive cut** | Keep facts scoring ≥ 50% of the top score, bounded to `[10, limit]` |
| **Source collapse** | If facts cost ≥ raw event tokens, return the raw event instead |

---

## 📋 Commands

| Command | Purpose | Path |
|---|---|---|
| `onemem init` | Interactive setup wizard | — |
| `onemem add "text"` | Store a note directly | ✍️ write |
| `onemem ask "question"` | Retrieve + synthesize an answer | 📖 read |
| `onemem import <path>` | Bulk-import `.txt` / `.md` files | ✍️ write |
| `onemem process` | Process pending events | ✍️ write |
| `onemem watch` | Capture Claude Code / Codex sessions | ✍️ write |
| `onemem watch --start` | Start background capture service | ✍️ write |
| `onemem watch --stop` | Stop background capture service | ✍️ write |
| `onemem status` | Event / fact / entity counts | 📖 read |
| `onemem doctor` | Health check (DB, sqlite-vec, LLM) | 📖 read |
| `onemem list events` | Browse events (`--since`, `--until`, `--source`) | 📖 read |
| `onemem show event N` | Full event detail + extraction provenance | 📖 read |
| `onemem sql "SELECT..."` | Read-only SQL query | 📖 read |
| `onemem tables` | List DB tables with row counts | 📖 read |
| `onemem config set` | Change provider, API key, model | ⚙️ config |
| `onemem config show` | Show active config safely | 📖 read |

---

## 🔌 MCP Setup

oneMEM works with **any MCP client** that supports local `stdio` servers.

```bash
# Claude Code
claude mcp add --scope user onemem -- "$(command -v onemem-mcp)"

# Codex
codex mcp add onemem -- "$(command -v onemem-mcp)"
```

`onemem init` automatically detects and wires Claude Code and Codex during setup.

### MCP Tools

| Tool | Purpose |
|---|---|
| `onemem_recall` | **The ONE read entry point** — topic search, time window, session reconstruction, or raw source lookup |
| `onemem_log` | **Invisible background write** — silently logs conversations. No announcement, no permission, no waiting. |

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

Embeddings always use **`bge-base-en-v1.5`** (768-d) running locally — no API key needed.

---

## 📊 Benchmarks

Measured on a 100-instance stratified sample of [LongMemEval-S](https://arxiv.org/abs/2410.10813):

| Metric | Result |
|---|---:|
| Retrieval recall | **0.89** |
| Context reduction | **99.1%** |
| End-to-end answer accuracy | **72%** |

---

## ⚙️ Configuration

Edit `~/.onemem/config.toml` (or use `onemem config set`):

```toml
[model]
provider = "openrouter"
model = "google/gemini-3.5-flash-lite"

[spend]
max_run_cost_usd = 20.0    # hard ceiling per batch import

[retrieval]
default_limit = 30         # max facts returned per recall
neighbour_max = 20         # neighbour facts gathered around a match

[ingestion]
concurrency = 20           # parallel LLM workers during bulk import
```

### Where data lives

| Path | Contents |
|---|---|
| `~/.onemem/onemem.db` | Events, facts, entities, embeddings — **back this up** |
| `~/.onemem/config.toml` | Active provider, model, runtime settings |
| `~/.onemem/.env` | Provider API keys |

---

## 🛠️ Development

```bash
git clone https://github.com/shashank-tomar0/onemem.git
cd onemem
uv sync --all-extras
uv run pytest -q                    # 144 passing
./scripts/dev-onemem doctor         # run with isolated dev home
```

---

## 📁 Project Structure

```
onemem/
├── cli/                  # Click CLI (init, add, ask, watch, ...)
├── api/                  # FastAPI HTTP API
├── providers/            # LLM + embedding implementations
├── mcp_server.py         # MCP server (onemem_recall + onemem_log)
├── fact_retrieval.py     # Deterministic hybrid search
├── pipeline.py           # Ingest + process orchestration
├── entity_extractor.py   # LLM-based entity + fact extraction
├── schema.sql            # SQLite schema
└── config.py             # All tunable settings
```

---

## 📜 License

MIT — Based on [Meniscus](https://github.com/magic-bubblez/meniscus) by magic_bubblez.

---

<div align="center">

**oneMEM** — Your memory, your machine, your AI.

[Get Started →](#-quick-start) · [Report Bug](https://github.com/shashank-tomar0/onemem/issues) · [View Design](DESIGN.md) · [PyPI](https://pypi.org/project/onemem/)

</div>
