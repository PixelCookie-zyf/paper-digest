import os
import re
import logging
from datetime import date
from paper_search.base import PaperMeta

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def _render_paper(summary: dict, paper_url: str) -> str:
    """Render a single paper's full summary as Markdown."""
    s = summary

    return f"""
> {s.get('one_line_summary_en', '')}
>
> {s.get('one_line_summary_zh', '')}

**Link / 论文链接:** [{paper_url}]({paper_url})

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


def generate_single_mdx(paper: PaperMeta, summary: dict, output_dir: str) -> str:
    """Generate one MDX file for one paper.

    Args:
        paper: Paper metadata
        summary: Structured summary dict from MiniMax
        output_dir: Directory to save the MDX file

    Returns:
        Path to the generated MDX file
    """
    today = date.today().isoformat()
    title_slug = _slugify(paper.title)
    filename = f"{today}-{title_slug}.mdx"

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Tags from keywords
    keywords = summary.get("keywords_en", [])
    tags_str = "\n".join(f"  - {kw}" for kw in keywords) if keywords else "  - LLM Agent"

    title_en = summary.get("title_en", paper.title)
    title_zh = summary.get("title_zh", "")
    one_line = summary.get("one_line_summary_en", "")
    authors_str = ", ".join(paper.authors[:5])
    if len(paper.authors) > 5:
        authors_str += " et al."

    # Frontmatter
    frontmatter = f"""---
title: "{title_en}"
date: "{paper.published}"
tags:
{tags_str}
draft: false
authors: "{authors_str}"
summary: "{one_line}"
paper_url: "{paper.url}"
---"""

    # Header
    header = f"""
# {title_en}

**{title_zh}**

**Authors:** {authors_str}  |  **Published:** {paper.published}  |  **Source:** {paper.source}
"""

    # Body
    body = _render_paper(summary, paper.url)

    content = frontmatter + "\n" + header + body

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"[MDX] Generated: {filepath}")
    return filepath
