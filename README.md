# Url-shortner
Url shortner website
Boom — I’ve built you a **ready-to-run URL Shortener** with a clean web UI, JSON API, SQLite storage, and a **single-command Docker start**. Grab it here:

**[Download the ZIP](sandbox:/mnt/data/url-shortener-fastapi.zip)**

### What’s inside

* **FastAPI app** with routes:

  * `GET /` web form (Tailwind UI)
  * `POST /shorten` (form) → returns short link
  * `POST /api/shorten` (JSON) → `{ code, short_url }`
  * `GET /{code}` → redirects to original URL
  * `GET /health` → simple health check
* **SQLite persistence** (`data/urlshort.db`) with Base62 codes
* **Extras for UX**: Copy button + QR code
* **Dockerfile + docker-compose.yml** → one-command start
* **README.md** with quick deploy notes (Render), recording tips
* **GitHub-ready** structure with `.gitignore` and `.env.example`

### How to run (during the assessment)

**Option A — One command (recommended for extra credit):**

```bash
docker-compose up --build
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and test:

* Paste any long URL → **Shorten**
* Try the short link (e.g., `http://127.0.0.1:8000/abc`)
* (Optional) Test API:

```bash
curl -X POST http://127.0.0.1:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com"}'
```

**Option B — Run without Docker:**

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### What to submit in the Google Form

* **GitHub repo link (public)** — push the project as-is.
* **Screen recording (1–2 min)** — demo `GET /`, create a short link, click it to show redirect, open `/health`, optionally show the curl API call.
* **Hosted demo link (optional bonus)** — deploy with Render (instructions in README). Set `BASE_URL` to your public URL.

If you want me to tweak branding, add click analytics, custom slugs, or a nicer dashboard page before you submit, say the word and I’ll ship an updated zip immediately.
