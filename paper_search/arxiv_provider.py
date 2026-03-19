import logging
from datetime import datetime
import arxiv
from .base import SearchProvider, PaperMeta

logger = logging.getLogger(__name__)

# CS categories relevant to LLM/Agent research
CS_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.MA", "cs.SE"]

# Expanded search terms per topic — helps catch foundational papers
# whose titles don't literally contain the user's query
TOPIC_EXPANSIONS = {
    "LLM Agent": [
        '(abs:LLM AND abs:agent)',
        '(abs:"large language model" AND abs:agent)',
        '(abs:"language model" AND abs:reasoning AND abs:acting)',
        '(abs:"language model" AND abs:"tool use")',
        '(abs:"language model" AND abs:planning AND abs:agent)',
    ],
}


class ArxivProvider(SearchProvider):
    """Search papers on arXiv, filtered to CS, sorted by date (oldest first)."""

    @property
    def name(self) -> str:
        return "arxiv"

    def _build_query(self, query: str) -> str:
        """Build an arXiv query targeting CS papers.

        Uses topic expansions for known topics, otherwise falls back
        to a simple abstract/title keyword search.
        """
        cat_filter = " OR ".join(f"cat:{c}" for c in CS_CATEGORIES)

        # Check if we have expanded search terms for this topic
        expansions = TOPIC_EXPANSIONS.get(query)
        if expansions:
            term_filter = "(" + " OR ".join(expansions) + ")"
        else:
            words = query.strip().split()
            if len(words) == 1:
                term_filter = f'(ti:"{query}" OR abs:"{query}")'
            else:
                term_parts = [f'abs:{w}' for w in words]
                term_filter = "(" + " AND ".join(term_parts) + ")"

        full_query = f"({cat_filter}) AND {term_filter}"
        logger.debug(f"[arXiv] Query: {full_query}")
        return full_query

    def search(self, query: str, max_results: int = 20,
               start_date: str | None = None) -> list[PaperMeta]:
        """Search arXiv for CS papers, sorted oldest-first, filtered by date.

        Args:
            query: Search keywords (e.g., "LLM Agent")
            max_results: How many results to return after filtering
            start_date: Only return papers published on/after this date (YYYY-MM-DD)
        """
        logger.info(f"[arXiv] Searching: '{query}' (target {max_results}, from {start_date or 'any'})")

        arxiv_query = self._build_query(query)

        # Fetch extra to account for date filtering and dedup
        fetch_count = max_results * 3 if start_date else max_results

        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=arxiv_query,
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

                # Deduplicate within this search
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

            # Sort by date to ensure chronological order across expanded queries
            results.sort(key=lambda p: p.published)

            logger.info(f"[arXiv] Found {len(results)} papers")
            return results
        except Exception as e:
            logger.error(f"[arXiv] Search failed: {e}")
            return []
