"""知识库管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import KnowledgeBase, get_db
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    MessageResponse,
)
from app.services import vector_store

router = APIRouter(prefix="/api/knowledge-bases", tags=["知识库管理"])


@router.get("", response_model=list[KnowledgeBaseResponse])
def list_knowledge_bases(db: Session = Depends(get_db)):
    """获取所有知识库列表"""
    kbs = db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()
    results = []
    for kb in kbs:
        resp = KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            embedding_model=kb.embedding_model or "",
            document_count=len(kb.documents),
            created_at=kb.created_at,
            updated_at=kb.updated_at,
        )
        results.append(resp)
    return results


@router.post("", response_model=KnowledgeBaseResponse, status_code=201)
def create_knowledge_base(data: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """创建新知识库"""
    existing = db.query(KnowledgeBase).filter(KnowledgeBase.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"知识库名称已存在: {data.name}")

    kb = KnowledgeBase(name=data.name, description=data.description)
    db.add(kb)
    db.commit()
    db.refresh(kb)

    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model or "",
        document_count=0,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """获取知识库详情"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model or "",
        document_count=len(kb.documents),
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(kb_id: int, data: KnowledgeBaseUpdate, db: Session = Depends(get_db)):
    """更新知识库信息"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    if data.name is not None:
        dup = db.query(KnowledgeBase).filter(
            KnowledgeBase.name == data.name, KnowledgeBase.id != kb_id
        ).first()
        if dup:
            raise HTTPException(status_code=400, detail=f"知识库名称已存在: {data.name}")
        kb.name = data.name

    if data.description is not None:
        kb.description = data.description

    db.commit()
    db.refresh(kb)

    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model or "",
        document_count=len(kb.documents),
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.delete("/{kb_id}", response_model=MessageResponse)
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """删除知识库及其所有数据"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 删除向量数据
    vector_store.delete_knowledge_base(kb_id)

    # 删除数据库记录（cascade 会删除关联的文档）
    db.delete(kb)
    db.commit()

    return MessageResponse(message=f"知识库 '{kb.name}' 已删除")
