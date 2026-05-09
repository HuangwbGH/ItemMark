from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import dotenv_values

from settings import BASE_DOMAIN, PROJECT_ROOT, rel_path


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
    template_path: str
    detail_type: str
    ledger_enabled: bool
    sync_enabled: bool
    sync_mode: str
    sync_cron: str
    interval_minutes: int

    def public_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["u8_password"] = "******" if self.u8_password else ""
        return data


def _bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是"}


def _module_env_path(module_key: str) -> Path:
    return PROJECT_ROOT / "config" / "modules" / f"{module_key}.env"


def _load_module_env(module_key: str) -> Dict[str, str]:
    path = _module_env_path(module_key)
    data = {k: v for k, v in dotenv_values(path).items() if v is not None}
    if not data:
        raise KeyError(f"模块配置不存在：{module_key}")
    return data


def _from_env(data: Dict[str, str]) -> ModuleConfig:
    module_key = data["MODULE_KEY"]
    return ModuleConfig(
        module_key=module_key,
        module_name=data.get("MODULE_NAME", module_key),
        base_path=data.get("BASE_PATH", f"/{module_key}").rstrip("/"),
        qr_base_url=data.get("QR_BASE_URL", f"{BASE_DOMAIN}/{module_key}").rstrip("/"),
        sqlite_path=data.get("SQLITE_PATH", f"./data/{module_key}/itemmark.db"),
        u8_host=data.get("U8_HOST", "192.168.1.135"),
        u8_port=int(data.get("U8_PORT", "1433")),
        u8_database=data.get("U8_DATABASE", "UFDATA_104_2018"),
        u8_user=data.get("U8_USER", "testreadonly"),
        u8_password=data.get("U8_PASSWORD", ""),
        template_path=data.get("TEMPLATE_PATH", f"./config/templates/{module_key}/label_config.xlsx"),
        detail_type=data.get("DETAIL_TYPE", "material_info"),
        ledger_enabled=_bool(data.get("LEDGER_ENABLED"), False),
        sync_enabled=_bool(data.get("SYNC_ENABLED"), True),
        sync_mode=data.get("SYNC_MODE", "cron"),
        sync_cron=data.get("SYNC_CRON", "0 8,10,14,18 * * *"),
        interval_minutes=int(data.get("SYNC_INTERVAL_MINUTES", "60")),
    )


def get_module_config(module_key: str) -> ModuleConfig:
    if module_key not in MODULE_KEYS:
        raise KeyError(f"未知模块：{module_key}")
    return _from_env(_load_module_env(module_key))


def list_module_configs() -> List[ModuleConfig]:
    return [get_module_config(key) for key in MODULE_KEYS]


def get_module_for_legacy_material() -> ModuleConfig:
    return get_module_config("material-info")


def resolve_module_path(path: str) -> str:
    return rel_path(path)

