"""Track processed papers to avoid duplicates across runs."""

import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

HISTORY_FILE = "processed_papers.json"


def _get_history_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), HISTORY_FILE)


def load_history() -> dict:
    """Load the processed papers history. Returns {arxiv_id: {title, date_processed, ...}}."""
    path = _get_history_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load history: {e}")
        return {}


def save_history(history: dict):
    """Save the processed papers history."""
    path = _get_history_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _paper_id(url: str) -> str:
    """Extract a stable ID from paper URL (e.g., '2210.03629' from arXiv URL)."""
    # arXiv URLs: http://arxiv.org/abs/2210.03629v3 -> 2210.03629
    parts = url.rstrip("/").split("/")
    raw_id = parts[-1]
    # Remove version suffix
    if "v" in raw_id:
        raw_id = raw_id.rsplit("v", 1)[0]
    return raw_id


def is_processed(paper_url: str) -> bool:
    """Check if a paper has already been processed."""
    history = load_history()
    pid = _paper_id(paper_url)
    return pid in history


def mark_processed(paper_url: str, title: str, query: str, mdx_path: str):
    """Mark a paper as processed."""
    history = load_history()
    pid = _paper_id(paper_url)
    history[pid] = {
        "title": title,
        "url": paper_url,
        "query": query,
        "mdx_path": mdx_path,
        "processed_at": datetime.now().isoformat(),
    }
    save_history(history)
    logger.info(f"[History] Marked as processed: {pid} — {title}")


def get_processed_ids() -> set[str]:
    """Get all processed paper IDs for fast lookup."""
    history = load_history()
    return set(history.keys())


def show_history():
    """Print a summary of all processed papers."""
    history = load_history()
    if not history:
        print("  No papers processed yet.")
        return
    print(f"\n  Processed papers ({len(history)} total):\n")
    for pid, info in sorted(history.items(), key=lambda x: x[1].get("processed_at", "")):
        print(f"    [{pid}] {info['title']}")
        print(f"           Query: {info.get('query', '?')}  |  {info.get('processed_at', '?')}")
    print()
