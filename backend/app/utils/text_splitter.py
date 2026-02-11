"""文本分割工具 - 将文档拆分为适合嵌入的文本块"""
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings


def create_text_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    separators: list[str] | None = None,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.document.chunk_size,
        chunk_overlap=chunk_overlap or settings.document.chunk_overlap,
        separators=separators or settings.document.separators,
        length_function=len,
        is_separator_regex=False,
    )


def split_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    return splitter.split_text(text)
