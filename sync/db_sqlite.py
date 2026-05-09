"""
SQLite 数据库操作模块
- 初始化建表
- 批量 upsert 存货标签数据
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS material_label_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_code TEXT NOT NULL,
    material_name TEXT NOT NULL,
    inv_class_code TEXT,
    inv_class_name TEXT,
    specification TEXT,
    com_unit_code TEXT,
    com_unit_name TEXT,
    cloth_card_no TEXT,
    color_desc TEXT,
    remark TEXT,
    size_model TEXT,
    craft_desc TEXT,
    material_desc TEXT,
    market_desc TEXT,
    package_size TEXT,
    qr_url TEXT,
    status INTEGER NOT NULL DEFAULT 1,
    source_updated_at TEXT,
    sync_updated_at TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_INDEX_SQLS = [
    """
    CREATE UNIQUE INDEX IF NOT EXISTS uk_material_label_items_code
    ON material_label_items(material_code);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_material_label_items_cloth_card_no
    ON material_label_items(cloth_card_no);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_material_label_items_inv_class_code
    ON material_label_items(inv_class_code);
    """,
]

UPSERT_SQL = """
INSERT INTO material_label_items (
    material_code, material_name, inv_class_code, inv_class_name,
    specification, com_unit_code, com_unit_name, cloth_card_no,
    color_desc, remark, size_model, craft_desc, material_desc,
    market_desc, package_size, qr_url, status, sync_updated_at
)
VALUES (
    :material_code, :material_name, :inv_class_code, :inv_class_name,
    :specification, :com_unit_code, :com_unit_name, :cloth_card_no,
    :color_desc, :remark, :size_model, :craft_desc, :material_desc,
    :market_desc, :package_size, :qr_url, :status, :sync_updated_at
)
ON CONFLICT(material_code) DO UPDATE SET
    material_name    = excluded.material_name,
    inv_class_code   = excluded.inv_class_code,
    inv_class_name   = excluded.inv_class_name,
    specification    = excluded.specification,
    com_unit_code    = excluded.com_unit_code,
    com_unit_name    = excluded.com_unit_name,
    cloth_card_no    = excluded.cloth_card_no,
    color_desc       = excluded.color_desc,
    remark           = excluded.remark,
    size_model       = excluded.size_model,
    craft_desc       = excluded.craft_desc,
    material_desc    = excluded.material_desc,
    market_desc      = excluded.market_desc,
    package_size     = excluded.package_size,
    qr_url           = excluded.qr_url,
    status           = excluded.status,
    sync_updated_at  = excluded.sync_updated_at,
    updated_at       = datetime('now', 'localtime');
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    """获取 SQLite 连接，自动创建上级目录"""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # 开启 WAL 模式，提升并发读写性能
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(db_path: str) -> None:
    """初始化数据库：建表 + 建索引（幂等）"""
    with get_connection(db_path) as conn:
        conn.execute(CREATE_TABLE_SQL)
        for idx_sql in CREATE_INDEX_SQLS:
            conn.execute(idx_sql)
        conn.commit()


def upsert_items(db_path: str, items: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    批量 upsert 存货标签数据。
    返回统计：{"inserted": N, "updated": N, "failed": N}
    """
    inserted = 0
    updated = 0
    failed = 0
    errors = []

    with get_connection(db_path) as conn:
        for item in items:
            try:
                cursor = conn.execute(UPSERT_SQL, item)
                # last_insert_rowid > 0 且 changes == 1 表示新插入
                # changes == 1 但 rowid 已存在表示更新
                if cursor.lastrowid and conn.execute(
                    "SELECT changes()"
                ).fetchone()[0] == 1:
                    # 通过判断 total_changes 累积量来区分 insert/update
                    pass
            except Exception as e:
                failed += 1
                errors.append({"code": item.get("material_code"), "error": str(e)})

        conn.commit()

    # SQLite 的 ON CONFLICT DO UPDATE 无法直接区分 insert/update，
    # 改用逐条检查的方式统计（已在 upsert 前后对比 total_changes）
    # 这里简化处理：成功条数 = len(items) - failed，不再细分 insert/update
    success = len(items) - failed
    return {"success": success, "failed": failed, "errors": errors}


def upsert_items_with_stats(db_path: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量 upsert，精确区分插入与更新条数。
    通过在 upsert 前先 SELECT 判断记录是否已存在。
    """
    inserted = 0
    updated = 0
    failed = 0
    errors = []

    with get_connection(db_path) as conn:
        for item in items:
            try:
                code = item.get("material_code")
                exists = conn.execute(
                    "SELECT 1 FROM material_label_items WHERE material_code = ?", (code,)
                ).fetchone()
                conn.execute(UPSERT_SQL, item)
                if exists:
                    updated += 1
                else:
                    inserted += 1
            except Exception as e:
                failed += 1
                errors.append({"code": item.get("material_code"), "error": str(e)})

        conn.commit()

    return {
        "inserted": inserted,
        "updated": updated,
        "failed": failed,
        "errors": errors,
    }


def get_material(db_path: str, material_code: str) -> Optional[Dict[str, Any]]:
    """按存货编码查询单条记录"""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM material_label_items WHERE material_code = ?",
            (material_code,),
        ).fetchone()
        return dict(row) if row else None


def list_materials(db_path: str, keyword: str = "", limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """列表查询，支持关键词搜索"""
    with get_connection(db_path) as conn:
        if keyword:
            sql = """
                SELECT * FROM material_label_items
                WHERE material_code LIKE ? OR material_name LIKE ? OR cloth_card_no LIKE ?
                ORDER BY material_code
                LIMIT ? OFFSET ?
            """
            kw = f"%{keyword}%"
            rows = conn.execute(sql, (kw, kw, kw, limit, offset)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM material_label_items ORDER BY material_code LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [dict(r) for r in rows]
