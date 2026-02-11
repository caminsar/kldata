#!/usr/bin/env bash
# 数据备份脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

BACKUP_DIR="data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="kldata_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "=== 本地知识库系统 - 数据备份 ==="
echo "[INFO] 备份时间: ${TIMESTAMP}"

mkdir -p "$BACKUP_PATH"

# 备份数据库
if [ -f "data/knowledge_base.db" ]; then
    cp "data/knowledge_base.db" "$BACKUP_PATH/"
    echo "[INFO] 数据库已备份"
fi

# 备份向量库
if [ -d "data/vector_store" ]; then
    cp -r "data/vector_store" "$BACKUP_PATH/"
    echo "[INFO] 向量库已备份"
fi

# 备份上传文件
if [ -d "data/uploads" ]; then
    cp -r "data/uploads" "$BACKUP_PATH/"
    echo "[INFO] 上传文件已备份"
fi

# 备份配置
cp -r "config" "$BACKUP_PATH/"
echo "[INFO] 配置文件已备份"

# 压缩
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

echo "[INFO] 备份完成: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# 清理旧备份（保留最近 10 个）
ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f
echo "[INFO] 旧备份已清理（保留最近 10 个）"
