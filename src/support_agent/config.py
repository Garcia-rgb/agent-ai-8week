from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中读取应用配置；同名环境变量会覆盖这里的默认值。"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./support_agent.db"
    redis_url: str | None = None
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    confirmation_secret: str = "development-only-secret"
    max_upload_bytes: int = 5 * 1024 * 1024
    retrieval_top_k: int = 5
    chunk_size: int = 700
    chunk_overlap: int = 100

    @property
    def llm_enabled(self) -> bool:
        """只有远程模型所需的三项配置齐全时才启用模型调用。"""
        return bool(self.llm_base_url and self.llm_api_key and self.llm_model)


@lru_cache
def get_settings() -> Settings:
    return Settings()
