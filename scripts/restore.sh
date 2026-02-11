#!/usr/bin/env bash
# 数据恢复脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "=== 本地知识库系统 - 数据恢复 ==="
    echo ""
    echo "用法: $0 <备份文件路径>"
    echo ""
    echo "可用备份:"
    ls -lh data/backups/*.tar.gz 2>/dev/null || echo "  （无备份文件）"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "[ERROR] 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "=== 本地知识库系统 - 数据恢复 ==="
echo "[WARN] 此操作将覆盖当前数据！"
read -p "确认继续？(y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "[INFO] 已取消"
    exit 0
fi

# 解压到临时目录
TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
BACKUP_DIR=$(ls "$TEMP_DIR")

echo "[INFO] 恢复数据..."

# 恢复数据库
if [ -f "$TEMP_DIR/$BACKUP_DIR/knowledge_base.db" ]; then
    cp "$TEMP_DIR/$BACKUP_DIR/knowledge_base.db" "data/"
    echo "[INFO] 数据库已恢复"
fi

# 恢复向量库
if [ -d "$TEMP_DIR/$BACKUP_DIR/vector_store" ]; then
    rm -rf "data/vector_store"
    cp -r "$TEMP_DIR/$BACKUP_DIR/vector_store" "data/"
    echo "[INFO] 向量库已恢复"
fi

# 恢复上传文件
if [ -d "$TEMP_DIR/$BACKUP_DIR/uploads" ]; then
    rm -rf "data/uploads"
    cp -r "$TEMP_DIR/$BACKUP_DIR/uploads" "data/"
    echo "[INFO] 上传文件已恢复"
fi

# 恢复配置
if [ -d "$TEMP_DIR/$BACKUP_DIR/config" ]; then
    cp -r "$TEMP_DIR/$BACKUP_DIR/config" .
    echo "[INFO] 配置文件已恢复"
fi

rm -rf "$TEMP_DIR"
echo "[INFO] 数据恢复完成！请重启服务使配置生效。"
