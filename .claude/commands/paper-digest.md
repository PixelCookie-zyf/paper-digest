---
name: paper-digest
description: "Search arXiv papers, AI-screen, summarize (bilingual), generate MDX"
argument-hint: '[query] [--mode native|script] [--summarizer claude|api] [--max N] [--start-date YYYY-MM-DD] [--no-screen]'
allowed-tools: Bash, Read, Write, Edit, WebFetch, Glob, Grep
---

# Paper Digest

You are a research paper digest assistant. Search arXiv for papers, screen them for quality, generate thorough bilingual (EN/ZH) summaries, and write per-paper MDX files.

## 1. Parse Arguments

Parse `$ARGUMENTS` for these options (all optional):

| Argument | Default | Description |
|----------|---------|-------------|
| `query` (positional) | `LLM Agent` | Search keyword |
| `--mode` | `native` | `native` = you do everything; `script` = run Python pipeline |
| `--summarizer` | `claude` | `claude` = you summarize; `api` = call external LLM API |
| `--max` | `3` | Papers to process this run |
| `--pool-size` | `20` | Candidate pool size |
| `--start-date` | (auto) | Search from this date (default: you decide based on topic) |
| `--no-screen` | false | Skip screening, process all |

Examples:
- `/paper-digest` → query="LLM Agent", native mode, claude summarizer, max 3
- `/paper-digest "RAG evaluation" --max 5` → query="RAG evaluation", 5 papers
- `/paper-digest --mode script` → use Python pipeline
- `/paper-digest --summarizer api` → use external LLM API for summaries

---

## 2. Mode: Script

If `--mode script`, delegate to the Python pipeline:

1. Check that `.venv` exists and dependencies are installed. If not, run:
   ```
   uv venv .venv && source .venv/bin/activate && uv pip install -r requirements.txt
   ```
2. Check that `LLM_API_KEY` is set in `.env`. If not, warn the user.
3. Run:
   ```
   source .venv/bin/activate && python3 main.py "<query>" -n <max> --pool-size <pool_size> --start-date <start_date> [--no-screen]
   ```
4. Report the results.

**Stop here if script mode.**

---

## 3. Mode: Native (default)

You do everything yourself using your tools. Follow these steps in order.

### Step 0: Plan Search Strategy

Before searching, think about the topic and generate a search strategy:

1. **What are the key terms, synonyms, and related concepts?** For example, "RAG evaluation" should also match "retrieval-augmented generation", "faithfulness", "RAGAS", etc.
2. **When did this field start?** Suggest a start date so we begin from foundational papers.
3. **Generate 3-5 arXiv search queries** using arXiv syntax (`abs:`, `ti:`, `AND`, `OR`, quoted phrases).

The first query should target the most canonical/classic papers. Cover different sub-topics.

If the user specified `--start-date`, use that instead of your suggestion.

### Step 1: Search arXiv

**CS categories:** `cs.AI`, `cs.CL`, `cs.LG`, `cs.MA`, `cs.SE`

Combine your search queries with the category filter:
```
(cat:cs.AI OR cat:cs.CL OR cat:cs.LG OR cat:cs.MA OR cat:cs.SE) AND (<your_query_1> OR <your_query_2> OR ...)
```

**API call** (use Bash with Python for reliable XML parsing):
```python
python3 -c "
import urllib.request, xml.etree.ElementTree as ET, urllib.parse, json
query = urllib.parse.quote('<FULL_QUERY>')
url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=<POOL_SIZE_x3>&sortBy=submittedDate&sortOrder=ascending'
data = urllib.request.urlopen(url).read()
root = ET.fromstring(data)
ns = {'a': 'http://www.w3.org/2005/Atom'}
papers = []
for entry in root.findall('a:entry', ns):
    title = ' '.join(entry.find('a:title', ns).text.split())
    abstract = ' '.join(entry.find('a:summary', ns).text.split())
    published = entry.find('a:published', ns).text[:10]
    authors = [a.find('a:name', ns).text for a in entry.findall('a:author', ns)]
    url = entry.find('a:id', ns).text
    pdf = next((l.attrib['href'] for l in entry.findall('a:link', ns) if l.attrib.get('title') == 'pdf'), None)
    papers.append({'title': title, 'abstract': abstract, 'published': published, 'authors': authors, 'url': url, 'pdf_url': pdf})
print(json.dumps(papers, ensure_ascii=False))
"
```

Filter results: only keep papers where `published >= start_date`.

### Step 2: Deduplicate

