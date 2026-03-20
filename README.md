<div align="center">
<pre>█▀█ ▄▀█ █▀█ █▀▀ █▀█   █▀▄ █ █▀▀ █▀▀ █▀ ▀█▀
█▀▀ █▀█ █▀▀ ██▄ █▀▄   █▄▀ █ █▄█ ██▄ ▄█  █ </pre>

**Let AI read papers for you — one at a time, from classics to cutting edge.**

[中文](README.zh-CN.md) | English

</div>

---

## Why This Tool

Reading papers is hard work. Especially in the LLM Agent space — since ReAct dropped in October 2022, hundreds of papers have piled up. You want to systematically read through them, but:

- Don't know where to start
- Can't tell which ones are worth reading vs. noise
- Forget the key points after reading
- Switching between Chinese and English is exhausting

This tool solves all of that.

## How It Works

```
python main.py
```

That's it. The tool will:

1. **Search** — Query arXiv from the ReAct era (2022-10) onward, oldest first
2. **Deduplicate** — Skip papers you've already read
3. **AI Screen** — AI judges each paper: worth your time?
4. **Deep Read** — Download full PDF, extract complete text
5. **Summarize** — One paper at a time to LLM for thorough bilingual analysis
6. **Generate** — One MDX file per paper, structured and blog-ready

Run it again tomorrow — it picks up where you left off, never repeats.

## What Makes This Different

- **Chronological reading path** — Starts from foundational papers (ReAct, Toolformer...) and progresses forward. You build understanding in order, not randomly.
- **AI as your reading filter** — AI screens candidates before committing to a full read. Skips the noise, keeps the signal.
- **One paper, full attention** — No batch summarization. Each paper gets the complete PDF fed to the LLM individually for a thorough, specific summary.
- **Bilingual output** — Every section in both Chinese and English. Not machine-translated — the AI writes each language natively.
- **Incremental & resumable** — History tracking means you can run it daily/weekly and steadily work through the field.
- **Real progress visibility** — Rich terminal UI with spinners and timing for every step. You always know what's happening.

## Quick Start

```bash
# Install
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env → add your LLM_API_KEY

# Run
python main.py
```

## Usage

```bash
python main.py                          # Default: "LLM Agent" from 2022-10
python main.py "multimodal reasoning"   # Custom topic
python main.py -n 5                     # Read 5 papers this run
python main.py --pool-size 50           # Search deeper
python main.py --start-date 2024-01-01  # Jump to a later period
python main.py --no-screen              # Skip screening, read everything
python main.py --history                # See what you've already read
```

## Use as a Slash Command (for LLM coding tools)

Paper Digest can run as a **slash command** inside [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or any LLM tool that supports `.claude/commands/`.

### Installation

The command file is already included at `.claude/commands/paper-digest.md`. Just open this project in your LLM tool.

For global access (any project), copy it:

```bash
mkdir -p ~/.claude/commands
cp .claude/commands/paper-digest.md ~/.claude/commands/
```

### Slash Command Usage

```
/paper-digest                                   # Default: "LLM Agent", Claude summarizes
/paper-digest "multimodal reasoning"            # Custom topic
/paper-digest --max 5                           # Process 5 papers
/paper-digest --summarizer api              # Use external LLM API instead of Claude
/paper-digest --mode script                     # Use the Python pipeline
/paper-digest --start-date 2024-01-01           # Start from a later date
/paper-digest --no-screen                       # Skip quality screening
```

### Modes

| Mode | How it works | Requires |
|------|-------------|----------|
| `native` (default) | The LLM does everything — search, screen, read PDFs, summarize, write MDX | Nothing extra |
| `script` | Runs the Python pipeline (`main.py`) | Python deps + `LLM_API_KEY` |

### Summarizer

| Option | How it works | Requires |
|--------|-------------|----------|
| `claude` (default) | The LLM generates summaries itself | Nothing extra |
| `api` | Calls external LLM API for summaries | `LLM_API_KEY` in `.env` |

### For other LLMs / Agent frameworks

The command file at `.claude/commands/paper-digest.md` is a self-contained prompt with the full workflow, arXiv query construction, summary schema, and MDX template. You can:

1. Feed it as a system prompt to any LLM
2. Adapt it for other agent frameworks (LangChain, CrewAI, etc.)
3. Use it as a reference spec for building your own paper digest tool

The file contains everything the LLM needs to know — no external documentation required.

---

## Configuration (.env)

```env
LLM_API_KEY=your_key_here           # Required
LLM_BASE_URL=https://api.minimaxi.com/v1    # Default: MiniMax
LLM_MODEL=MiniMax-M2.7
OUTPUT_DIR=output
```

## MDX Output

Each paper gets its own `.mdx` file containing:

| Section              | Description                    |
|----------------------|--------------------------------|
| Paper title          | EN + ZH                        |
| One-line summary     | What it does and why it matters|
| Research problem     | What problem it addresses      |
| Abstract summary     | Motivation, method, results    |
| Core method          | Specific technical approach    |
| Model / framework    | Architecture and components    |
| Datasets             | What data, what scale          |
| Experimental setup   | Baselines, metrics, params     |
| Main results         | Key numbers and findings       |
| Innovations          | What's new                     |
| Limitations          | Shortcomings                   |
| Use cases            | Where to apply                 |
| Key takeaways        | What you should focus on       |
| Keywords             | EN + ZH                        |

Includes frontmatter — drop it straight into your blog.

## Project Structure

```
├── main.py                  # CLI with rich progress UI
├── config/                  # Settings from .env
├── paper_search/            # arXiv provider (extensible)
├── paper_fetch/             # PDF download + full text extraction
├── llm_summary/             # LLM screening + deep summarization
├── mdx_writer/              # Per-paper bilingual MDX generation
├── history.py               # Dedup tracking across runs
├── processed_papers.json    # Auto-generated reading history
└── output/                  # Your paper summaries live here
```

## Terminal Output

```
╭──────── Paper Digest ────────╮
│ Query: LLM Agent             │
│ From:  2022-10-01            │
│ Pool:  20 candidates         │
│ Goal:  3 papers              │
╰──────────────────────────────╯

  Found 20 candidates from arXiv
  All 20 are new

──────────── Paper 1/20 ────────────
  ReAct: Synergizing Reasoning and Acting in Language Models
  2022-10-06 · Shunyu Yao, Jeffrey Zhao, Dian Yu...

  PASS (3.2s) Foundational ReAct framework for LLM agents
  PDF extracted (8.4s) 52,381 chars
  LLM is reading and writing summary...
  Summary done (45.2s)
  Saved: output/2026-03-19-react-synergizing-reasoning-and-acting.mdx

┌──── Done — 3 paper(s) processed ────┐
│ #  File                              │
│ 1  output/2026-03-19-react-….mdx     │
│ 2  output/2026-03-19-toolfo-….mdx    │
│ 3  output/2026-03-19-llm-pl-….mdx    │
└──────────────────────────────────────┘
```

---

<div align="center">

*Built with arXiv API, any LLM you like, and a lot of coffee.*

</div>
