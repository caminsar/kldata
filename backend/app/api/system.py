"""系统配置 API"""
from fastapi import APIRouter

from app.config import settings
from app.models.schemas import SystemConfigResponse, SystemConfigUpdate, MessageResponse
from app.services.embedding_service import reset_embedding_model
from app.services.llm_service import reset_llm

router = APIRouter(prefix="/api/system", tags=["系统配置"])


@router.get("/config", response_model=SystemConfigResponse)
def get_system_config():
    """获取当前系统配置"""
    llm_model = ""
    if settings.llm.provider == "openai":
        llm_model = settings.llm.openai.model
    elif settings.llm.provider == "ollama":
        llm_model = settings.llm.ollama.model

    emb_model = ""
    if settings.embedding.provider == "openai":
        emb_model = settings.embedding.openai.model
    elif settings.embedding.provider == "ollama":
        emb_model = settings.embedding.ollama.model
    elif settings.embedding.provider == "huggingface":
        emb_model = settings.embedding.huggingface.model

    return SystemConfigResponse(
        llm_provider=settings.llm.provider,
        llm_model=llm_model,
        embedding_provider=settings.embedding.provider,
        embedding_model=emb_model,
        vector_store_type=settings.vector_store.type,
        chunk_size=settings.document.chunk_size,
        chunk_overlap=settings.document.chunk_overlap,
        retrieval_top_k=settings.retrieval.top_k,
        retrieval_score_threshold=settings.retrieval.score_threshold,
    )


@router.put("/config", response_model=MessageResponse)
def update_system_config(data: SystemConfigUpdate):
    """更新系统配置（运行时生效，不持久化到文件）"""
    if data.llm_provider is not None:
        settings.llm.provider = data.llm_provider
        reset_llm()

    if data.llm_model is not None:
        if settings.llm.provider == "openai":
            settings.llm.openai.model = data.llm_model
        elif settings.llm.provider == "ollama":
            settings.llm.ollama.model = data.llm_model
        reset_llm()

    if data.llm_api_key is not None and settings.llm.provider == "openai":
        settings.llm.openai.api_key = data.llm_api_key
        reset_llm()

    if data.llm_api_base is not None and settings.llm.provider == "openai":
        settings.llm.openai.api_base = data.llm_api_base
        reset_llm()

    if data.llm_temperature is not None:
        if settings.llm.provider == "openai":
            settings.llm.openai.temperature = data.llm_temperature
        elif settings.llm.provider == "ollama":
            settings.llm.ollama.temperature = data.llm_temperature
        reset_llm()

    if data.llm_max_tokens is not None:
        if settings.llm.provider == "openai":
            settings.llm.openai.max_tokens = data.llm_max_tokens
        elif settings.llm.provider == "ollama":
            settings.llm.ollama.max_tokens = data.llm_max_tokens
        reset_llm()

    if data.embedding_provider is not None:
        settings.embedding.provider = data.embedding_provider
        reset_embedding_model()

    if data.embedding_model is not None:
        if settings.embedding.provider == "openai":
            settings.embedding.openai.model = data.embedding_model
        elif settings.embedding.provider == "ollama":
            settings.embedding.ollama.model = data.embedding_model
        elif settings.embedding.provider == "huggingface":
            settings.embedding.huggingface.model = data.embedding_model
        reset_embedding_model()

    if data.chunk_size is not None:
        settings.document.chunk_size = data.chunk_size
    if data.chunk_overlap is not None:
        settings.document.chunk_overlap = data.chunk_overlap
    if data.retrieval_top_k is not None:
        settings.retrieval.top_k = data.retrieval_top_k
    if data.retrieval_score_threshold is not None:
        settings.retrieval.score_threshold = data.retrieval_score_threshold

    return MessageResponse(message="配置已更新")


@router.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}