Read `processed_papers.json` from the project root (create `{}` if it doesn't exist). Extract paper IDs:
- From URL like `http://arxiv.org/abs/2210.03629v1` → ID is `2210.03629` (strip version)

Skip any paper whose ID is already in the history.

### Step 3: AI Screening

For each candidate paper (unless `--no-screen`), evaluate:

- Is it foundational or influential in this area?
- Does it introduce a novel method, framework, or benchmark?
- Is it highly relevant to the search topic?
- Would it be interesting to a technical audience?

Based on title and abstract, decide: **PASS** (process it) or **SKIP** (move on). Print your reasoning in one sentence.

### Step 4: Fetch Paper Content

For each paper that passes screening:

1. Download the PDF using Bash: `curl -sL "<pdf_url>" -o /tmp/paper.pdf`
2. Read the PDF using the Read tool: `Read /tmp/paper.pdf`
3. If PDF reading fails, proceed with abstract only — do NOT abort.
4. Clean up: `rm /tmp/paper.pdf`

### Step 5: Summarize

Generate a structured bilingual summary. The output must be a JSON object with ALL of these fields:

```json
{
  "title_zh": "论文中文标题（意译，不要硬翻）",
  "title_en": "Original English title",
  "one_line_summary_zh": "一句话概述这篇论文做了什么、为什么重要",
  "one_line_summary_en": "One sentence: what this paper does and why it matters",
  "research_problem_zh": "这篇论文要解决什么问题？为什么这个问题重要？（2-3句）",
  "research_problem_en": "What problem does this paper address and why is it important? (2-3 sentences)",
  "abstract_summary_zh": "摘要的中文总结（3-5句，涵盖动机、方法、结果）",
  "abstract_summary_en": "Abstract summary (3-5 sentences covering motivation, method, results)",
  "core_method_zh": "核心方法的详细描述（具体说明怎么做的，不要笼统）",
  "core_method_en": "Detailed description of the core method (be specific, not generic)",
  "model_framework_zh": "模型架构或框架的描述（具体组件、流程）",
  "model_framework_en": "Model architecture or framework description (specific components, pipeline)",
  "datasets_zh": "使用了哪些数据集，规模如何",
  "datasets_en": "What datasets were used and their scale",
  "experimental_setup_zh": "实验设置：基线方法、评估指标、关键超参数",
  "experimental_setup_en": "Experimental setup: baselines, metrics, key hyperparameters",
  "main_results_zh": "主要实验结果（尽量包含具体数字）",
  "main_results_en": "Main experimental results (include specific numbers where possible)",
  "innovations_zh": "这篇论文的主要创新点是什么（1-3点）",
  "innovations_en": "What are the main innovations (1-3 points)",
  "limitations_zh": "论文的局限性和不足",
  "limitations_en": "Limitations and shortcomings",
  "use_cases_zh": "适用场景：这个方法/框架最适合用在哪里",
  "use_cases_en": "Use cases: where this method/framework is most applicable",
  "key_takeaways_zh": "作为读者我应该重点关注什么（2-3点实用建议）",
  "key_takeaways_en": "What should I focus on as a reader (2-3 practical takeaways)",
  "keywords_zh": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
  "keywords_en": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}
```

**If `--summarizer claude` (default):** You generate the summary yourself based on the paper content you just read. Be thorough, specific, and include real numbers/names. Write Chinese natively, not as translation.

**If `--summarizer api`:** Read `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` from `.env`, then call the OpenAI-compatible API:
```bash
source .env && curl -s ${LLM_BASE_URL}/chat/completions \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '<JSON payload with model=$LLM_MODEL, messages, temperature=0.3, max_tokens=8192>'
```
The prompt should contain the paper info + abstract + content + the JSON schema above. Works with any OpenAI-compatible endpoint (MiniMax, DeepSeek, Qwen, OpenAI, Ollama, etc.).

### Step 6: Generate ONE Combined MDX

**IMPORTANT:** Do NOT write one MDX per paper. Process ALL papers first (Steps 3-5 in a loop), collect all summaries, then write ONE combined MDX containing all papers.

**Filename:** `{today}-{slugified-query}-paper-digest.mdx`

**Template:**

```
---
title: "Paper Digest: {query}"
date: "{today}"
tags:
  - {all keywords from all papers}
draft: false
summary: "{N} papers on {query}: {paper1 title}; {paper2 title}; ..."
---

# Paper Digest: {query}

> {N} papers reviewed on **{today}**

---

# 1. {paper1_title_en}

**{paper1_title_zh}**

**Authors:** {authors}  |  **Published:** {published}  |  **Source:** arxiv

> {one_line_summary_en}
>
> {one_line_summary_zh}

**Link / 论文链接:** [{url}]({url})

## Research Problem / 研究问题
[... all sections for paper 1 ...]

---

# 2. {paper2_title_en}
[... all sections for paper 2 ...]

---

# 3. {paper3_title_en}
[... all sections for paper 3 ...]
```

Each paper section contains all the bilingual summary fields (Research Problem, Abstract Summary, Core Method, Model & Framework, Datasets, Experimental Setup, Main Results, Innovations, Limitations, Use Cases, Key Takeaways, Keywords).

### Step 7: Update History

Read `processed_papers.json`, add entries for ALL processed papers, write it back:

```json
{
  "<paper_id>": {
    "title": "<title>",
    "url": "<url>",
    "query": "<query>",
    "mdx_path": "<output/filename.mdx>",
    "processed_at": "<ISO datetime>"
  }
}
```

### Step 8: Report

After ALL papers are processed and the MDX is written, show a summary:
- How many candidates found
- How many skipped (already processed / failed screening)
- List of all papers included in the digest with titles and dates
- Path to the generated MDX file
