#!/usr/bin/env python3
"""数据库初始化脚本"""
import sys
import os

# 将 backend 目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.models.database import init_db, engine, Base


def main():
    print("=== 数据库初始化 ===")
    init_db()
    print("[INFO] 数据库表已创建")

    # 显示所有表
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"[INFO] 数据库包含 {len(tables)} 张表:")
    for t in tables:
        columns = inspector.get_columns(t)
        print(f"  - {t} ({len(columns)} 列)")

    print("[INFO] 初始化完成")


if __name__ == "__main__":
    main()
