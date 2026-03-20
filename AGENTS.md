# Paper Digest

Research paper digest tool: search arXiv, AI-screen, bilingual (EN/ZH) summarization, MDX generation.

## How to Use

When the user asks to digest, summarize, or review papers on any topic, read and follow the complete workflow in `.claude/commands/paper-digest.md`.

That file is a **self-contained prompt** containing the full workflow: arXiv search, AI screening, PDF reading, bilingual summary generation, and MDX output.

### Example Requests

- "Digest papers about RAG evaluation"
- "Summarize recent papers on multimodal reasoning, max 5"
- "Find and summarize foundational papers on LLM agents"

## Python Script (Alternative)

If the user prefers the Python pipeline:

```bash
source .venv/bin/activate && python main.py "topic" -n 3
```

Requires `.env` with `LLM_API_KEY`. See `.env.example` for configuration.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/commands/paper-digest.md` | Complete agent skill / workflow prompt |
| `main.py` | Python CLI entry point |
| `processed_papers.json` | Reading history (dedup across runs) |
| `output/` | Generated MDX files |
