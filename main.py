# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, StreamingResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
# import re
# from datetime import datetime, timedelta
# import os
# from PIL import Image, ImageDraw, ImageFont
# import io
# import psycopg2
# import urllib.parse as urlparse

# app = FastAPI()

# # Allow CORS for frontend JS
# app.add_middleware(
    # CORSMiddleware,
    # allow_origins=["*"],
    # allow_methods=["*"],
    # allow_headers=["*"],
# )

# # Setup template and static files
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# # Regex for validating inputs
# USERNAME_RE = re.compile(r"^[a-zA-ZÀ-ỹ\s]{1,20}$")
# COMMENT_RE = re.compile(r"^[a-zA-Z0-9À-ỹ\s.,;:!?()\[\]\-_\'\"/\\]{1,300}$")

# # PostgreSQL DB setup (fixed credentials)
# DATABASE_URL = "postgresql://comment_user:WQ2bdJW51aIrAC1Tgu7noky0KxKyLFPz@dpg-d1urm3ruibrs738p9vsg-a.oregon-postgres.render.com/comment_db_3wtv"
# urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse(DATABASE_URL)

# conn_args = {
    # 'dbname': url.path[1:],
    # 'user': url.username,
    # 'password': url.password,
    # 'host': url.hostname,
    # 'port': url.port
# }

# def init_db():
    # with psycopg2.connect(**conn_args) as conn:
        # with conn.cursor() as cur:
            # cur.execute('''
                # CREATE TABLE IF NOT EXISTS comments (
                    # id SERIAL PRIMARY KEY,
                    # username TEXT NOT NULL,
                    # content TEXT NOT NULL,
                    # timestamp TIMESTAMP NOT NULL
                # );
            # ''')
            # conn.commit()

# init_db()

# @app.get("/comment", response_class=HTMLResponse)
# async def comment_page(request: Request):
    # return templates.TemplateResponse("comment.html", {"request": request})

# @app.get("/")
# async def image_home():
    # with psycopg2.connect(**conn_args) as conn:
        # with conn.cursor() as cur:
            # cur.execute("SELECT username, content, timestamp FROM comments ORDER BY timestamp DESC LIMIT 32")
            # rows = cur.fetchall()

    # width, height = 800, max(300, len(rows) * 18 + 20)
    # image = Image.new("RGB", (width, height), color=(255, 255, 255))
    # draw = ImageDraw.Draw(image)

    # for y in range(0, height, 20):
        # draw.line((0, y, width, y), fill=(220, 220, 220))

    # try:
        # font = ImageFont.truetype("Roboto-Regular.ttf", 14)
    # except IOError:
        # font = ImageFont.load_default()

    # y = 10
    # for row in reversed(rows):
        # timestamp, username, content = row[2], row[0], row[1]
        # text = f"[{timestamp}]<{username}>: {content}"
        # draw.text((10, y), text, font=font, fill=(0, 0, 0))
        # y += 18

    # img_bytes = io.BytesIO()
    # image.save(img_bytes, format="PNG")
    # img_bytes.seek(0)
    # return StreamingResponse(img_bytes, media_type="image/png")

# @app.post("/submit")
# async def submit_comment(username: str = Form(...), content: str = Form(...)):
    # username = username.strip()
    # content = content.strip()

    # if not USERNAME_RE.fullmatch(username):
        # return {"status": "error", "message": "Tên không hợp lệ."}
    # if not COMMENT_RE.fullmatch(content):
        # return {"status": "error", "message": "Bình luận không hợp lệ."}

    # now = datetime.now()

    # with psycopg2.connect(**conn_args) as conn:
        # with conn.cursor() as cur:
            # cur.execute("SELECT timestamp FROM comments WHERE username = %s ORDER BY timestamp DESC LIMIT 1", (username,))
            # row = cur.fetchone()
            # if row:
                # try:
                    # last_time = row[0]
                    # if now - last_time < timedelta(seconds=5):
                        # return {"status": "error", "message": "Bạn phải chờ 5 giây giữa các bình luận."}
                # except Exception:
                    # pass

            # cur.execute("INSERT INTO comments (username, content, timestamp) VALUES (%s, %s, %s)", (username, content, now))
            # cur.execute("DELETE FROM comments WHERE id NOT IN (SELECT id FROM comments ORDER BY timestamp DESC LIMIT 32)")
            # conn.commit()

    # return {"status": "ok"}


