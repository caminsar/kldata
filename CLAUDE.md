# CLAUDE.md

## Project Overview

**kldata** — 基于 LLM 的本地知识库问答系统，采用 RAG 架构。后端 Python/FastAPI，前端 Vue 3/Element Plus。

## Repository Structure

```
kldata/
├── backend/                # Python 后端
│   ├── app/
│   │   ├── api/            # FastAPI 路由 (chat, documents, knowledge_base, system)
│   │   ├── models/         # SQLAlchemy ORM + Pydantic schemas
│   │   ├── services/       # 业务逻辑 (chat, document, embedding, llm, vector_store)
│   │   ├── utils/          # 文件解析、文本分块
│   │   ├── config.py       # 配置管理（读取 config/config.yaml）
│   │   └── main.py         # FastAPI 入口
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # ChatView, KnowledgeBaseView, DocumentsView, SettingsView
│   │   ├── api/index.js    # Axios API 封装
│   │   ├── stores/         # Pinia 状态
│   │   └── router/         # Vue Router
│   ├── package.json
│   └── vite.config.js      # Vite + API 代理到 :8000
├── config/config.yaml      # 主配置文件
├── docker/                 # Dockerfile, docker-compose, nginx.conf
├── scripts/                # start.sh, stop.sh, backup.sh, restore.sh, health_check.sh
├── data/                   # 运行时数据（不入库）
├── docs/                   # architecture.md, development.md, deployment.md, api.md
└── .env.example            # 环境变量模板
```

## Development Workflows

### Install & Run (Dev Mode)

```bash
# 后端
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend && npm install && npm run dev
```

Or use the one-liner: `./scripts/start.sh dev`

### Build Frontend

```bash
cd frontend && npm run build
```

### Docker

```bash
./scripts/start.sh docker    # 启动
./scripts/stop.sh docker     # 停止
```

### Maintenance

```bash
./scripts/backup.sh                       # 备份数据
./scripts/restore.sh data/backups/xxx.tar.gz  # 恢复数据
./scripts/health_check.sh                 # 健康检查
python3 scripts/init_db.py                # 初始化数据库
```

## Key Configuration

Config file: `config/config.yaml`

| Section | Key fields |
|---------|------------|
| `llm` | `provider` (openai/ollama), model, temperature, max_tokens |
| `embedding` | `provider` (openai/ollama/huggingface), model |
| `document` | chunk_size (500), chunk_overlap (50), allowed_extensions |
| `retrieval` | top_k (5), score_threshold (0.5), search_type (similarity/mmr) |
| `database` | SQLite URL |

Environment variables: `OPENAI_API_KEY`, `OPENAI_API_BASE`

## Architecture (RAG Pipeline)

```
Upload → Parse file → Chunk text → Embed → Store in FAISS
Query  → Embed query → Search FAISS → Build context → LLM generate → Response
```

## Conventions

- **Backend**: Python 3.11+, type hints, Chinese docstrings
- **Frontend**: Vue 3 Composition API (`<script setup>`), Element Plus components
- **Config**: All tunables in `config/config.yaml`, not hardcoded
- **API paths**: `/api/knowledge-bases`, `/api/documents`, `/api/chat`, `/api/system`
- **Commit messages**: imperative mood, under 72 chars

## Notes for AI Assistants

- Read `config/config.yaml` to understand tunable parameters before changing defaults
- Backend services use singleton pattern for LLM/embedding instances; call `reset_*()` after config changes
- Vector data is stored per knowledge base in `data/vector_store/kb_{id}/`
- The frontend proxies `/api` to `localhost:8000` in dev mode (see `vite.config.js`)
- SQLite DB path is relative to project root: `data/knowledge_base.db`
- File parsing is synchronous; for production consider async task queues
