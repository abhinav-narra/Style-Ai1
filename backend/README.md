# AI Fashion Stylist Backend (FastAPI)

Production-oriented FastAPI backend scaffold for an AI fashion stylist.

## Features
- OpenCV Haar-cascade face detection (lazy-loaded; endpoint fails gracefully if missing)
- Skin tone detection module (face-region average color + tone bucket)
- Outfit scoring engine (rule-based scoring + explanation)
- Diversity engine (reduces repetition using user history similarity)
- LLM recommendation module (OpenAI-compatible via HTTP; falls back to template)
- JSON safe parsing utilities
- User history memory (SQLite)
- JSON logging + request correlation id

## Quickstart
From the workspace root:

```bash
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt
.venv\Scripts\uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Open docs at `http://localhost:8000/docs`.

## Configuration
Environment variables (all optional):
- `APP_NAME` (default: `ai-fashion-stylist`)
- `APP_ENV` (`dev`/`prod`, default: `dev`)
- `LOG_LEVEL` (default: `INFO`)
- `DATABASE_PATH` (default: `backend/data/app.db`)
- `OPENAI_API_KEY` (optional; enables real LLM calls)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)

