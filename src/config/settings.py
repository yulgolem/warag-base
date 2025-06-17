from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    host: str = Field("postgres", env="DATABASE__HOST")
    port: int = Field(5432, env="DATABASE__PORT")
    name: str = Field("worldbuilding", env="DATABASE__NAME")
    user: str = Field("postgres", env="DATABASE__USER")
    password: str = Field("postgres", env="DATABASE__PASSWORD")


class Neo4jSettings(BaseModel):
    uri: str = Field("bolt://neo4j:7687", env="NEO4J__URI")
    user: str = Field("neo4j", env="NEO4J__USER")
    password: str = Field("neo4j", env="NEO4J__PASSWORD")


class OllamaSettings(BaseModel):
    base_url: str = Field("http://ollama:11434", env="OLLAMA__BASE_URL")


class ChunkingSettings(BaseModel):
    chunk_size: int = Field(500, env="CHUNKING__CHUNK_SIZE")
    chunk_overlap: int = Field(100, env="CHUNKING__CHUNK_OVERLAP")


class UiSettings(BaseModel):
    host: str = Field("0.0.0.0", env="UI__HOST")
    port: int = Field(8501, env="UI__PORT")


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    neo4j: Neo4jSettings = Neo4jSettings()
    ollama: OllamaSettings = OllamaSettings()
    chunking: ChunkingSettings = ChunkingSettings()
    ui: UiSettings = UiSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


settings = Settings()
