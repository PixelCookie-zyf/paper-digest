import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # LLM API (any OpenAI-compatible endpoint)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.minimaxi.com/v1"
    llm_model: str = "MiniMax-M2.7"

    # Output
    output_dir: str = "output"

    # Search defaults (hardcoded)
    default_query: str = "LLM Agent"
    max_papers: int = 3
    search_pool_size: int = 20
    search_start_date: str = "2022-10-01"
    search_providers: list = field(default_factory=lambda: ["arxiv"])

    def __post_init__(self):
        self.llm_api_key = os.getenv("LLM_API_KEY", self.llm_api_key)
        self.llm_base_url = os.getenv("LLM_BASE_URL", self.llm_base_url)
        self.llm_model = os.getenv("LLM_MODEL", self.llm_model)
        self.output_dir = os.getenv("OUTPUT_DIR", self.output_dir)


settings = Settings()
