from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from dotenv import dotenv_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_KEYS = ("material-info", "wuping")


@dataclass
class ModuleConfig:
    module_key: str
    module_name: str
    base_path: str
    qr_base_url: str
    sqlite_path: str
    u8_host: str
    u8_port: int
    u8_database: str
    u8_user: str
    u8_password: str
    sync_enabled: bool
    sync_mode: str
    sync_cron: str
    interval_minutes: int


def rel_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"运行路径必须使用相对路径：{value}")
    return str(PROJECT_ROOT / path)


def _bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是"}


def _load_env(module_key: str) -> Dict[str, str]:
    path = PROJECT_ROOT / "config" / "modules" / f"{module_key}.env"
    data = {key: value for key, value in dotenv_values(path).items() if value is not None}
    if not data:
        raise KeyError(f"模块配置不存在：{module_key}")
    return data


def get_module_config(module_key: str) -> ModuleConfig:
    data = _load_env(module_key)
    return ModuleConfig(
        module_key=data["MODULE_KEY"],
        module_name=data.get("MODULE_NAME", module_key),
        base_path=data.get("BASE_PATH", f"/{module_key}").rstrip("/"),
        qr_base_url=data.get("QR_BASE_URL", "").rstrip("/"),
        sqlite_path=data.get("SQLITE_PATH", f"./data/{module_key}/itemmark.db"),
        u8_host=data.get("U8_HOST", "192.168.1.135"),
        u8_port=int(data.get("U8_PORT", "1433")),
        u8_database=data.get("U8_DATABASE", "UFDATA_104_2018"),
        u8_user=data.get("U8_USER", "testreadonly"),
        u8_password=data.get("U8_PASSWORD", ""),
        sync_enabled=_bool(data.get("SYNC_ENABLED"), True),
        sync_mode=data.get("SYNC_MODE", "cron"),
        sync_cron=data.get("SYNC_CRON", "0 8,10,14,18 * * *"),
        interval_minutes=int(data.get("SYNC_INTERVAL_MINUTES", "60")),
    )


def list_module_configs() -> List[ModuleConfig]:
    return [get_module_config(key) for key in MODULE_KEYS]

