# 基于LLM的本地知识库系统

一个支持本地部署的智能知识库问答系统，基于 RAG（检索增强生成）架构，将文档知识与大语言模型结合，实现精准的知识检索和智能问答。

## 功能特性

- **知识库管理** - 创建、编辑、删除多个独立知识库
- **文档处理** - 支持 PDF、DOCX、TXT、Markdown、CSV、HTML 格式
- **智能对话** - 基于知识库内容的 RAG 问答，支持多轮对话
- **多模型支持** - OpenAI 兼容接口 / Ollama 本地模型
- **向量检索** - FAISS 高性能向量搜索，支持 similarity / MMR 检索
- **可视化界面** - 完整的 Web 管理界面

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python + FastAPI + LangChain |
| 向量库 | FAISS |
| 数据库 | SQLite |
| 部署 | Docker Compose |

## 快速开始

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 2. 一键启动开发环境
./scripts/start.sh dev

# 或 Docker 部署
./scripts/start.sh docker
```

- 前端: http://localhost:5173 (开发) / http://localhost (Docker)
- API 文档: http://localhost:8000/docs

## 文档

- [系统架构](docs/architecture.md)
- [开发文档](docs/development.md)
- [部署文档](docs/deployment.md)
- [API 文档](docs/api.md)
