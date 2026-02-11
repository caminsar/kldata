# 系统架构文档

## 架构概述

本系统采用经典的 RAG（Retrieval-Augmented Generation）架构，将文档知识与大语言模型结合，实现基于本地知识库的智能问答。

```
┌──────────────────────────────────────────────────────┐
│                    前端 (Vue 3)                       │
│  ┌──────┐  ┌──────────┐  ┌──────┐  ┌──────────────┐ │
│  │ 对话  │  │ 知识库管理 │  │ 文档  │  │  系统设置    │ │
│  └──┬───┘  └────┬─────┘  └──┬───┘  └──────┬───────┘ │
└─────┼───────────┼───────────┼──────────────┼─────────┘
      │           │           │              │
      ▼           ▼           ▼              ▼
┌──────────────────────────────────────────────────────┐
│                   REST API (FastAPI)                  │
│  /api/chat    /api/knowledge-bases   /api/documents  │
│                  /api/system                          │
└──────────┬───────────────────────────┬───────────────┘
           │                           │
     ┌─────▼─────┐              ┌─────▼──────┐
     │  Chat      │              │  Document   │
     │  Service   │              │  Service    │
     └─────┬─────┘              └──┬───┬──────┘
           │                       │   │
     ┌─────▼─────┐          ┌─────▼┐ ┌▼──────────┐
     │  LLM      │          │ File │ │ Text      │
     │  Service   │          │Parser│ │ Splitter  │
     └─────┬─────┘          └──────┘ └─────┬─────┘
           │                               │
           │         ┌─────────────────────▼──┐
           │         │    Vector Store (FAISS)  │
           │         │    Embedding Service     │
           │         └─────────────────────────┘
           │
    ┌──────▼──────┐
    │ LLM Backend │
    │ OpenAI/Ollama│
    └─────────────┘
```

## 核心组件

### 1. 文档处理管线

```
上传文件 → 文件解析 → 文本分块 → 向量嵌入 → 存入 FAISS
```

- **文件解析** (`file_parser.py`): 支持 PDF, DOCX, TXT, MD, CSV, HTML
- **文本分块** (`text_splitter.py`): 使用 RecursiveCharacterTextSplitter，支持中英文分隔符
- **向量嵌入** (`embedding_service.py`): 支持 OpenAI / Ollama / HuggingFace
- **向量存储** (`vector_store.py`): 基于 FAISS，按知识库分目录存储

### 2. RAG 问答管线

```
用户提问 → 向量检索 → 构造上下文 → 组装 Prompt → LLM 生成 → 返回答案
```

- 检索方式支持 similarity 和 MMR
- 支持多轮对话（基于 session_id 管理历史）
- 答案附带参考来源及相关度分数

### 3. 数据存储

| 存储 | 技术 | 用途 |
|------|------|------|
| 关系数据库 | SQLite | 知识库、文档、对话历史元数据 |
| 向量数据库 | FAISS | 文档向量索引和检索 |
| 文件系统 | 磁盘 | 上传的原始文档 |

### 4. LLM 集成

支持两种 LLM 后端：
- **OpenAI 兼容接口**: 支持 OpenAI 官方及所有兼容 API（如 DeepSeek、Moonshot 等）
- **Ollama**: 本地大模型，完全离线运行

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python + FastAPI + LangChain |
| 向量库 | FAISS |
| 数据库 | SQLite + SQLAlchemy |
| 部署 | Docker Compose + Nginx |
