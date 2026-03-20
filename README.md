<div align="center">
<pre>█▀█ ▄▀█ █▀█ █▀▀ █▀█   █▀▄ █ █▀▀ █▀▀ █▀ ▀█▀
█▀▀ █▀█ █▀▀ ██▄ █▀▄   █▄▀ █ █▄█ ██▄ ▄█  █ </pre>

**Let AI read papers for you — one at a time, from classics to cutting edge.**

[中文](README.zh-CN.md) | English

</div>

---

> **Agent Skill** — Works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex](https://github.com/openai/codex), [OpenCode](https://opencode.ai), [Cursor](https://cursor.sh), [Copilot](https://github.com/features/copilot), and any AI coding agent. Zero dependencies, works out of the box. [See installation →](#install-as-agent-skill)

---

## Why This Tool

Reading papers is hard work. Any research field — LLM agents, multimodal reasoning, RAG, code generation — has hundreds of papers piling up. You want to systematically read through them, but:

- Don't know where to start
- Can't tell which ones are worth reading vs. noise
- Forget the key points after reading
- Switching between Chinese and English is exhausting

This tool solves all of that.

## How It Works

1. **Plan** — LLM generates search queries and determines when the field started
2. **Search** — Query arXiv chronologically, oldest first
3. **Deduplicate** — Skip papers you've already read
4. **AI Screen** — AI judges each paper: worth your time?
5. **Deep Read** — Download full PDF, extract complete text
6. **Summarize** — One paper at a time to LLM for thorough bilingual analysis
7. **Generate** — One MDX file per paper, structured and blog-ready

Run it again tomorrow — it picks up where you left off, never repeats.

## What Makes This Different

- **Chronological reading path** — LLM figures out when the field started, then progresses forward from foundational papers. You build understanding in order, not randomly.
- **AI as your reading filter** — AI screens candidates before committing to a full read. Skips the noise, keeps the signal.
- **One paper, full attention** — No batch summarization. Each paper gets the complete PDF fed to the LLM individually for a thorough, specific summary.
- **Bilingual output** — Every section in both Chinese and English. Not machine-translated — the AI writes each language natively.
- **Incremental & resumable** — History tracking means you can run it daily/weekly and steadily work through the field.
- **Real progress visibility** — Rich terminal UI with spinners and timing for every step. You always know what's happening.

---

## Install as Agent Skill

**No Python, no pip, no API key needed** — the agent does everything natively.

The skill file (`.claude/commands/paper-digest.md`) is a **self-contained prompt** — any agent that reads markdown instructions can use it.

### Claude Code

```bash
# Option A: Clone and use in this project
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest

# Option B: Install globally (works in any project)
mkdir -p ~/.claude/commands
curl -o ~/.claude/commands/paper-digest.md \
  https://raw.githubusercontent.com/PixelCookie-zyf/paper-digest/main/.claude/commands/paper-digest.md
```

Then use:

```
/paper-digest                                   # Default: "LLM Agent"
/paper-digest "multimodal reasoning"            # Any research topic
/paper-digest "RAG evaluation" --max 5          # Read 5 papers
/paper-digest --start-date 2024-01-01           # From a specific date
/paper-digest --no-screen                       # Skip screening, read all
```

### OpenAI Codex CLI

```bash
# Option A: Clone the repo (Codex reads AGENTS.md automatically)
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest
codex "digest papers about RAG evaluation"

# Option B: Use as one-off instructions
curl -O https://raw.githubusercontent.com/PixelCookie-zyf/paper-digest/main/.claude/commands/paper-digest.md
codex -i paper-digest.md "digest papers about RAG evaluation"
```

### OpenCode

```bash
# Clone the repo (OpenCode reads AGENTS.md automatically)
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest
opencode
# Then ask: "digest papers about LLM agents"
```

### Cursor / Copilot / Windsurf / Others

Clone the repo, then copy the skill file to your agent's rules directory:

```bash
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest
```

| Agent | Copy to |
|-------|---------|
| **Cursor** | `cp .claude/commands/paper-digest.md .cursor/rules/paper-digest.md` |
| **GitHub Copilot** | `cp .claude/commands/paper-digest.md .github/copilot-instructions.md` |
| **Windsurf** | `cp .claude/commands/paper-digest.md .windsurf/rules/paper-digest.md` |
| **Gemini CLI** | `cp .claude/commands/paper-digest.md GEMINI.md` |
| **Any LLM** | Use `.claude/commands/paper-digest.md` as system prompt |

### Advanced Options

```
/paper-digest --summarizer api                  # Uses LLM_API_KEY from .env
/paper-digest --mode script                     # Run the full Python pipeline instead
```

| Mode | How it works | Requires |
|------|-------------|----------|
| `native` (default) | The LLM does everything itself | Nothing |
| `script` | Delegates to the Python pipeline (`main.py`) | Python deps + `.env` |

| Summarizer | How it works | Requires |
|------------|-------------|----------|
| `claude` (default) | The LLM writes summaries itself | Nothing |
| `api` | Calls external LLM API | `LLM_API_KEY` in `.env` |

---

## Alternative: Run as Python Script

If you prefer the Python pipeline (supports any OpenAI-compatible LLM API):

### Install

```bash
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env
# Edit .env → add your LLM_API_KEY
```

### Usage

```bash
python main.py                          # Default: "LLM Agent"
python main.py "multimodal reasoning"   # Any topic
python main.py -n 5                     # Read 5 papers
python main.py --pool-size 50           # Search deeper
python main.py --start-date 2024-01-01  # From a specific date
python main.py --no-screen              # Skip screening
python main.py --history                # See what you've read
```

### Configuration (.env)

```env
# Works with: MiniMax, OpenAI, DeepSeek, Qwen, Ollama, etc.
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.minimaxi.com/v1    # Default: MiniMax
LLM_MODEL=MiniMax-M2.7
OUTPUT_DIR=output
```

---

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
├── AGENTS.md                # Agent instructions (Codex, OpenCode, etc.)
├── .claude/commands/        # Skill file (Claude Code slash command)
└── output/                  # Your paper summaries live here
```

## Terminal Output

```
╭──────── Paper Digest ────────╮
│ Query: RAG evaluation        │
│ Model: deepseek-chat         │
│ Pool:  20 candidates         │
│ Goal:  3 papers              │
╰──────────────────────────────╯

  LLM is planning search strategy... (2.1s)
  Covers retrieval-augmented generation, faithfulness, RAGAS benchmark...
  Queries: 4 | From: 2020-05-01

  Searching arXiv...
  Found 18 candidates
  All 18 are new

──────────── Paper 1/18 ────────────
  Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
  2020-05-22 · Patrick Lewis, Ethan Perez...

  PASS (2.8s) Foundational RAG paper
  PDF extracted (6.2s) 41,208 chars
  deepseek-chat is reading and writing summary...
  Summary done (38.5s)
  Saved: output/2026-03-20-retrieval-augmented-generation-for-knowledge.mdx

┌──── Done — 3 paper(s) processed ────┐
│ #  File                              │
│ 1  output/2026-03-20-retrieval-….mdx │
│ 2  output/2026-03-20-self-rag-….mdx  │
│ 3  output/2026-03-20-ragas-aut-….mdx │
└──────────────────────────────────────┘
```

---

<div align="center">

*Built with arXiv API, any LLM you like, and a lot of coffee.*

</div>
