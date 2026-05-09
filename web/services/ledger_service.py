from datetime import date
from typing import Any, Dict

from db.u8_ledger_db import fetch_inventory_ledger
from services.module_config_service import ModuleConfig


def default_start_date(end_date: date) -> date:
    try:
        return end_date.replace(year=end_date.year - 1)
    except ValueError:
        return end_date.replace(year=end_date.year - 1, day=28)


def fetch_ledger(cfg: ModuleConfig, material_code: str, start_date: date, end_date: date) -> Dict[str, Any]:
    return fetch_inventory_ledger(
        host=cfg.u8_host,
        port=cfg.u8_port,
        database=cfg.u8_database,
        user=cfg.u8_user,
        password=cfg.u8_password,
        material_code=material_code,
        start_date=start_date,
        end_date=end_date,
    )


def format_quantity(value) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return str(value or "0")
    text = f"{number:.6f}".rstrip("0").rstrip(".")
    return text or "0"

