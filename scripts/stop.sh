#!/usr/bin/env bash
# 停止服务脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== 本地知识库系统 - 停止 ==="

MODE="${1:-dev}"

if [ "$MODE" = "docker" ]; then
    echo "[INFO] 停止 Docker 容器..."
    cd docker
    docker compose down
    echo "[INFO] 容器已停止"
elif [ "$MODE" = "dev" ]; then
    echo "[INFO] 停止开发服务..."
    # 停止 uvicorn
    pkill -f "uvicorn app.main:app" 2>/dev/null && echo "[INFO] 后端已停止" || echo "[WARN] 后端未运行"
    # 停止 vite
    pkill -f "vite" 2>/dev/null && echo "[INFO] 前端已停止" || echo "[WARN] 前端未运行"
else
    echo "用法: $0 [dev|docker]"
    exit 1
fi
