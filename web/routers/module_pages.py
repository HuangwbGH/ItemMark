import io
from datetime import date, datetime
from typing import Optional

import qrcode
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from services.label_template_service import get_label_config
from services.ledger_service import default_start_date, fetch_ledger, format_quantity
from services.material_service import by_codes, find_material
from services.module_config_service import get_module_config
from settings import PROJECT_ROOT


templates = Jinja2Templates(directory=str(PROJECT_ROOT / "web" / "templates"))
router = APIRouter()


def _cfg(module_key: str):
    try:
        return get_module_config(module_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _template_prefix(module_key: str) -> str:
    return "material_info" if module_key == "material-info" else "wuping"


def _context(request: Request, cfg):
    return {
        "request": request,
        "module": cfg,
        "public_base_path": cfg.base_path,
        "api_base_path": f"/api/{cfg.module_key}",
    }


def _material_or_404(cfg, material_code: str):
    item = find_material(cfg, material_code)
    if not item:
        raise HTTPException(status_code=404, detail="物料不存在")
    return item


def _footer_text(template: str, item) -> str:
    values = {
        "print_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    values.update({key: "" if value is None else str(value) for key, value in dict(item).items()})
    text = template or ""
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text


@router.get("/material/{material_code}", response_class=HTMLResponse)
def legacy_material_detail(request: Request, material_code: str):
    cfg = _cfg("material-info")
    item = _material_or_404(cfg, material_code)
    context = _context(request, cfg)
    context.update({"item": item, "public_base_path": cfg.base_path})
    return templates.TemplateResponse("material_info/detail.html", context)


@router.get("/print/{material_code}", response_class=HTMLResponse)
def legacy_print_label(request: Request, material_code: str):
    return print_label(request, "material-info", material_code)


@router.get("/batch", response_class=HTMLResponse)
def legacy_batch(request: Request):
    return batch(request, "material-info")


@router.get("/batch/print", response_class=HTMLResponse)
def legacy_batch_print(request: Request, codes: Optional[str] = Query(default="")):
    return batch_print(request, "material-info", codes)


@router.get("/qr/{material_code}")
def legacy_qr_image(material_code: str):
    return qr_image("material-info", material_code)


@router.get("/{module_key}/material/{material_code}", response_class=HTMLResponse)
def module_material_detail(
    request: Request,
    module_key: str,
    material_code: str,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
):
    cfg = _cfg(module_key)
    item = _material_or_404(cfg, material_code)
    context = _context(request, cfg)
    context["item"] = item
    if cfg.detail_type == "ledger":
        query_end = end_date or date.today()
        query_start = start_date or default_start_date(query_end)
        ledger = None
        ledger_error = ""
        if query_start > query_end:
            ledger_error = "开始日期不能晚于结束日期"
        else:
            try:
                ledger = fetch_ledger(cfg, material_code, query_start, query_end)
            except Exception as exc:
                ledger_error = f"U8 台账查询失败：{exc}"
        context.update(
            {
                "ledger": ledger,
                "ledger_error": ledger_error,
                "start_date": query_start.strftime("%Y-%m-%d"),
                "end_date": query_end.strftime("%Y-%m-%d"),
                "fmt_qty": format_quantity,
            }
        )
        return templates.TemplateResponse("wuping/ledger_detail.html", context)
    return templates.TemplateResponse("material_info/detail.html", context)


@router.get("/{module_key}/print/{material_code}", response_class=HTMLResponse)
def print_label(request: Request, module_key: str, material_code: str):
    cfg = _cfg(module_key)
    item = _material_or_404(cfg, material_code)
    context = _context(request, cfg)
    context.update({"item": item, "cfg": get_label_config(cfg)})
    context["footer_text"] = _footer_text
    return templates.TemplateResponse(f"{_template_prefix(module_key)}/print.html", context)


@router.get("/{module_key}/batch", response_class=HTMLResponse)
def batch(request: Request, module_key: str):
    cfg = _cfg(module_key)
    return templates.TemplateResponse(f"{_template_prefix(module_key)}/batch.html", _context(request, cfg))


@router.get("/{module_key}/batch/print", response_class=HTMLResponse)
def batch_print(request: Request, module_key: str, codes: Optional[str] = Query(default="")):
    cfg = _cfg(module_key)
    code_list = [code.strip() for code in (codes or "").split(",") if code.strip()]
    if not code_list:
        raise HTTPException(status_code=400, detail="未传入任何编码")
    items = by_codes(cfg, code_list)
    if not items:
        raise HTTPException(status_code=404, detail="未找到对应物料")
    context = _context(request, cfg)
    context.update({"items": items, "cfg": get_label_config(cfg)})
    context["footer_text"] = _footer_text
    return templates.TemplateResponse(f"{_template_prefix(module_key)}/batch_print.html", context)


@router.get("/{module_key}/qr/{material_code}")
def qr_image(module_key: str, material_code: str):
    cfg = _cfg(module_key)
    _material_or_404(cfg, material_code)
    qr_url = f"{cfg.qr_base_url.rstrip('/')}/material/{material_code}"
    img = qrcode.make(qr_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
