"""Configuration management for Mimic.AI backend."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Data Processing
    max_upload_size_mb: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
