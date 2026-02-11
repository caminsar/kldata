"""对话 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, ChatHistoryResponse, MessageResponse
from app.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["智能对话"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """发送消息并获取AI回答"""
    try:
        return chat_service.chat(db, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.get("/history/{session_id}", response_model=list[ChatHistoryResponse])
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """获取指定会话的对话历史"""
    return chat_service.get_history(db, session_id)


@router.get("/sessions")
def get_sessions(knowledge_base_id: int | None = None, db: Session = Depends(get_db)):
    """获取会话列表"""
    return chat_service.get_sessions(db, knowledge_base_id)


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """删除会话"""
    success = chat_service.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return MessageResponse(message="会话已删除")
