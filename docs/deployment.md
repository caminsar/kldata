# 部署文档

## Docker 部署（推荐）

### 前置条件

- Docker 20.10+
- Docker Compose v2+

### 步骤

1. **配置环境变量**

```bash
cp .env.example .env
vim .env  # 填入 OPENAI_API_KEY
```

2. **启动服务**

```bash
./scripts/start.sh docker
# 或直接运行
cd docker && docker compose up -d --build
```

3. **访问**

- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

4. **停止服务**

```bash
./scripts/stop.sh docker
```

## 手动部署

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 生产环境启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端

```bash
cd frontend
npm install
npm run build
# 将 dist/ 目录部署到 Nginx 或其他 Web 服务器
```

### Nginx 配置参考

参见 `docker/nginx.conf`，主要需要：
- 静态文件服务指向前端 dist 目录
- `/api/` 路径反向代理到后端 8000 端口
- SPA 历史路由模式支持

## 数据管理

### 备份

```bash
./scripts/backup.sh
# 备份文件保存在 data/backups/，自动保留最近 10 份
```

### 恢复

```bash
./scripts/restore.sh data/backups/kldata_backup_20260101_120000.tar.gz
```

### 健康检查

```bash
./scripts/health_check.sh
```

## 性能调优

| 参数 | 建议值 | 说明 |
|------|--------|------|
| `document.chunk_size` | 500-1000 | 中文文档建议 500，英文建议 1000 |
| `document.chunk_overlap` | 50-100 | 约为 chunk_size 的 10% |
| `retrieval.top_k` | 3-5 | 过大会引入噪声 |
| `retrieval.score_threshold` | 0.3-0.7 | 视数据质量调整 |
| `llm.max_tokens` | 2000-4000 | 根据回答长度需求设置 |
