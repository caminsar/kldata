"""基于LLM的本地知识库系统 - 后端入口"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, get_project_root
from app.models.database import init_db
from app.api import chat, documents, knowledge_base, system


def setup_logging():
    log_dir = get_project_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, settings.logging.level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                settings.resolve_path(settings.logging.file),
                encoding="utf-8",
            ),
        ],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("系统启动完成")
    yield
    logger.info("系统关闭")


app = FastAPI(
    title="本地知识库系统",
    description="基于LLM的本地知识库问答系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge_base.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {
        "name": "本地知识库系统",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug,
    )
