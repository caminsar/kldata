"""文档管理 API"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.models.database import Document, KnowledgeBase, get_db
from app.models.schemas import DocumentResponse, MessageResponse
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["文档管理"])


@router.get("/{kb_id}", response_model=list[DocumentResponse])
def list_documents(kb_id: int, db: Session = Depends(get_db)):
    """获取指定知识库的文档列表"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    docs = (
        db.query(Document)
        .filter(Document.knowledge_base_id == kb_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return docs


@router.post("/{kb_id}/upload", response_model=DocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传文档到指定知识库"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")

    content = await file.read()
    try:
        doc = document_service.upload_and_process(db, kb_id, file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return doc


@router.post("/{kb_id}/upload-batch", response_model=list[DocumentResponse])
async def upload_documents_batch(
    kb_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """批量上传文档"""
    results = []
    for file in files:
        if not file.filename:
            continue
        content = await file.read()
        try:
            doc = document_service.upload_and_process(db, kb_id, file.filename, content)
            results.append(doc)
        except ValueError:
            continue
    return results


@router.delete("/file/{doc_id}", response_model=MessageResponse)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """删除指定文档"""
    success = document_service.delete_document(db, doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return MessageResponse(message="文档已删除")


@router.post("/file/{doc_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(doc_id: int, db: Session = Depends(get_db)):
    """重新处理文档"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    document_service.process_document(db, doc_id)
    db.refresh(doc)
    return doc
