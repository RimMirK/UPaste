import html
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from contextlib import asynccontextmanager

from database import DB
from texts import *

db = DB("database.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.bootstrap()
    yield
    await db.teardown()


app = FastAPI(lifespan=lifespan)


formatter = HtmlFormatter(style="monokai")
PYGMENTS_CSS = formatter.get_style_defs(".highlight")

# =========================
# ROOT
# =========================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return INDEX_HTML.format(base_url=request.base_url)


# =========================
# WEB FORM
# =========================

@app.get("/web", response_class=HTMLResponse)
async def web():
    return WEB_HTML


# =========================
# MACHINE UPLOAD
# =========================

@app.post("/upload")
async def upload(
    request: Request,
    content: str = Form(None),
    ext: str | None = Form(None)
):
    # JSON support
    if request.headers.get("content-type", "").startswith("application/json"):
        data = await request.json()
        content = data.get("content")
        ext = data.get("ext")

    # Raw body support
    if not content:
        body = await request.body()
        if body:
            content = body.decode("utf-8", errors="ignore")

    if not content:
        raise HTTPException(400, "content required")

    ip = request.client.host
    paste_id, delete_token = await db.add_paste(content, ip, ext)

    return JSONResponse({
        "id": paste_id,
        "url": f"{request.base_url}{paste_id}",
        "raw": f"{request.base_url}raw/{paste_id}",
        "token": delete_token,
        "delete": f"{request.base_url}delete/{paste_id}?token={delete_token}",
        "edit": f"{request.base_url}edit/{paste_id}?token={delete_token}",
    })


# =========================
# HUMAN UPLOAD
# =========================

@app.post("/upload/human", response_class=HTMLResponse)
async def upload_human(
    request: Request,
    content: str = Form(...),
    ext: str | None = Form(None)
):
    ip = request.client.host
    paste_id, token = await db.add_paste(content, ip, ext)

    return UPLOAD_HUMAN_HTML.format(
        status='upload',
        base_url=str(request.base_url),
        paste_id=paste_id,
        token=token
    )


# =========================
# RAW
# =========================

@app.get("/raw/{paste_id}")
async def raw(paste_id: str):
    r = await db.get_paste(paste_id)
    if not r:
        return PlainTextResponse(ERROR_404_TEXT, status_code=404)

    content, _ = r
    return PlainTextResponse(content)


# =========================
# VIEW
# =========================

@app.get("/{paste_id}")
async def view(paste_id: str):
    r = await db.get_paste(paste_id)
    if not r:
        return PlainTextResponse(ERROR_404_TEXT, status_code=404)

    content, ext = r
    ext = (ext or "").lower()

    # ================= HTML =================
    if ext == "html":
        return HTMLResponse(content)

    # ================= MARKDOWN =================
    if ext in {"md", "mdown", "markd", "markdown"}:
        rendered = markdown.markdown(
            content,
            extensions=["fenced_code", "codehilite"]
        )

        return HTMLResponse(f"""
        <style>
            body {{ font-family: sans-serif; padding:40px; }}
            {PYGMENTS_CSS}
        </style>
        {rendered}
        """)

    # ================= CODE =================
    try:
        if ext:
            lexer = get_lexer_by_name(ext)
        else:
            lexer = guess_lexer(content)

        highlighted = highlight(content, lexer, formatter)

        return HTMLResponse(f"""
        <style>
            body {{ background:#272822; padding:40px; }}
            {PYGMENTS_CSS}
        </style>
        {highlighted}
        """)

    except ClassNotFound:
        # fallback plain text
        escaped = html.escape(content)
        return HTMLResponse(f"""
        <pre style="font-family: monospace;">
{escaped}
        </pre>
        """)


# =========================
# DELETE
# =========================

@app.delete("/delete/{paste_id}")
@app.get("/delete/{paste_id}")
async def delete(paste_id: str, token: str):
    valid = await db.check_delete_token(paste_id, token)

    if not valid:
        raise HTTPException(403, "Invalid token")

    await db.delete_paste(paste_id)

    return {"status": "deleted"}


@app.get("/edit/{paste_id}", response_class=HTMLResponse)
async def edit_form(paste_id: str, token: str = None):
    r = await db.get_paste(paste_id)
    if not r:
        return PlainTextResponse(ERROR_404_TEXT, status_code=404)

    content, ext = r

    return EDIT_FORM_HTML.format(
        paste_id=paste_id,
        content=html.escape(content),
        ext=ext or '',
        token=token or ''
    )
    
    
@app.post("/edit/{paste_id}")
async def edit_save(
    request: Request,
    paste_id: str,
    token: str,
    content: str = Form(...),
    ext: str | None = Form(None)
):
    valid = await db.check_delete_token(paste_id, token)

    if not valid:
        raise HTTPException(403, "Invalid token")
    
    await db.update_paste(paste_id, content, ext)
    return {"status": "updated", "url": f"{request.base_url}{paste_id}"}


@app.post("/edit/human/{paste_id}")
async def edit_save(
    request: Request,
    paste_id: str,
    token: str = Form(...),
    content: str = Form(...),
    ext: str | None = Form(None)
):
    valid = await db.check_delete_token(paste_id, token)

    if not valid:
        raise HTTPException(403, "Invalid token")
    
    await db.update_paste(paste_id, content, ext)

    return HTMLResponse(UPLOAD_HUMAN_HTML.format(
        status='edited',
        base_url=str(request.base_url).removesuffix('/'),
        paste_id=paste_id,
        token=token,
    ))