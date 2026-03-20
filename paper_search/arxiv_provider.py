import logging
from datetime import datetime
import arxiv
from .base import SearchProvider, PaperMeta

logger = logging.getLogger(__name__)

CS_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.MA", "cs.SE"]


class ArxivProvider(SearchProvider):
    """Search papers on arXiv, filtered to CS, sorted by date (oldest first)."""

    @property
    def name(self) -> str:
        return "arxiv"

    def search(self, search_queries: list[str], max_results: int = 20,
               start_date: str | None = None) -> list[PaperMeta]:
        """Search arXiv using LLM-generated queries.

        Args:
            search_queries: List of arXiv query fragments from LLM (e.g. '(abs:LLM AND abs:agent)')
            max_results: How many results to return after filtering
            start_date: Only return papers published on/after this date (YYYY-MM-DD)
        """
        cat_filter = " OR ".join(f"cat:{c}" for c in CS_CATEGORIES)
        term_filter = "(" + " OR ".join(search_queries) + ")"
        full_query = f"({cat_filter}) AND {term_filter}"

        logger.info(f"[arXiv] Searching with {len(search_queries)} queries (target {max_results}, from {start_date or 'any'})")
        logger.debug(f"[arXiv] Query: {full_query}")

        fetch_count = max_results * 3 if start_date else max_results

        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=full_query,
                max_results=fetch_count,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Ascending,
            )

            cutoff = None
            if start_date:
                cutoff = datetime.strptime(start_date, "%Y-%m-%d")

            results = []
            seen_ids = set()
            for r in client.results(search):
                if cutoff and r.published.replace(tzinfo=None) < cutoff:
                    continue

                paper_id = r.entry_id.rstrip("/").split("/")[-1]
                if "v" in paper_id:
                    paper_id = paper_id.rsplit("v", 1)[0]
                if paper_id in seen_ids:
                    continue
                seen_ids.add(paper_id)

                paper = PaperMeta(
                    title=r.title.replace("\n", " ").strip(),
                    authors=[a.name for a in r.authors],
                    published=r.published.strftime("%Y-%m-%d"),
                    abstract=r.summary.replace("\n", " ").strip(),
                    url=r.entry_id,
                    pdf_url=r.pdf_url,
                    source="arxiv",
                )
                results.append(paper)
                logger.debug(f"  [{paper.published}] {paper.title}")

                if len(results) >= max_results:
                    break

            results.sort(key=lambda p: p.published)
            logger.info(f"[arXiv] Found {len(results)} papers")
            return results
        except Exception as e:
            logger.error(f"[arXiv] Search failed: {e}")
            return []
