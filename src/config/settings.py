from __future__ import annotations

import os
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = os.getenv("ENV_FILE")
if ENV_FILE is None:
    ENV_FILE = ".env" if Path(".env").exists() else ".env.example"
class DatabaseSettings(BaseSettings):
    """Database connection configuration."""

    dsn: str = Field(..., alias="DATABASE_URL")

    @field_validator("dsn")
    def _dsn_must_not_be_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("DATABASE_URL must be set")
        return value

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )


class Neo4jSettings(BaseSettings):
    """Neo4j connection configuration."""

    uri: str = Field(..., alias="NEO4J_URI")
    user: str = Field(..., alias="NEO4J_USER")
    password: str = Field(..., alias="NEO4J_PASSWORD")

    @field_validator("uri", "user", "password")
    def _not_empty(cls, value: str, info):
        if not value:
            raise ValueError(f"{info.field_name.upper()} must be set")
        return value

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )


class OllamaSettings(BaseSettings):
    """Ollama service configuration."""

    url: str = Field(..., alias="OLLAMA_URL")

    @field_validator("url")
    def _url_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("OLLAMA_URL must be set")
        return value

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )


class ChunkingSettings(BaseSettings):
    """Text chunking configuration."""

    size: int = Field(..., alias="CHUNK_SIZE")
    overlap: int = Field(..., alias="CHUNK_OVERLAP")

    @field_validator("size", "overlap")
    def _positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("chunk values must be positive")
        return value

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )


class UISettings(BaseSettings):
    """Streamlit UI configuration."""

    host: str = Field(..., alias="UI_HOST")
    port: int = Field(..., alias="UI_PORT")

    @field_validator("port")
    def _valid_port(cls, value: int) -> int:
        if not (1 <= value <= 65535):
            raise ValueError("UI_PORT must be between 1 and 65535")
        return value

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )




class Settings(BaseSettings):
    """Application configuration grouped into logical sections."""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    ui: UISettings = Field(default_factory=UISettings)

    @property
    def postgres_dsn(self) -> str:
        return self.database.dsn

    @property
    def neo4j_uri(self) -> str:
        return self.neo4j.uri

    @property
    def neo4j_user(self) -> str:
        return self.neo4j.user

    @property
    def neo4j_password(self) -> str:
        return self.neo4j.password

    @property
    def ollama_url(self) -> str:
        return self.ollama.url

    @property
    def chunk_size(self) -> int:
        return self.chunking.size

    @property
    def chunk_overlap(self) -> int:
        return self.chunking.overlap

    @property
    def ui_host(self) -> str:
        return self.ui.host

    @property
    def ui_port(self) -> int:
        return self.ui.port

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

