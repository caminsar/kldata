"""向量嵌入服务 - 支持 OpenAI / Ollama / HuggingFace"""
import logging
from functools import lru_cache

from langchain_core.embeddings import Embeddings

from app.config import settings

logger = logging.getLogger(__name__)


def _create_openai_embeddings() -> Embeddings:
    from langchain_openai import OpenAIEmbeddings
    cfg = settings.embedding.openai
    api_key = cfg.api_key or settings.get_openai_api_key()
    kwargs: dict = {
        "model": cfg.model,
        "openai_api_key": api_key,
    }
    base_url = cfg.api_base or settings.get_openai_base_url()
    if base_url:
        kwargs["openai_api_base"] = base_url
    return OpenAIEmbeddings(**kwargs)


def _create_ollama_embeddings() -> Embeddings:
    from langchain_community.embeddings import OllamaEmbeddings
    cfg = settings.embedding.ollama
    return OllamaEmbeddings(
        base_url=cfg.base_url,
        model=cfg.model,
    )


def _create_huggingface_embeddings() -> Embeddings:
    from langchain_huggingface import HuggingFaceEmbeddings
    cfg = settings.embedding.huggingface
    return HuggingFaceEmbeddings(
        model_name=cfg.model,
        model_kwargs={"device": cfg.device},
        encode_kwargs={"normalize_embeddings": True},
    )


_PROVIDERS = {
    "openai": _create_openai_embeddings,
    "ollama": _create_ollama_embeddings,
    "huggingface": _create_huggingface_embeddings,
}

_instance: Embeddings | None = None


def get_embedding_model() -> Embeddings:
    global _instance
    if _instance is not None:
        return _instance

    provider = settings.embedding.provider
    factory = _PROVIDERS.get(provider)
    if not factory:
        raise ValueError(f"不支持的嵌入模型提供者: {provider}，可选: {list(_PROVIDERS.keys())}")

    logger.info("初始化嵌入模型: provider=%s", provider)
    _instance = factory()
    return _instance


def reset_embedding_model():
    global _instance
    _instance = None


def get_embedding_model_name() -> str:
    provider = settings.embedding.provider
    if provider == "openai":
        return f"openai/{settings.embedding.openai.model}"
    if provider == "ollama":
        return f"ollama/{settings.embedding.ollama.model}"
    if provider == "huggingface":
        return f"huggingface/{settings.embedding.huggingface.model}"
    return provider
