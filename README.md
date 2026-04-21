# Hobby Tracker

A lightweight app to store user interests and hobbies, with a GitHub Actions CI/CD pipeline modelled after ADO.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12 + FastAPI |
| Database | SQLite (file-based, zero config) |
| Frontend | Vanilla HTML/CSS/JS |
| CI | GitHub Actions — lint + test on every PR |
| CD | GitHub Actions — deploy on push to `main` |

## CI/CD Pipeline

```
PR opened
  └── ci.yml
        ├── lint  (ruff check + format)
        └── test  (pytest) ← blocked until lint passes

Push to main
  └── cd.yml
        ├── deploy-frontend → GitHub Pages
        ├── deploy-backend  → Render (via deploy hook)
        └── notify          → Job summary in GitHub UI
```

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API available at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

### Run Tests

```bash
cd backend
pytest tests/ -v
```

## Deploying

### Frontend → GitHub Pages

1. In your repo: **Settings → Pages → Source → GitHub Actions**
2. Push to `main` — the `cd.yml` workflow deploys automatically

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Set **Build Command:** `pip install -r backend/requirements.txt`
3. Set **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Copy the **Deploy Hook URL** from Render → add as GitHub secret `RENDER_DEPLOY_HOOK_URL`
5. Push to `main` — CD pipeline triggers the Render deploy automatically

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/profiles` | Create a profile |
| GET | `/api/profiles` | List all profiles |
| GET | `/api/profiles/{id}` | Get one profile |
| DELETE | `/api/profiles/{id}` | Delete a profile |
