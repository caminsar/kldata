"""向量存储服务 - 基于 FAISS 的向量检索"""
import logging
import os
import shutil
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.services.embedding_service import get_embedding_model

logger = logging.getLogger(__name__)


def _get_kb_path(knowledge_base_id: int) -> Path:
    return settings.vector_store_dir / f"kb_{knowledge_base_id}"


def add_documents(knowledge_base_id: int, texts: list[str], metadatas: list[dict] | None = None) -> int:
    """向指定知识库添加文档向量"""
    if not texts:
        return 0

    embeddings = get_embedding_model()
    kb_path = _get_kb_path(knowledge_base_id)

    documents = [
        Document(page_content=text, metadata=meta or {})
        for text, meta in zip(texts, metadatas or [{}] * len(texts))
    ]

    if kb_path.exists():
        logger.info("加载已有向量库: kb_id=%d", knowledge_base_id)
        store = FAISS.load_local(
            str(kb_path), embeddings, allow_dangerous_deserialization=True
        )
        store.add_documents(documents)
    else:
        logger.info("创建新向量库: kb_id=%d", knowledge_base_id)
        store = FAISS.from_documents(documents, embeddings)

    store.save_local(str(kb_path))
    logger.info("已保存 %d 个文档块到向量库 kb_id=%d", len(texts), knowledge_base_id)
    return len(texts)


def search(
    knowledge_base_id: int,
    query: str,
    top_k: int | None = None,
    score_threshold: float | None = None,
) -> list[tuple[Document, float]]:
    """在指定知识库中检索相关文档"""
    embeddings = get_embedding_model()
    kb_path = _get_kb_path(knowledge_base_id)

    if not kb_path.exists():
        logger.warning("向量库不存在: kb_id=%d", knowledge_base_id)
        return []

    store = FAISS.load_local(
        str(kb_path), embeddings, allow_dangerous_deserialization=True
    )

    k = top_k or settings.retrieval.top_k
    threshold = score_threshold or settings.retrieval.score_threshold

    if settings.retrieval.search_type == "mmr":
        docs = store.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=settings.retrieval.mmr_fetch_k,
            lambda_mult=settings.retrieval.mmr_lambda,
        )
        return [(doc, 1.0) for doc in docs]

    results = store.similarity_search_with_relevance_scores(query, k=k)
    return [(doc, score) for doc, score in results if score >= threshold]


def delete_knowledge_base(knowledge_base_id: int) -> bool:
    """删除知识库的全部向量数据"""
    kb_path = _get_kb_path(knowledge_base_id)
    if kb_path.exists():
        shutil.rmtree(kb_path)
        logger.info("已删除向量库: kb_id=%d", knowledge_base_id)
        return True
    return False


def delete_document_vectors(knowledge_base_id: int, doc_id: int) -> bool:
    """从向量库中删除指定文档的所有向量（通过重建索引实现）"""
    embeddings = get_embedding_model()
    kb_path = _get_kb_path(knowledge_base_id)

    if not kb_path.exists():
        return False

    store = FAISS.load_local(
        str(kb_path), embeddings, allow_dangerous_deserialization=True
    )

    all_docs = store.similarity_search("", k=store.index.ntotal)
    remaining = [doc for doc in all_docs if doc.metadata.get("doc_id") != doc_id]

    if remaining:
        new_store = FAISS.from_documents(remaining, embeddings)
        new_store.save_local(str(kb_path))
    else:
        shutil.rmtree(kb_path)

    logger.info("已删除文档向量: kb_id=%d, doc_id=%d", knowledge_base_id, doc_id)
    return True


def get_document_count(knowledge_base_id: int) -> int:
    """获取知识库中的向量数量"""
    kb_path = _get_kb_path(knowledge_base_id)
    if not kb_path.exists():
        return 0
    embeddings = get_embedding_model()
    store = FAISS.load_local(
        str(kb_path), embeddings, allow_dangerous_deserialization=True
    )
    return store.index.ntotal
