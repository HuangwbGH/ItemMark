import sys
from pathlib import Path
from typing import Dict, List

from db.admin_db import latest_run, list_runs
from services.module_config_service import ModuleConfig, get_module_config
from settings import PROJECT_ROOT


SYNC_DIR = PROJECT_ROOT / "sync"
if str(SYNC_DIR) not in sys.path:
    sys.path.insert(0, str(SYNC_DIR))

from sync_runner import run_sync  # noqa: E402


def run_module_sync(module_key: str, sync_scope: str = "incremental") -> Dict[str, object]:
    return run_sync(module_key, "manual", sync_scope)


def get_sync_status(module_key: str) -> Dict[str, object]:
    cfg = get_module_config(module_key)
    return {
        "module": cfg.public_dict(),
        "latest_run": latest_run(module_key),
        "recent_runs": list_runs(module_key, limit=20),
    }


def update_sync_config(module_key: str, sync_enabled: bool, sync_mode: str, sync_cron: str, interval_minutes: int) -> ModuleConfig:
    path = PROJECT_ROOT / "config" / "modules" / f"{module_key}.env"
    lines = path.read_text(encoding="utf-8").splitlines()
    values = {
        "SYNC_ENABLED": "true" if sync_enabled else "false",
        "SYNC_MODE": sync_mode,
        "SYNC_CRON": sync_cron,
        "SYNC_INTERVAL_MINUTES": str(interval_minutes),
    }
    seen = set()
    new_lines: List[str] = []
    for line in lines:
        if "=" not in line or line.strip().startswith("#"):
            new_lines.append(line)
            continue
        key = line.split("=", 1)[0]
        if key in values:
            new_lines.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            new_lines.append(line)
    for key, value in values.items():
        if key not in seen:
            new_lines.append(f"{key}={value}")
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return get_module_config(module_key)
