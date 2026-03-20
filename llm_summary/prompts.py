# ── Search strategy prompt: LLM generates search terms for any topic ──

SEARCH_STRATEGY_PROMPT = """You are a research advisor helping someone systematically read through a research field.

Given a research topic/direction, generate arXiv search queries to find the most important papers, starting from the foundational ones.

Topic: {topic}

Think about:
1. What are the key terms, synonyms, and related concepts for this topic?
2. What are the foundational papers that started this field? What keywords would match them?
3. When did this research direction start gaining traction? (Suggest a start date)

Respond with ONLY a JSON object (no markdown fences):
{{
  "search_queries": [
    "(abs:term1 AND abs:term2)",
    "(abs:\\"exact phrase\\" AND abs:term3)",
    "(abs:term4 OR abs:term5) AND abs:term6)"
  ],
  "start_date": "YYYY-MM-DD",
  "description": "Brief description of what these queries cover and why"
}}

Rules for search_queries:
- Generate 3-5 arXiv search queries using arXiv query syntax
- Use abs: for abstract search, ti: for title search
- Use AND, OR operators, quote exact phrases with \\"
- Make queries broad enough to catch foundational papers, not just recent ones
- First query should target the most canonical/classic papers in this field
- Cover different angles and sub-topics of the field"""


# ── Screening prompt: quick check if paper is worth reading ──

SCREENING_PROMPT = """You are a research paper curator for a technical blog focused on "{topic}".

Given this paper's title and abstract, decide if it's **worth a detailed read** for someone following this field. Consider:
- Is it a foundational / influential paper in this area?
- Does it introduce a novel method, framework, or benchmark?
- Is it highly relevant to the topic "{topic}"?
- Would it be interesting to a technical audience?

Paper Title: {title}
Authors: {authors}
Published: {published}
Abstract: {abstract}

Respond with ONLY a JSON object (no markdown fences):
{{
  "worth_reading": true or false,
  "reason": "One sentence explaining why or why not"
}}"""


# ── Detailed summary prompt: thorough bilingual analysis ──

PAPER_SUMMARY_PROMPT = """You are a senior research paper analyst writing for a bilingual technical blog.

You are given a paper's full information below. Write a thorough, structured, bilingual (Chinese + English) summary. Be specific — include actual method names, dataset names, metric numbers, and architecture details. Do NOT be vague or generic.

## Paper Information
- Title: {title}
- Authors: {authors}
- Published: {published}
- Source: {source}
- URL: {url}

## Abstract
{abstract}

## Paper Content (may be partial)
{content}

---

## Output Format

Produce a structured summary in the EXACT JSON format below. Each field must have substantive content. For Chinese fields, write naturally — not machine-translated. For English fields, be precise and technical.

Output ONLY the JSON object. No markdown fences, no extra text.

{{
  "title_zh": "论文中文标题（意译，不要硬翻）",
  "title_en": "{title}",
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
}}"""


def build_search_strategy_prompt(topic: str) -> str:
    return SEARCH_STRATEGY_PROMPT.format(topic=topic)


def build_screening_prompt(title: str, authors: list[str], published: str,
                           abstract: str, topic: str = "AI research") -> str:
    return SCREENING_PROMPT.format(
        title=title,
        authors=", ".join(authors[:5]),
        published=published,
        abstract=abstract[:1000],
        topic=topic,
    )


def build_summary_prompt(title: str, authors: list[str], published: str,
                         abstract: str, content: str, url: str,
                         source: str) -> str:
    # Give MiniMax as much content as possible (keep ~30000 chars for M2.7's large context)
    max_content_len = 30000
    if len(content) > max_content_len:
        content = content[:max_content_len] + "\n\n[... content truncated ...]"

    if not content.strip():
        content = "(Full text not available. Please produce the best summary possible based on the abstract.)"

    return PAPER_SUMMARY_PROMPT.format(
        title=title,
        authors=", ".join(authors),
        published=published,
        abstract=abstract,
        content=content,
        url=url,
        source=source,
    )
