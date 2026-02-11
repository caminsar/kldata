"""Pydantic 请求/响应模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---- 知识库 ----

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="知识库名称")
    description: str = Field("", max_length=2000, description="知识库描述")


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: str
    embedding_model: str
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---- 文档 ----

class DocumentResponse(BaseModel):
    id: int
    knowledge_base_id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---- 对话 ----

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000, description="用户问题")
    knowledge_base_id: Optional[int] = Field(None, description="知识库ID，为空则使用通用对话")
    session_id: Optional[str] = Field(None, description="会话ID，用于多轮对话")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="检索文档数量")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="生成温度")


class SourceDocument(BaseModel):
    content: str
    source: str
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[SourceDocument] = []
    knowledge_base_id: Optional[int] = None


class ChatHistoryResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    sources: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- 系统配置 ----

class SystemConfigResponse(BaseModel):
    llm_provider: str
    llm_model: str
    embedding_provider: str
    embedding_model: str
    vector_store_type: str
    chunk_size: int
    chunk_overlap: int
    retrieval_top_k: int
    retrieval_score_threshold: float


class SystemConfigUpdate(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_api_base: Optional[str] = None
    llm_temperature: Optional[float] = None
    llm_max_tokens: Optional[int] = None
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    retrieval_top_k: Optional[int] = None
    retrieval_score_threshold: Optional[float] = None


# ---- 通用 ----

class MessageResponse(BaseModel):
    message: str
    success: bool = True
