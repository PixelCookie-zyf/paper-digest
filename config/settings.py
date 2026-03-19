import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # MiniMax API
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_model: str = "MiniMax-M2.7"

    # Output
    output_dir: str = "output"

    # Search defaults (hardcoded, no need to configure)
    default_query: str = "LLM Agent"
    max_papers: int = 3
    search_pool_size: int = 20
    search_start_date: str = "2022-10-01"
    search_providers: list = field(default_factory=lambda: ["arxiv"])

    def __post_init__(self):
        self.minimax_api_key = os.getenv("MINIMAX_API_KEY", self.minimax_api_key)
        self.minimax_base_url = os.getenv("MINIMAX_BASE_URL", self.minimax_base_url)
        self.minimax_model = os.getenv("MINIMAX_MODEL", self.minimax_model)
        self.output_dir = os.getenv("OUTPUT_DIR", self.output_dir)


settings = Settings()