from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import re
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw, ImageFont
import io
import psycopg2
import urllib.parse as urlparse
import time
import requests

app = FastAPI()

# Allow CORS for frontend JS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup template and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Regex for validating inputs
USERNAME_RE = re.compile(r"^[a-zA-ZÀ-ỹ\s]{1,20}$")
COMMENT_RE = re.compile(r"^[a-zA-Z0-9À-ỹ\s.,;:!?()\[\]\-_\'\"/\\]{1,300}$")

# PostgreSQL DB setup (fixed credentials)
DATABASE_URL = "postgresql://comment_user:WQ2bdJW51aIrAC1Tgu7noky0KxKyLFPz@dpg-d1urm3ruibrs738p9vsg-a.oregon-postgres.render.com/comment_db_3wtv"
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(DATABASE_URL)

conn_args = {
    'dbname': url.path[1:],
    'user': url.username,
    'password': url.password,
    'host': url.hostname,
    'port': url.port
}

def init_db():
    with psycopg2.connect(**conn_args) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL
                );
            ''')
            conn.commit()

init_db()

@app.get("/comment", response_class=HTMLResponse)
async def comment_page(request: Request):
    return templates.TemplateResponse("comment.html", {"request": request})

@app.get("/ubort")
async def ubort():
    time.sleep(5)
    TARGET_URL = "https://ubort.onrender.com"
    try:
        response = requests.get(TARGET_URL, timeout=5)
        return {"fetched_url": TARGET_URL, "status_code": response.status_code}
    except requests.RequestException as e:
        return {"fetched_url": TARGET_URL, "error": str(e)}

@app.get("/")
async def image_home():
    with psycopg2.connect(**conn_args) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username, content, timestamp FROM comments ORDER BY timestamp DESC LIMIT 32")
            rows = cur.fetchall()

    width, height = 800, max(300, len(rows) * 18 + 20)
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    for y in range(0, height, 20):
        draw.line((0, y, width, y), fill=(220, 220, 220))

    try:
        font = ImageFont.truetype("Roboto-Regular.ttf", 14)
    except IOError:
        font = ImageFont.load_default()

    y = 10
    for row in reversed(rows):
        timestamp, username, content = row[2], row[0], row[1]
        text = f"[{timestamp}]<{username}>: {content}"
        lines = []
        max_width = 780  # allow 10px margin on left and right
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        for l in lines:
            draw.text((10, y), l, font=font, fill=(0, 0, 0))
            y += 18

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return StreamingResponse(img_bytes, media_type="image/png")

@app.post("/submit")
async def submit_comment(username: str = Form(...), content: str = Form(...)):
    username = username.strip()
    content = content.strip()

    if not USERNAME_RE.fullmatch(username):
        return {"status": "error", "message": "Tên không hợp lệ."}
    if not COMMENT_RE.fullmatch(content):
        return {"status": "error", "message": "Bình luận không hợp lệ."}

    now = datetime.now()

    with psycopg2.connect(**conn_args) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT timestamp FROM comments WHERE username = %s ORDER BY timestamp DESC LIMIT 1", (username,))
            row = cur.fetchone()
            if row:
                try:
                    last_time = row[0]
                    if now - last_time < timedelta(seconds=5):
                        return {"status": "error", "message": "Bạn phải chờ 5 giây giữa các bình luận."}
                except Exception:
                    pass

            cur.execute("INSERT INTO comments (username, content, timestamp) VALUES (%s, %s, %s)", (username, content, now))
            cur.execute("DELETE FROM comments WHERE id NOT IN (SELECT id FROM comments ORDER BY timestamp DESC LIMIT 32)")
            conn.commit()

    return {"status": "ok"}
