from datetime import date
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from services.label_template_service import get_label_config
from services.ledger_service import default_start_date, fetch_ledger
from services.material_service import by_codes, find_material, search
from services.module_config_service import get_module_config, list_module_configs
from services.sync_service import get_sync_status, run_module_sync, update_sync_config


router = APIRouter(prefix="/api")


class ByCodesRequest(BaseModel):
    codes: List[str]


class SyncConfigRequest(BaseModel):
    sync_enabled: bool = True
    sync_mode: str = "cron"
    sync_cron: str = "0 8,10,14,18 * * *"
    interval_minutes: int = 60


class SyncRunRequest(BaseModel):
    sync_scope: str = "incremental"


def _module_cfg(module_key: str):
    try:
        return get_module_config(module_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/health")
def health():
    return {"code": 0, "service": "ItemMark"}


@router.get("/modules")
def modules():
    return {"code": 0, "data": [cfg.public_dict() for cfg in list_module_configs()]}


@router.get("/{module_key}/material/{material_code}")
def api_get_material(module_key: str, material_code: str):
    cfg = _module_cfg(module_key)
    item = find_material(cfg, material_code)
    if not item:
        raise HTTPException(status_code=404, detail="物料不存在")
    return {"code": 0, "data": item}


@router.get("/{module_key}/materials")
def api_search_materials(
    module_key: str,
    keyword: Optional[str] = Query(default=""),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    cfg = _module_cfg(module_key)
    items = search(cfg, keyword=keyword or "", limit=limit, offset=offset)
    return {"code": 0, "data": items, "count": len(items)}


@router.post("/{module_key}/materials/by-codes")
def api_materials_by_codes(module_key: str, body: ByCodesRequest):
    if len(body.codes) > 200:
        raise HTTPException(status_code=400, detail="一次最多查询 200 条")
    cfg = _module_cfg(module_key)
    items = by_codes(cfg, body.codes)
    return {"code": 0, "data": items, "count": len(items)}


@router.get("/{module_key}/label-config")
def api_label_config(module_key: str):
    cfg = _module_cfg(module_key)
    return {"code": 0, "data": get_label_config(cfg)}


@router.get("/{module_key}/material/{material_code}/ledger")
def api_ledger(
    module_key: str,
    material_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    cfg = _module_cfg(module_key)
    if not cfg.ledger_enabled:
        raise HTTPException(status_code=404, detail="当前模块未启用台账查询")
    query_end = end_date or date.today()
    query_start = start_date or default_start_date(query_end)
    if query_start > query_end:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
    try:
        data = fetch_ledger(cfg, material_code, query_start, query_end)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"U8 台账查询失败：{exc}") from exc
    return {"code": 0, "data": data}


@router.get("/{module_key}/sync/status")
def api_sync_status(module_key: str):
    _module_cfg(module_key)
    return {"code": 0, "data": get_sync_status(module_key)}


@router.post("/{module_key}/sync/run")
def api_sync_run(module_key: str, background_tasks: BackgroundTasks, body: SyncRunRequest = SyncRunRequest()):
    _module_cfg(module_key)
    if body.sync_scope not in {"incremental", "full"}:
        raise HTTPException(status_code=400, detail="同步范围只能是 incremental 或 full")
    background_tasks.add_task(run_module_sync, module_key, body.sync_scope)
    return {"code": 0, "message": "同步任务已提交"}


@router.get("/{module_key}/sync/config")
def api_sync_config(module_key: str):
    cfg = _module_cfg(module_key)
    return {
        "code": 0,
        "data": {
            "sync_enabled": cfg.sync_enabled,
            "sync_mode": cfg.sync_mode,
            "sync_cron": cfg.sync_cron,
            "interval_minutes": cfg.interval_minutes,
        },
    }


@router.put("/{module_key}/sync/config")
def api_sync_config_update(module_key: str, body: SyncConfigRequest):
    _module_cfg(module_key)
    if body.sync_mode not in {"cron", "interval"}:
        raise HTTPException(status_code=400, detail="同步模式只能是 cron 或 interval")
    cfg = update_sync_config(
        module_key,
        sync_enabled=body.sync_enabled,
        sync_mode=body.sync_mode,
        sync_cron=body.sync_cron,
        interval_minutes=body.interval_minutes,
    )
    return {"code": 0, "data": cfg.public_dict()}


@router.get("/material/{material_code}")
def legacy_api_material(material_code: str):
    return api_get_material("material-info", material_code)


@router.get("/materials")
def legacy_api_materials(
    keyword: Optional[str] = Query(default=""),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return api_search_materials("material-info", keyword=keyword, limit=limit, offset=offset)
