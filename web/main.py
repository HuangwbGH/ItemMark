import os
import sys
from pathlib import Path

from fastapi import FastAPI

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from routers.admin import router as admin_router  # noqa: E402
from routers.api import router as api_router  # noqa: E402
from routers.module_pages import router as module_pages_router  # noqa: E402
from settings import APP_NAME, WEB_HOST, WEB_PORT  # noqa: E402


app = FastAPI(title=APP_NAME, version="1.0.0")
app.include_router(admin_router)
app.include_router(api_router)
app.include_router(module_pages_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "web.main:app",
        host=WEB_HOST,
        port=WEB_PORT,
        reload=False,
    )

