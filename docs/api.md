# API 文档

> 完整的交互式文档请访问: http://localhost:8000/docs

## 基础信息

- Base URL: `http://localhost:8000`
- Content-Type: `application/json`（文件上传除外）

## 知识库管理

### 创建知识库

```http
POST /api/knowledge-bases
Content-Type: application/json

{
  "name": "产品手册",
  "description": "产品使用说明文档集合"
}
```

响应:
```json
{
  "id": 1,
  "name": "产品手册",
  "description": "产品使用说明文档集合",
  "embedding_model": "",
  "document_count": 0,
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00"
}
```

### 获取知识库列表

```http
GET /api/knowledge-bases
```

### 删除知识库

```http
DELETE /api/knowledge-bases/{id}
```

## 文档管理

### 上传文档

```http
POST /api/documents/{kb_id}/upload
Content-Type: multipart/form-data

file: <binary>
```

响应:
```json
{
  "id": 1,
  "knowledge_base_id": 1,
  "filename": "manual.pdf",
  "file_type": ".pdf",
  "file_size": 1024000,
  "chunk_count": 42,
  "status": "completed",
  "error_message": "",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00"
}
```

### 获取文档列表

```http
GET /api/documents/{kb_id}
```

### 删除文档

```http
DELETE /api/documents/file/{doc_id}
```

## 智能对话

### 发送消息

```http
POST /api/chat
Content-Type: application/json

{
  "question": "如何安装本产品？",
  "knowledge_base_id": 1,
  "session_id": null,
  "top_k": 5
}
```

响应:
```json
{
  "answer": "根据产品手册，安装步骤如下：...",
  "session_id": "abc123def456",
  "sources": [
    {
      "content": "安装步骤：1. 下载安装包...",
      "source": "manual.pdf",
      "score": 0.8921
    }
  ],
  "knowledge_base_id": 1
}
```

- `knowledge_base_id` 为空时进入通用对话模式（不检索文档）
- `session_id` 为空时创建新会话，传入已有值可继续多轮对话

### 获取对话历史

```http
GET /api/chat/history/{session_id}
```

### 获取会话列表

```http
GET /api/chat/sessions?knowledge_base_id=1
```

## 系统配置

### 获取配置

```http
GET /api/system/config
```

### 更新配置

```http
PUT /api/system/config
Content-Type: application/json

{
  "llm_provider": "ollama",
  "llm_model": "qwen2.5:7b",
  "retrieval_top_k": 3
}
```

### 健康检查

```http
GET /api/system/health
```

响应: `{"status": "ok"}`
