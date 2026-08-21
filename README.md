<div align="center">

# oneMEM

### One memory. Every AI. You own it.

Local, structured memory for AI agents—in one SQLite file on your machine.

[![PyPI](https://img.shields.io/pypi/v/onemem?label=PyPI&color=6C3AED)](https://pypi.org/project/onemem/)
[![License: MIT](https://img.shields.io/badge/license-MIT-14B8A6)](LICENSE)

</div>

oneMEM gives AI tools a shared local memory. It turns useful context into compact facts and surfaces the minimum amount of memory sufficient for a query. Every connected agent reads and writes the same SQLite file.

```text
AI agents ───┐
Code editors ┼── MCP ── oneMEM ── ~/.onemem/onemem.db
Local tools ─┘
```

## Install

oneMEM requires Python 3.11 or newer and an API key for any supported language-model provider. Embeddings run locally; there is no embedding service or API key to configure.

```console
uv tool install "onemem[all]"
onemem init
```

`onemem init` does the rest:

1. asks which model provider you want to use;
2. recommends a model or lets you enter another model ID;
3. verifies the key and model before saving them;
4. initializes the local database and embedding model;
5. offers background capture; and
6. connects detected AI tools over MCP.

Nothing is uploaded to a oneMEM server. Configuration and credentials stay under `~/.onemem/`; the API key is sent only to the provider you select.

## Try it

Add something directly:

```console
onemem add "Chose SQLite because it needs zero operations and one-file backups."
```

Ask for it later:

```console
onemem ask "What storage did I choose, and why?"
```

Or ask from a connected agent. It receives two MCP tools:

- `onemem_recall` retrieves relevant memory.
- `onemem_log` stores something worth remembering.

## MCP setup

oneMEM works with any client that can run a local `stdio` MCP server, including Claude Code, Codex, Cursor, and Windsurf. `onemem init` automatically configures clients whose command-line tools it detects; other clients only need the `onemem-mcp` executable path.

```console
claude mcp add --scope user onemem -- "$(command -v onemem-mcp)"
codex mcp add onemem -- "$(command -v onemem-mcp)"
```

## Commands

| Command | Purpose |
|---|---|
| `onemem init` | Complete interactive setup |
| `onemem add "memory"` | Store one note or observation |
| `onemem ask "question"` | Retrieve relevant facts and answer a question |
| `onemem watch --start` | Start capturing in the background |
| `onemem doctor` | Check the environment |
| `onemem status` | Show event, fact, entity counts |

## Where data lives

| Path | Contents |
|---|---|
| `~/.onemem/onemem.db` | Events, facts, entities, embeddings |
| `~/.onemem/config.toml` | Active provider, model, and runtime settings |
| `~/.onemem/.env` | Provider API keys |

## How retrieval works

```text
session or imported text
        ↓
append-only raw event
        ↓
compact facts + local embeddings + entity anchors
        ↓
deterministic fusion of semantic, keyword, and entity retrieval
        ↓
minimum relevant memory returned to the agent
```

oneMEM uses an LLM only to interpret and compact language and, optionally, to synthesize the final answer. Storage, indexing, and retrieval are ordinary code.

## Benchmarks

Measured on a 100-instance stratified sample of [LongMemEval-S](https://arxiv.org/abs/2410.10813):

| Metric | Result |
|---|---:|
| Retrieval recall | **0.89** |
| Context reduction | **99.1%** |
| End-to-end answer accuracy | **72%** |

## Development

```console
git clone https://github.com/YOUR_USERNAME/onemem.git
cd onemem
uv sync --all-extras
uv run pytest -q
```

## License

MIT — Based on [Meniscus](https://github.com/magic-bubblez/meniscus) by magic_bubblez.
