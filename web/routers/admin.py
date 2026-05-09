from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.module_config_service import list_module_configs
from settings import PROJECT_ROOT


router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "web" / "templates"))


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "admin/index.html",
        {"request": request, "modules": [cfg.public_dict() for cfg in list_module_configs()]},
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_index(request: Request):
    return index(request)


@router.get("/admin/sync", response_class=HTMLResponse)
def admin_sync(request: Request):
    return templates.TemplateResponse(
        "admin/sync.html",
        {"request": request, "modules": [cfg.public_dict() for cfg in list_module_configs()]},
    )
