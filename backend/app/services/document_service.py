"""文档处理服务 - 上传、解析、分块、入库"""
import logging
import os
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import Document, KnowledgeBase
from app.services import vector_store
from app.services.embedding_service import get_embedding_model_name
from app.utils.file_parser import parse_file, get_file_size
from app.utils.text_splitter import split_text

logger = logging.getLogger(__name__)


def save_uploaded_file(file_content: bytes, filename: str, knowledge_base_id: int) -> str:
    """保存上传的文件到磁盘，返回文件路径"""
    kb_dir = settings.upload_dir / str(knowledge_base_id)
    kb_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    file_path = kb_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(file_content)
    return str(file_path)


def process_document(db: Session, document_id: int) -> None:
    """处理文档: 解析 -> 分块 -> 生成向量 -> 存储"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        logger.error("文档不存在: id=%d", document_id)
        return

    doc.status = "processing"
    db.commit()

    try:
        # 1. 解析文档
        logger.info("解析文档: %s", doc.filename)
        text = parse_file(doc.file_path)
        if not text.strip():
            raise ValueError("文档内容为空")

        # 2. 分块
        chunks = split_text(text)
        logger.info("文档分块完成: %s -> %d 块", doc.filename, len(chunks))

        # 3. 生成元数据
        metadatas = [
            {
                "doc_id": doc.id,
                "filename": doc.filename,
                "knowledge_base_id": doc.knowledge_base_id,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        # 4. 向量化并存储
        vector_store.add_documents(
            knowledge_base_id=doc.knowledge_base_id,
            texts=chunks,
            metadatas=metadatas,
        )

        doc.chunk_count = len(chunks)
        doc.status = "completed"
        logger.info("文档处理完成: %s, %d 块", doc.filename, len(chunks))

    except Exception as e:
        logger.exception("文档处理失败: %s", doc.filename)
        doc.status = "failed"
        doc.error_message = str(e)

    db.commit()


def upload_and_process(
    db: Session,
    knowledge_base_id: int,
    filename: str,
    file_content: bytes,
) -> Document:
    """上传文件并处理入库"""
    # 验证知识库
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
    if not kb:
        raise ValueError(f"知识库不存在: id={knowledge_base_id}")

    # 验证文件扩展名
    ext = Path(filename).suffix.lower()
    if ext not in settings.document.allowed_extensions:
        raise ValueError(f"不支持的文件格式: {ext}")

    # 验证文件大小
    size = len(file_content)
    max_size = settings.document.max_file_size_mb * 1024 * 1024
    if size > max_size:
        raise ValueError(f"文件大小超限: {size / 1024 / 1024:.1f}MB > {settings.document.max_file_size_mb}MB")

    # 保存文件
    file_path = save_uploaded_file(file_content, filename, knowledge_base_id)

    # 创建文档记录
    doc = Document(
        knowledge_base_id=knowledge_base_id,
        filename=filename,
        file_path=file_path,
        file_type=ext,
        file_size=size,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 如果知识库没有记录嵌入模型，更新它
    if not kb.embedding_model:
        kb.embedding_model = get_embedding_model_name()
        db.commit()

    # 处理文档（同步方式，生产环境应改为异步任务队列）
    process_document(db, doc.id)
    db.refresh(doc)

    return doc


def delete_document(db: Session, document_id: int) -> bool:
    """删除文档及其向量"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return False

    # 删除向量
    vector_store.delete_document_vectors(doc.knowledge_base_id, doc.id)

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # 删除数据库记录
    db.delete(doc)
    db.commit()
    return True
