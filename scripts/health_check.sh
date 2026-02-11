#!/usr/bin/env bash
# 健康检查脚本
set -e

BACKEND_URL="${1:-http://localhost:8000}"

echo "=== 本地知识库系统 - 健康检查 ==="

# 检查后端
echo -n "[CHECK] 后端服务 (${BACKEND_URL})... "
if curl -sf "${BACKEND_URL}/api/system/health" > /dev/null 2>&1; then
    echo "OK"
else
    echo "FAIL"
    echo "[ERROR] 后端服务不可用"
    exit 1
fi

# 检查磁盘空间
echo -n "[CHECK] 磁盘空间... "
USAGE=$(df -h . | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$USAGE" -lt 90 ]; then
    echo "OK (${USAGE}% 已使用)"
else
    echo "WARN (${USAGE}% 已使用，空间不足)"
fi

# 检查数据目录
echo -n "[CHECK] 数据目录... "
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
if [ -d "$PROJECT_DIR/data" ]; then
    echo "OK"
    echo "  上传文件: $(du -sh "$PROJECT_DIR/data/uploads" 2>/dev/null | cut -f1 || echo '0')"
    echo "  向量数据: $(du -sh "$PROJECT_DIR/data/vector_store" 2>/dev/null | cut -f1 || echo '0')"
    echo "  备份: $(ls "$PROJECT_DIR/data/backups"/*.tar.gz 2>/dev/null | wc -l || echo '0') 个"
else
    echo "WARN (数据目录不存在)"
fi

echo ""
echo "=== 检查完成 ==="
