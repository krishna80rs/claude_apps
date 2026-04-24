# Hobby System

A dashboard app to register and browse member interests and hobbies — with a full GitHub Actions CI/CD pipeline.

---

## Live URLs

| | URL |
|---|---|
| **App (frontend)** | https://krishna80rs.github.io/claude_apps/ |
| **Backend API** | https://claude-apps-tymn.onrender.com |
| **API Docs (Swagger)** | https://claude-apps-tymn.onrender.com/docs |
| **GitHub Repo** | https://github.com/krishna80rs/claude_apps |

> **Note:** The backend runs on Render free tier and spins down after 15 min of inactivity. The first request after idle may take ~30 seconds to wake up.

---

## How to Test the App

### 1 — Browser UI (quickest)

Open **https://krishna80rs.github.io/claude_apps/**

**Report tab**
- Loads all saved members automatically
- Click **Bio** on any row to expand interests, hobbies, and attached document
- Click **✕** to delete a member
- Click **Refresh** to reload from the backend

**New Entry tab**
- Fill in Name and Email (both required)
- Click interest tags to select (toggle on/off)
- Type hobbies as comma-separated text
- Optionally click the upload area to attach a file from your PC
- Click **Save Profile** → switches to Report to confirm

---

### 2 — Swagger UI (API explorer)

Open **https://claude-apps-tymn.onrender.com/docs**

Interact with every endpoint directly in the browser — no code needed:

| Endpoint | What it does |
|---|---|
| `POST /api/profiles` | Create a new profile (multipart form) |
| `GET /api/profiles` | List all profiles |
| `GET /api/profiles/{id}` | Get one profile by ID |
| `GET /api/profiles/{id}/document` | Download attached document |
| `DELETE /api/profiles/{id}` | Delete a profile |

---

### 3 — PowerShell (quick API test)

```powershell
$BASE = "https://claude-apps-tymn.onrender.com"

# Create a profile
Invoke-WebRequest -Uri "$BASE/api/profiles" -Method POST `
  -Body @{
    name      = "Test User"
    email     = "test@example.com"
    hobbies   = '["cycling","reading"]'
    interests = '["technology","music"]'
  } -UseBasicParsing | Select-Object StatusCode, Content

# List all profiles
Invoke-WebRequest -Uri "$BASE/api/profiles" -UseBasicParsing | Select-Object Content

# Delete a profile (replace 1 with real ID)
Invoke-WebRequest -Uri "$BASE/api/profiles/1" -Method DELETE -UseBasicParsing
```

---

### 4 — curl (Linux / macOS / Git Bash)

```bash
BASE="https://claude-apps-tymn.onrender.com"

# Create
curl -X POST "$BASE/api/profiles" \
  -F "name=Test User" \
  -F "email=test@example.com" \
  -F 'hobbies=["cycling","reading"]' \
  -F 'interests=["technology","music"]'

# List all
curl "$BASE/api/profiles" | python -m json.tool

# Create with file attachment
curl -X POST "$BASE/api/profiles" \
  -F "name=File User" \
  -F "email=fileuser@example.com" \
  -F 'hobbies=["coding"]' \
  -F 'interests=["science"]' \
  -F "document=@/path/to/your/file.pdf"
```

---

## CI/CD Pipeline

Every push to `main` triggers two GitHub Actions workflows:

```
Push to main
  ├── CI — Lint & Test
  │     ├── ruff check  (import sort + lint)
  │     ├── ruff format (code formatting)
  │     └── pytest      (7 tests, including file upload)
  │
  └── CD — Deploy
        ├── Frontend → GitHub Pages  (automatic)
        └── Backend  → Render        (via deploy hook secret)
```

Pull requests are gated — CI must pass before merge.

View pipeline runs: **https://github.com/krishna80rs/claude_apps/actions**

---

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

App runs at **http://localhost:8000**  
Swagger docs at **http://localhost:8000/docs**

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend

The frontend is plain HTML/CSS/JS — open `frontend/index.html` directly in a browser, or serve it:

```bash
cd frontend
python -m http.server 3000
# open http://localhost:3000
```

Update `const API` in `app.js` to point to your local backend (`http://localhost:8000`) when testing locally.

---

## Project Structure

```
claude_apps/
├── .github/workflows/
│   ├── ci.yml          ← lint + test on every push / PR
│   └── cd.yml          ← deploy on push to main
├── backend/
│   ├── main.py         ← FastAPI app (CRUD + file upload)
│   ├── database.py     ← SQLite init + connection
│   ├── conftest.py     ← pytest path setup
│   ├── requirements.txt
│   ├── ruff.toml       ← linter config
│   └── tests/
│       └── test_api.py ← 7 endpoint tests
├── frontend/
│   ├── index.html      ← dashboard layout
│   ├── style.css       ← full UI styles
│   └── app.js          ← report, bio drawer, form, upload
├── render.yaml         ← Render deploy config
└── README.md
```

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Database | SQLite (file-based, zero config) |
| Frontend | Vanilla HTML / CSS / JS |
| CI | GitHub Actions — ruff lint + pytest |
| CD | GitHub Actions → GitHub Pages + Render |
