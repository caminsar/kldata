"""应用配置管理模块"""
import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def load_yaml_config() -> dict:
    config_path = get_project_root() / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_yaml = load_yaml_config()


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


class OpenAILLMConfig(BaseModel):
    api_key: str = ""
    api_base: str = ""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9


class OllamaLLMConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    temperature: float = 0.7
    max_tokens: int = 2000


class LLMConfig(BaseModel):
    provider: str = "openai"
    openai: OpenAILLMConfig = OpenAILLMConfig()
    ollama: OllamaLLMConfig = OllamaLLMConfig()


class OpenAIEmbeddingConfig(BaseModel):
    api_key: str = ""
    api_base: str = ""
    model: str = "text-embedding-3-small"


class OllamaEmbeddingConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "nomic-embed-text"


class HuggingFaceEmbeddingConfig(BaseModel):
    model: str = "BAAI/bge-small-zh-v1.5"
    device: str = "cpu"


class EmbeddingConfig(BaseModel):
    provider: str = "openai"
    openai: OpenAIEmbeddingConfig = OpenAIEmbeddingConfig()
    ollama: OllamaEmbeddingConfig = OllamaEmbeddingConfig()
    huggingface: HuggingFaceEmbeddingConfig = HuggingFaceEmbeddingConfig()


class VectorStoreConfig(BaseModel):
    type: str = "faiss"
    persist_directory: str = "./data/vector_store"
    collection_name: str = "knowledge_base"


class DocumentConfig(BaseModel):
    upload_directory: str = "./data/uploads"
    allowed_extensions: list[str] = [".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".html"]
    max_file_size_mb: int = 50
    chunk_size: int = 500
    chunk_overlap: int = 50
    separators: list[str] = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]


class RetrievalConfig(BaseModel):
    top_k: int = 5
    score_threshold: float = 0.5
    search_type: str = "similarity"
    mmr_fetch_k: int = 20
    mmr_lambda: float = 0.5


class DatabaseConfig(BaseModel):
    url: str = "sqlite:///./data/knowledge_base.db"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "./logs/app.log"
    max_size_mb: int = 10
    backup_count: int = 5


class Settings(BaseSettings):
    server: ServerConfig = Field(default_factory=lambda: ServerConfig(**_yaml.get("server", {})))
    llm: LLMConfig = Field(default_factory=lambda: LLMConfig(**{
        k: v for k, v in _yaml.get("llm", {}).items()
    }) if _yaml.get("llm") else LLMConfig())
    embedding: EmbeddingConfig = Field(default_factory=lambda: EmbeddingConfig(**{
        k: v for k, v in _yaml.get("embedding", {}).items()
    }) if _yaml.get("embedding") else EmbeddingConfig())
    vector_store: VectorStoreConfig = Field(
        default_factory=lambda: VectorStoreConfig(**_yaml.get("vector_store", {}))
    )
    document: DocumentConfig = Field(
        default_factory=lambda: DocumentConfig(**_yaml.get("document", {}))
    )
    retrieval: RetrievalConfig = Field(
        default_factory=lambda: RetrievalConfig(**_yaml.get("retrieval", {}))
    )
    database: DatabaseConfig = Field(
        default_factory=lambda: DatabaseConfig(**_yaml.get("database", {}))
    )
    logging: LoggingConfig = Field(
        default_factory=lambda: LoggingConfig(**_yaml.get("logging", {}))
    )

    class Config:
        env_prefix = "KB_"

    def resolve_path(self, path_str: str) -> Path:
        p = Path(path_str)
        if p.is_absolute():
            return p
        return get_project_root() / p

    @property
    def upload_dir(self) -> Path:
        path = self.resolve_path(self.document.upload_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def vector_store_dir(self) -> Path:
        path = self.resolve_path(self.vector_store.persist_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_openai_api_key(self) -> str:
        return self.llm.openai.api_key or os.getenv("OPENAI_API_KEY", "")

    def get_openai_base_url(self) -> Optional[str]:
        url = self.llm.openai.api_base or os.getenv("OPENAI_API_BASE", "")
        return url or None


settings = Settings()
