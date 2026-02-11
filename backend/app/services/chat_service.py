"""对话服务 - RAG 检索增强生成"""
import json
import logging
import uuid
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import ChatHistory
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from app.services.llm_service import get_llm
from app.services import vector_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个智能知识库助手。请根据以下提供的参考资料来回答用户的问题。

回答要求：
1. 基于参考资料进行回答，不要编造信息
2. 如果参考资料中没有相关信息，请如实说明
3. 回答要条理清晰、准确简洁
4. 如果需要，可以适当整合多个来源的信息

参考资料：
{context}"""

GENERAL_SYSTEM_PROMPT = """你是一个智能助手，请准确、友好地回答用户的问题。"""


def _build_context(sources: list[tuple]) -> str:
    parts = []
    for i, (doc, score) in enumerate(sources, 1):
        source_name = doc.metadata.get("filename", "未知来源")
        parts.append(f"[{i}] 来源: {source_name}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _get_chat_history(db: Session, session_id: str, limit: int = 10) -> list:
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    records.reverse()
    messages = []
    for r in records:
        if r.role == "user":
            messages.append(HumanMessage(content=r.content))
        elif r.role == "assistant":
            messages.append(AIMessage(content=r.content))
    return messages


def _save_message(db: Session, session_id: str, role: str, content: str,
                  knowledge_base_id: int | None = None, sources: str = ""):
    record = ChatHistory(
        session_id=session_id,
        knowledge_base_id=knowledge_base_id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(record)
    db.commit()


def chat(db: Session, request: ChatRequest) -> ChatResponse:
    """执行RAG对话"""
    session_id = request.session_id or uuid.uuid4().hex
    llm = get_llm()

    source_docs: list[SourceDocument] = []
    messages = []

    if request.knowledge_base_id:
        # RAG 模式：检索相关文档
        results = vector_store.search(
            knowledge_base_id=request.knowledge_base_id,
            query=request.question,
            top_k=request.top_k,
        )
        context = _build_context(results)
        system_prompt = SYSTEM_PROMPT.format(context=context)

        source_docs = [
            SourceDocument(
                content=doc.page_content[:200],
                source=doc.metadata.get("filename", "未知"),
                score=round(score, 4),
            )
            for doc, score in results
        ]
    else:
        # 通用对话模式
        system_prompt = GENERAL_SYSTEM_PROMPT

    messages.append(SystemMessage(content=system_prompt))

    # 加载历史对话
    history = _get_chat_history(db, session_id)
    messages.extend(history)

    # 添加当前问题
    messages.append(HumanMessage(content=request.question))

    # 调用 LLM
    logger.info("调用LLM，会话=%s, 知识库=%s", session_id, request.knowledge_base_id)
    response = llm.invoke(messages)
    answer = response.content

    # 保存对话记录
    sources_json = json.dumps([s.model_dump() for s in source_docs], ensure_ascii=False)
    _save_message(db, session_id, "user", request.question, request.knowledge_base_id)
    _save_message(db, session_id, "assistant", answer, request.knowledge_base_id, sources_json)

    return ChatResponse(
        answer=answer,
        session_id=session_id,
        sources=source_docs,
        knowledge_base_id=request.knowledge_base_id,
    )


def get_history(db: Session, session_id: str) -> list[ChatHistory]:
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )


def get_sessions(db: Session, knowledge_base_id: int | None = None) -> list[dict]:
    """获取所有会话列表"""
    query = db.query(
        ChatHistory.session_id,
        ChatHistory.knowledge_base_id,
    ).distinct(ChatHistory.session_id)

    if knowledge_base_id:
        query = query.filter(ChatHistory.knowledge_base_id == knowledge_base_id)

    results = query.all()
    sessions = []
    for session_id, kb_id in results:
        first = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id, ChatHistory.role == "user")
            .order_by(ChatHistory.created_at.asc())
            .first()
        )
        sessions.append({
            "session_id": session_id,
            "knowledge_base_id": kb_id,
            "title": (first.content[:50] + "...") if first and len(first.content) > 50 else (first.content if first else "新对话"),
        })
    return sessions


def delete_session(db: Session, session_id: str) -> bool:
    count = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).delete()
    db.commit()
    return count > 0
