import json
import logging
import re
from openai import OpenAI
from config import settings
from paper_search.base import PaperMeta
from .prompts import build_summary_prompt, build_screening_prompt

logger = logging.getLogger(__name__)


def _create_client() -> OpenAI:
    return OpenAI(
        api_key=settings.minimax_api_key,
        base_url=settings.minimax_base_url,
    )


def _extract_json(raw: str) -> dict:
    """Extract JSON from a response that might have markdown fences or extra text."""
    # Remove markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw)
    cleaned = cleaned.strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("No valid JSON found", raw, 0)


def screen_paper(paper: PaperMeta) -> tuple[bool, str]:
    """Quick screening: is this paper worth a detailed read?

    Returns (worth_reading: bool, reason: str)
    """
    logger.info(f"[Screen] Evaluating: {paper.title}")

    prompt = build_screening_prompt(
        title=paper.title,
        authors=paper.authors,
        published=paper.published,
        abstract=paper.abstract,
    )

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=settings.minimax_model,
            messages=[
                {"role": "system", "content": "You are a paper screening assistant. Respond with JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=256,
        )
        raw = response.choices[0].message.content.strip()
        result = _extract_json(raw)
        worth = result.get("worth_reading", False)
        reason = result.get("reason", "No reason given")
        logger.info(f"[Screen] {'PASS' if worth else 'SKIP'}: {reason}")
        return worth, reason
    except Exception as e:
        logger.warning(f"[Screen] Screening failed ({e}), defaulting to PASS")
        return True, "Screening failed, including by default"


def summarize_paper(paper: PaperMeta) -> dict:
    """Call MiniMax API to generate a thorough bilingual summary for one paper.

    Returns a dict with structured summary fields, or a fallback dict on failure.
    """
    logger.info(f"[MiniMax] Summarizing: {paper.title}")
    logger.info(f"[MiniMax] Content length: {len(paper.full_text)} chars")

    prompt = build_summary_prompt(
        title=paper.title,
        authors=paper.authors,
        published=paper.published,
        abstract=paper.abstract,
        content=paper.full_text,
        url=paper.url,
        source=paper.source,
    )

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=settings.minimax_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior research paper analyst. Produce thorough, specific, bilingual summaries. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=8192,
        )

        raw = response.choices[0].message.content.strip()
        summary = _extract_json(raw)
        logger.info(f"[MiniMax] Summary generated successfully ({len(raw)} chars)")
        return summary

    except json.JSONDecodeError as e:
        logger.error(f"[MiniMax] Failed to parse JSON response: {e}")
        return _fallback_summary(paper)
    except Exception as e:
        logger.error(f"[MiniMax] API call failed: {e}")
        return _fallback_summary(paper)


def _fallback_summary(paper: PaperMeta) -> dict:
    """Generate a minimal fallback summary from paper metadata."""
    logger.warning(f"[MiniMax] Using fallback summary for: {paper.title}")
    return {
        "title_zh": paper.title,
        "title_en": paper.title,
        "one_line_summary_zh": f"关于 {paper.title} 的研究论文",
        "one_line_summary_en": f"Research paper on {paper.title}",
        "research_problem_zh": "（API 调用失败，无法生成详细总结）",
        "research_problem_en": "(API call failed, detailed summary unavailable)",
        "abstract_summary_zh": paper.abstract[:500],
        "abstract_summary_en": paper.abstract[:500],
        "core_method_zh": "请参阅原论文",
        "core_method_en": "Please refer to the original paper",
        "model_framework_zh": "请参阅原论文",
        "model_framework_en": "Please refer to the original paper",
        "datasets_zh": "请参阅原论文",
        "datasets_en": "Please refer to the original paper",
        "experimental_setup_zh": "未提取到详细实验设置",
        "experimental_setup_en": "Detailed experimental setup not extracted",
        "main_results_zh": "请参阅原论文",
        "main_results_en": "Please refer to the original paper",
        "innovations_zh": "请参阅原论文",
        "innovations_en": "Please refer to the original paper",
        "limitations_zh": "请参阅原论文",
        "limitations_en": "Please refer to the original paper",
        "use_cases_zh": "请参阅原论文",
        "use_cases_en": "Please refer to the original paper",
        "key_takeaways_zh": "建议直接阅读原论文摘要",
        "key_takeaways_en": "Recommend reading the original paper abstract",
        "keywords_zh": [],
        "keywords_en": [],
    }
