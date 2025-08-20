import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .deps import verify_token
from .settings import settings

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "content.json"

app = FastAPI(title=settings.APP_NAME)

# Static & templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def read_content() -> dict:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps({"title": "Hello", "body": "Welcome!"}, ensure_ascii=False), encoding="utf-8")
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)

def write_content(payload: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, DATA_FILE)  # atomic on POSIX

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    content = read_content()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": content.get("title", "My Site"),
            "body": content.get("body", ""),
            "env": settings.APP_ENV,
        },
    )

# Public read API
@app.get("/api/content")
async def get_content():
    return read_content()

# Protected write API (send header: X-API-Token: <token>)
@app.post("/api/content", dependencies=[Depends(verify_token)])
async def update_content(payload: dict):
    title: Optional[str] = payload.get("title")
    body: Optional[str] = payload.get("body")
    if title is None and body is None:
        raise HTTPException(status_code=422, detail="Provide 'title' or 'body'")
    current = read_content()
    if title is not None:
        current["title"] = str(title)
    if body is not None:
        current["body"] = str(body)
    write_content(current)
    return JSONResponse({"status": "ok", "content": current})
