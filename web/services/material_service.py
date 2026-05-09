from typing import Any, Dict, List, Optional

from db.material_db import get_material, get_materials_by_codes, search_materials
from services.module_config_service import ModuleConfig


def find_material(cfg: ModuleConfig, material_code: str) -> Optional[Dict[str, Any]]:
    return get_material(cfg, material_code)


def search(cfg: ModuleConfig, keyword: str = "", limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    return search_materials(cfg, keyword=keyword, limit=limit, offset=offset)


def by_codes(cfg: ModuleConfig, codes: List[str]) -> List[Dict[str, Any]]:
    return get_materials_by_codes(cfg, codes)

