from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str
    pinecone_api_key: str
    pinecone_index_name: str = "agentic-ai-rag"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    top_k: int = 5
    min_relevance_score: float = 0.30
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
