"""LLM 服务 - 支持 OpenAI / Ollama"""
import logging

from langchain_core.language_models import BaseChatModel

from app.config import settings

logger = logging.getLogger(__name__)

_instance: BaseChatModel | None = None


def _create_openai_llm() -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    cfg = settings.llm.openai
    api_key = cfg.api_key or settings.get_openai_api_key()
    kwargs: dict = {
        "model": cfg.model,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "openai_api_key": api_key,
    }
    base_url = cfg.api_base or settings.get_openai_base_url()
    if base_url:
        kwargs["openai_api_base"] = base_url
    return ChatOpenAI(**kwargs)


def _create_ollama_llm() -> BaseChatModel:
    from langchain_community.chat_models import ChatOllama
    cfg = settings.llm.ollama
    return ChatOllama(
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=cfg.temperature,
        num_predict=cfg.max_tokens,
    )


_PROVIDERS = {
    "openai": _create_openai_llm,
    "ollama": _create_ollama_llm,
}


def get_llm() -> BaseChatModel:
    global _instance
    if _instance is not None:
        return _instance

    provider = settings.llm.provider
    factory = _PROVIDERS.get(provider)
    if not factory:
        raise ValueError(f"不支持的LLM提供者: {provider}，可选: {list(_PROVIDERS.keys())}")

    logger.info("初始化LLM: provider=%s", provider)
    _instance = factory()
    return _instance


def reset_llm():
    global _instance
    _instance = None


def get_llm_model_name() -> str:
    provider = settings.llm.provider
    if provider == "openai":
        return f"openai/{settings.llm.openai.model}"
    if provider == "ollama":
        return f"ollama/{settings.llm.ollama.model}"
    return provider
