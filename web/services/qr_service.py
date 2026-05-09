from services.module_config_service import ModuleConfig


def material_detail_url(cfg: ModuleConfig, material_code: str) -> str:
    base = cfg.qr_base_url.rstrip("/")
    return f"{base}/material/{material_code}"

