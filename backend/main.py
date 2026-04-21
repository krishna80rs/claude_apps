from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from pathlib import Path
import json

from database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Hobby Tracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


class ProfileIn(BaseModel):
    name: str
    email: EmailStr
    hobbies: list[str]
    interests: list[str]


class ProfileOut(ProfileIn):
    id: int
    created_at: str


@app.get("/")
def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Hobby Tracker API running"}


@app.post("/api/profiles", response_model=ProfileOut, status_code=201)
def create_profile(profile: ProfileIn):
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO profiles (name, email, hobbies, interests) VALUES (?, ?, ?, ?)",
                (profile.name, profile.email,
                 json.dumps(profile.hobbies), json.dumps(profile.interests)),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM profiles WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        except Exception:
            raise HTTPException(status_code=409, detail="Email already registered")

    return _row_to_dict(row)


@app.get("/api/profiles", response_model=list[ProfileOut])
def list_profiles():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM profiles ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


@app.get("/api/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _row_to_dict(row)


@app.delete("/api/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int):
    with get_connection() as conn:
        result = conn.execute(
            "DELETE FROM profiles WHERE id = ?", (profile_id,)
        )
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Profile not found")


def _row_to_dict(row) -> dict:
    d = dict(row)
    d["hobbies"] = json.loads(d["hobbies"])
    d["interests"] = json.loads(d["interests"])
    return d
