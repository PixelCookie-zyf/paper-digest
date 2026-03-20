import os
import re
import logging
from datetime import date
from paper_search.base import PaperMeta

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def _render_paper_section(idx: int, paper: PaperMeta, summary: dict) -> str:
    """Render one paper's summary as a section within a combined MDX."""
    s = summary
    title_en = s.get("title_en", paper.title)
    title_zh = s.get("title_zh", "")
    authors_str = ", ".join(paper.authors[:5])
    if len(paper.authors) > 5:
        authors_str += " et al."

    return f"""
---

# {idx}. {title_en}

**{title_zh}**

**Authors:** {authors_str}  |  **Published:** {paper.published}  |  **Source:** {paper.source}

> {s.get('one_line_summary_en', '')}
>
> {s.get('one_line_summary_zh', '')}

**Link / 论文链接:** [{paper.url}]({paper.url})

## Research Problem / 研究问题

**EN:** {s.get('research_problem_en', 'N/A')}

**ZH:** {s.get('research_problem_zh', 'N/A')}

## Abstract Summary / 摘要总结

**EN:** {s.get('abstract_summary_en', 'N/A')}

**ZH:** {s.get('abstract_summary_zh', 'N/A')}

## Core Method / 核心方法

**EN:** {s.get('core_method_en', 'N/A')}

**ZH:** {s.get('core_method_zh', 'N/A')}

## Model & Framework / 模型与框架

**EN:** {s.get('model_framework_en', 'N/A')}

**ZH:** {s.get('model_framework_zh', 'N/A')}

## Datasets / 数据集

**EN:** {s.get('datasets_en', 'N/A')}

**ZH:** {s.get('datasets_zh', 'N/A')}

## Experimental Setup / 实验设置

**EN:** {s.get('experimental_setup_en', 'N/A')}

**ZH:** {s.get('experimental_setup_zh', 'N/A')}

## Main Results / 主要结果

**EN:** {s.get('main_results_en', 'N/A')}

**ZH:** {s.get('main_results_zh', 'N/A')}

## Innovations / 创新点

**EN:** {s.get('innovations_en', 'N/A')}

**ZH:** {s.get('innovations_zh', 'N/A')}

## Limitations / 局限性

**EN:** {s.get('limitations_en', 'N/A')}

**ZH:** {s.get('limitations_zh', 'N/A')}

## Use Cases / 适用场景

**EN:** {s.get('use_cases_en', 'N/A')}

**ZH:** {s.get('use_cases_zh', 'N/A')}

## Key Takeaways / 重点关注

**EN:** {s.get('key_takeaways_en', 'N/A')}

**ZH:** {s.get('key_takeaways_zh', 'N/A')}

## Keywords / 关键词

**EN:** {', '.join(s.get('keywords_en', []))}

**ZH:** {', '.join(s.get('keywords_zh', []))}
"""


def generate_digest_mdx(query: str, papers_with_summaries: list[tuple[PaperMeta, dict]], output_dir: str) -> str:
    """Generate ONE combined MDX file containing all papers from this run.

    Args:
        query: The search topic
        papers_with_summaries: List of (PaperMeta, summary_dict) tuples
        output_dir: Directory to save the MDX file

    Returns:
        Path to the generated MDX file
    """
    today = date.today().isoformat()
    slug = _slugify(query)
    filename = f"{today}-{slug}-paper-digest.mdx"

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Collect all keywords for tags
    all_keywords = set()
    for _, s in papers_with_summaries:
        all_keywords.update(s.get("keywords_en", []))
    tags_str = "\n".join(f"  - {kw}" for kw in sorted(all_keywords)) if all_keywords else f"  - {query}"

    # Paper titles for summary
    titles = [s.get("title_en", p.title) for p, s in papers_with_summaries]
    titles_list = "; ".join(titles)

    # Frontmatter
    frontmatter = f"""---
title: "Paper Digest: {query}"
date: "{today}"
tags:
{tags_str}
draft: false
summary: "{len(papers_with_summaries)} papers on {query}: {titles_list}"
---"""

    # Header
    header = f"""
# Paper Digest: {query}

> {len(papers_with_summaries)} papers reviewed on **{today}**
"""

    # Paper sections
    sections = []
    for idx, (paper, summary) in enumerate(papers_with_summaries, 1):
        sections.append(_render_paper_section(idx, paper, summary))

    content = frontmatter + "\n" + header + "\n".join(sections)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"[MDX] Generated: {filepath}")
    return filepath
