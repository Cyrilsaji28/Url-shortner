# URL Shortener (FastAPI)

A clean, Docker-ready URL shortener with a minimalist web UI.

## Features
- Paste a long URL and get a short code like `http://127.0.0.1:8000/abc`.
- Redirect from short code to the original URL.
- Stores mappings in **SQLite** (`data/urlshort.db`) for persistence.
- JSON API: `POST /api/shorten` with `{"long_url": "https://..."}` returns `{ code, short_url }`.
- Copy button + QR code on the UI.
- Health endpoint: `GET /health`.

---

## 1) One-Command Start (Docker)
```bash
docker-compose up --build
```
Then open: http://127.0.0.1:8000

> The database persists in the `data/` folder.

### Environment
- `BASE_URL` controls the base used when generating short links (defaults to `http://127.0.0.1:8000`).
- For deployment, set `BASE_URL` to your public domain.

---

## 2) Run Locally (without Docker)
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open http://127.0.0.1:8000

---

## 3) API Example
```bash
curl -X POST http://127.0.0.1:8000/api/shorten   -H "Content-Type: application/json"   -d '{"long_url": "https://example.com"}'
```

Response:
```json
{"code":"1","short_url":"http://127.0.0.1:8000/1"}
```

---

## 4) Quick Deploy (Render free tier)
1. Push this repo to **GitHub** (public).
2. Create a new **Web Service** on [Render](https://render.com/), connect the repo.
3. Runtime: **Docker** (uses the provided Dockerfile).
4. Set `BASE_URL` env var to your Render URL (e.g., `https://your-app.onrender.com`).
5. Save & Deploy.

Alternative hosts: Railway, Fly.io, AWS Lightsail, ECS Fargate, etc.

---

## 5) Project Structure
```
url-shortener-fastapi/
├─ app/
│  ├─ main.py
│  ├─ static/
│  │  └─ script.js
│  └─ templates/
│     ├─ base.html
│     └─ index.html
├─ data/                # SQLite DB stored here
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

---

## 6) Recording Tips (Loom / any tool, 1–2 minutes)
- Open http://127.0.0.1:8000
- Paste a long URL, click **Shorten**.
- Click **Open** to show redirection works.
- Show **/health** responding.
- (Optional) Show `POST /api/shorten` in a tool like curl or hoppscotch/postman.
- Stop recording; share the view-only link.

---

## 7) Notes
- If a URL is shortened more than once, you’ll get the original code back (idempotent behavior).
- Codes are Base62 of the row ID. This keeps it deterministic and fast.
- Redirect uses status **307 Temporary Redirect** to preserve method.
