from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PaperMeta:
    """Metadata for a single paper."""
    title: str
    authors: list[str]
    published: str
    abstract: str
    url: str
    pdf_url: Optional[str] = None
    source: str = "unknown"
    full_text: str = ""


class SearchProvider(ABC):
    """Abstract base class for paper search providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def search(self, query: str, max_results: int = 3) -> list[PaperMeta]:
        pass
