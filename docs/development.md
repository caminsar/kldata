# 开发文档

## 环境要求

- Python 3.11+
- Node.js 18+
- (可选) Docker & Docker Compose

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd kldata
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 启动开发环境

**一键启动（推荐）：**
```bash
./scripts/start.sh dev
```

**手动启动：**

后端：
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

前端：
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 项目结构

```
kldata/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── chat.py           # 对话接口
│   │   │   ├── documents.py      # 文档管理接口
│   │   │   ├── knowledge_base.py # 知识库管理接口
│   │   │   └── system.py         # 系统配置接口
│   │   ├── models/         # 数据模型
│   │   │   ├── database.py       # SQLAlchemy ORM 模型
│   │   │   └── schemas.py        # Pydantic 请求/响应模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── chat_service.py       # RAG 对话
│   │   │   ├── document_service.py   # 文档处理
│   │   │   ├── embedding_service.py  # 向量嵌入
│   │   │   ├── llm_service.py        # LLM 调用
│   │   │   └── vector_store.py       # 向量存储
│   │   ├── utils/          # 工具函数
│   │   │   ├── file_parser.py        # 文件解析
│   │   │   └── text_splitter.py      # 文本分块
│   │   ├── config.py       # 配置管理
│   │   └── main.py         # FastAPI 入口
│   └── requirements.txt
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── api/            # API 调用封装
│   │   ├── stores/         # Pinia 状态管理
│   │   └── router/         # 路由
│   ├── package.json
│   └── vite.config.js
├── config/
│   └── config.yaml         # 主配置文件
├── docker/                 # Docker 相关
├── scripts/                # 运维脚本
├── data/                   # 运行时数据（不纳入版本管理）
│   ├── uploads/            # 上传文件
│   ├── vector_store/       # FAISS 索引
│   └── backups/            # 备份文件
├── docs/                   # 文档
├── .env.example            # 环境变量模板
└── CLAUDE.md               # AI 助手指引
```

## 配置说明

核心配置文件为 `config/config.yaml`，包含以下部分：

| 配置项 | 说明 |
|--------|------|
| `server` | 服务端口、CORS 设置 |
| `llm` | LLM 提供者、模型、参数 |
| `embedding` | 嵌入模型提供者和参数 |
| `vector_store` | 向量库类型和存储路径 |
| `document` | 文件上传限制、分块参数 |
| `retrieval` | 检索数量、阈值、搜索方式 |
| `database` | 数据库连接字符串 |
| `logging` | 日志级别和输出 |

也支持通过环境变量覆盖：`OPENAI_API_KEY`, `OPENAI_API_BASE`

## API 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/knowledge-bases` | 获取知识库列表 |
| POST | `/api/knowledge-bases` | 创建知识库 |
| PUT | `/api/knowledge-bases/{id}` | 更新知识库 |
| DELETE | `/api/knowledge-bases/{id}` | 删除知识库 |
| GET | `/api/documents/{kb_id}` | 获取文档列表 |
| POST | `/api/documents/{kb_id}/upload` | 上传文档 |
| DELETE | `/api/documents/file/{doc_id}` | 删除文档 |
| POST | `/api/chat` | 发送对话 |
| GET | `/api/chat/history/{session_id}` | 获取对话历史 |
| GET | `/api/chat/sessions` | 获取会话列表 |
| GET | `/api/system/config` | 获取系统配置 |
| PUT | `/api/system/config` | 更新系统配置 |
| GET | `/api/system/health` | 健康检查 |

完整 API 文档请访问: http://localhost:8000/docs

## 使用本地模型 (Ollama)

如果不想使用 OpenAI API，可以通过 Ollama 运行本地模型：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 修改 config/config.yaml
# llm.provider: "ollama"
# embedding.provider: "ollama"
```
