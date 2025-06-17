from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    postgres_dsn: str = Field(
        "postgresql://postgres:postgres@localhost:5432/postgres",
        alias="DATABASE_URL",
    )
    neo4j_uri: str = Field("bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field("neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field("neo4j", alias="NEO4J_PASSWORD")
    ollama_url: str = Field("http://localhost:11434", alias="OLLAMA_URL")
    chunk_size: int = Field(500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(100, alias="CHUNK_OVERLAP")
    ui_host: str = Field("0.0.0.0", alias="UI_HOST")
    ui_port: int = Field(8501, alias="UI_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True


settings = Settings()
