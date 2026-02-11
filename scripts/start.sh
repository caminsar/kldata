#!/usr/bin/env bash
# 启动服务脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== 本地知识库系统 - 启动 ==="

# 创建必要目录
mkdir -p data/uploads data/vector_store data/backups logs

MODE="${1:-dev}"

if [ "$MODE" = "docker" ]; then
    echo "[INFO] 使用 Docker Compose 启动..."
    cd docker
    docker compose up -d --build
    echo "[INFO] 服务已启动"
    echo "  前端: http://localhost"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
elif [ "$MODE" = "dev" ]; then
    echo "[INFO] 开发模式启动..."

    # 启动后端
    echo "[INFO] 启动后端服务..."
    cd backend
    if [ ! -d ".venv" ]; then
        echo "[INFO] 创建 Python 虚拟环境..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    else
        source .venv/bin/activate
    fi
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..

    # 启动前端
    echo "[INFO] 启动前端开发服务器..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "[INFO] 安装前端依赖..."
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo "[INFO] 服务已启动"
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo ""
    echo "按 Ctrl+C 停止所有服务"

    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
else
    echo "用法: $0 [dev|docker]"
    exit 1
fi
