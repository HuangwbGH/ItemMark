import sqlite3
from typing import Any, Dict, List, Optional

from services.module_config_service import ModuleConfig, resolve_module_path


SEARCH_FIELDS = [
    "material_code", "material_name", "inv_class_code", "inv_class_name",
    "specification", "com_unit_name", "cloth_card_no", "color_desc", "remark",
    "size_model", "craft_desc", "material_desc", "market_desc", "package_size",
]


def _connect(cfg: ModuleConfig) -> sqlite3.Connection:
    conn = sqlite3.connect(resolve_module_path(cfg.sqlite_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_material(cfg: ModuleConfig, material_code: str) -> Optional[Dict[str, Any]]:
    with _connect(cfg) as conn:
        row = conn.execute(
            "SELECT * FROM material_label_items WHERE material_code = ?",
            (material_code,),
        ).fetchone()
        return dict(row) if row else None


def search_materials(
    cfg: ModuleConfig, keyword: str = "", limit: int = 100, offset: int = 0
) -> List[Dict[str, Any]]:
    with _connect(cfg) as conn:
        if keyword:
            kw = f"%{keyword}%"
            where = " OR ".join(f"{field} LIKE ?" for field in SEARCH_FIELDS)
            sql = f"""
                SELECT * FROM material_label_items
                WHERE {where}
                ORDER BY material_code LIMIT ? OFFSET ?
            """
            rows = conn.execute(sql, (kw,) * len(SEARCH_FIELDS) + (limit, offset)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM material_label_items ORDER BY material_code LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [dict(row) for row in rows]


def get_materials_by_codes(cfg: ModuleConfig, codes: List[str]) -> List[Dict[str, Any]]:
    if not codes:
        return []
    with _connect(cfg) as conn:
        placeholders = ",".join("?" * len(codes))
        rows = conn.execute(
            f"SELECT * FROM material_label_items WHERE material_code IN ({placeholders})",
            codes,
        ).fetchall()
    order = {code: index for index, code in enumerate(codes)}
    return sorted([dict(row) for row in rows], key=lambda row: order.get(row["material_code"], 9999))

