from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    llm_url: str = Field(alias="LLM_URL", default="http://localhost:11434/v1/chat/completions")
    llm_key: str = Field(alias="LLM_KEY", default="dev")
    redis_host: str = Field(alias="REDIS_HOST", default="localhost")
    redis_port: int = Field(alias="REDIS_PORT", default=6379)
    embed_dim: int = Field(alias="EMBED_DIM", default=384)
    ef_search: int = Field(alias="EF_SEARCH", default=64)
    k_examples: int = Field(alias="K_EXAMPLES", default=3)

settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
