import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def rel_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"运行路径必须使用相对路径：{value}")
    return str(PROJECT_ROOT / path)


APP_NAME = os.getenv("APP_NAME", "ItemMark")
BASE_DOMAIN = os.getenv("BASE_DOMAIN", "https://code.zestrade.com").rstrip("/")
ADMIN_DB_PATH = os.getenv("ADMIN_DB_PATH", "./data/admin/itemmark_admin.db")
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "18089"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

