from datetime import datetime, timedelta
from typing import Any, Dict

from admin_db import finish_run, latest_success, running_run, start_run
from db_sqlite import init_db, upsert_items_with_stats
from db_u8 import fetch_materials
from module_config import ModuleConfig, get_module_config, rel_path
from qr_gen import make_qr_url


def _normalize_item(row: Dict[str, Any], cfg: ModuleConfig, sync_time: str) -> Dict[str, Any]:
    code = (row.get("material_code") or "").strip()
    return {
        "material_code": code,
        "material_name": (row.get("material_name") or "").strip(),
        "inv_class_code": row.get("inv_class_code") or "",
        "inv_class_name": row.get("inv_class_name") or "",
        "specification": row.get("specification") or "",
        "com_unit_code": row.get("com_unit_code") or "",
        "com_unit_name": row.get("com_unit_name") or "",
        "cloth_card_no": row.get("cloth_card_no") or "",
        "color_desc": row.get("color_desc") or "",
        "remark": row.get("remark") or "",
        "size_model": row.get("size_model") or "",
        "craft_desc": row.get("craft_desc") or "",
        "material_desc": row.get("material_desc") or "",
        "market_desc": row.get("market_desc") or "",
        "package_size": row.get("package_size") or "",
        "qr_url": make_qr_url(cfg.qr_base_url, code),
        "status": 1,
        "sync_updated_at": sync_time,
    }


def _incremental_since(module_key: str) -> tuple:
    latest = latest_success(module_key)
    if not latest or not latest.get("finished_at"):
        return "", "首次增量同步无历史成功记录，执行全量初始化"
    finished_at = datetime.strptime(latest["finished_at"], "%Y-%m-%d %H:%M:%S")
    return (finished_at - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), ""


def run_sync(module_key: str, trigger_type: str = "manual", sync_scope: str = "incremental") -> Dict[str, Any]:
    if running_run(module_key):
        return {"status": "skipped", "message": "模块正在同步中"}

    cfg = get_module_config(module_key)
    run_id = start_run(module_key, trigger_type)
    db_path = rel_path(cfg.sqlite_path)

    try:
        init_db(db_path)
        modified_after, initial_reason = _incremental_since(module_key) if sync_scope == "incremental" else ("", "")
        degraded_reason = ""
        try:
            rows = fetch_materials(
                host=cfg.u8_host,
                port=cfg.u8_port,
                database=cfg.u8_database,
                user=cfg.u8_user,
                password=cfg.u8_password,
                modified_after=modified_after,
            )
        except RuntimeError as exc:
            if sync_scope != "incremental":
                raise
            degraded_reason = str(exc)
            rows = fetch_materials(
                host=cfg.u8_host,
                port=cfg.u8_port,
                database=cfg.u8_database,
                user=cfg.u8_user,
                password=cfg.u8_password,
            )
        sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = [
            _normalize_item(row, cfg, sync_time)
            for row in rows
            if (row.get("material_code") or "").strip()
        ]
        stats = upsert_items_with_stats(db_path, items)
        result = {
            "extracted": len(rows),
            "inserted": stats["inserted"],
            "updated": stats["updated"],
            "failed": stats["failed"],
        }
        message = f"增量同步：抽取 {modified_after} 之后变更的物料" if modified_after else sync_scope
        if initial_reason:
            message = initial_reason
        if degraded_reason:
            message = f"{message}; 已降级全量同步：{degraded_reason}"
        finish_run(run_id, "success", result, message)
        return {"status": "success", "scope": sync_scope, "message": message, **result}
    except Exception as exc:
        finish_run(run_id, "failed", {}, str(exc))
        return {"status": "failed", "message": str(exc)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ItemMark 模块同步")
    parser.add_argument("module_key", choices=["material-info", "wuping"])
    parser.add_argument("--trigger", default="manual")
    parser.add_argument("--scope", default="incremental", choices=["incremental", "full"])
    args = parser.parse_args()
    print(run_sync(args.module_key, args.trigger, args.scope))
