\
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

# ---------- Paths & Config ----------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "urlshort.db"
DATA_DIR.mkdir(exist_ok=True, parents=True)

BASE_URL = os.getenv("BASE_URL", f"http://127.0.0.1:{os.getenv('PORT', '8000')}")

# ---------- App ----------
app = FastAPI(title="URL Shortener", version="1.0.0")
app.mount("/static", StaticFiles(directory=ROOT_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(ROOT_DIR / "app" / "templates"))

# ---------- Database ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT NOT NULL UNIQUE,
                code TEXT UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                clicks INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()

@app.on_event("startup")
def on_startup():
    init_db()

# ---------- Base62 helpers ----------
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    s = []
    base = len(ALPHABET)
    while n > 0:
        n, r = divmod(n, base)
        s.append(ALPHABET[r])
    return "".join(reversed(s))

# ---------- Core operations ----------
def get_or_create_code(long_url: str) -> str:
    long_url = long_url.strip()
    if not long_url:
        raise ValueError("URL cannot be empty")
    # Normalize: add scheme if missing
    if not (long_url.startswith("http://") or long_url.startswith("https://")):
        long_url = "http://" + long_url

    with get_conn() as conn:
        # Existing?
        cur = conn.execute("SELECT code FROM urls WHERE long_url = ?", (long_url,))
        row = cur.fetchone()
        if row and row["code"]:
            return row["code"]

        # Insert to get id, then generate code from id
        cur = conn.execute("INSERT OR IGNORE INTO urls (long_url) VALUES (?)", (long_url,))
        conn.commit()
        # Retrieve id for the (possibly existing) row
        cur = conn.execute("SELECT id FROM urls WHERE long_url = ?", (long_url,))
        row = cur.fetchone()
        if not row:
            raise RuntimeError("Failed to insert/select URL")
        new_id = row["id"]
        code = base62_encode(new_id)
        conn.execute("UPDATE urls SET code = ? WHERE id = ?", (code, new_id))
        conn.commit()
        return code

def resolve_code(code: str) -> Optional[str]:
    with get_conn() as conn:
        cur = conn.execute("SELECT long_url FROM urls WHERE code = ?", (code,))
        row = cur.fetchone()
        return row["long_url"] if row else None

def increment_click(code: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
        conn.commit()

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, created: Optional[str] = None):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "created": created, "base_url": BASE_URL},
    )

@app.post("/shorten", response_class=HTMLResponse)
def shorten(request: Request, long_url: str = Form(...)):
    try:
        code = get_or_create_code(long_url)
        short_url = f"{BASE_URL.rstrip('/')}/{code}"
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "created": short_url,
                "base_url": BASE_URL,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# JSON API
@app.post("/api/shorten")
async def api_shorten(payload: dict):
    long_url = payload.get("long_url", "")
    try:
        code = get_or_create_code(long_url)
        short_url = f"{BASE_URL.rstrip('/')}/{code}"
        return {"code": code, "short_url": short_url}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@app.get("/{code}")
def follow(code: str):
    long_url = resolve_code(code)
    if not long_url:
        raise HTTPException(status_code=404, detail="Short code not found")
    increment_click(code)
    return RedirectResponse(long_url, status_code=307)
