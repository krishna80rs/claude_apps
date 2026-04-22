import base64
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

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


class ProfileOut(BaseModel):
    id: int
    name: str
    email: str
    hobbies: list[str]
    interests: list[str]
    document_name: Optional[str]
    created_at: str


@app.get("/")
def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Hobby Tracker API running"}


@app.post("/api/profiles", response_model=ProfileOut, status_code=201)
async def create_profile(
    name: str = Form(...),
    email: str = Form(...),
    hobbies: str = Form(...),
    interests: str = Form(...),
    document: Optional[UploadFile] = File(None),
):
    hobbies_list = json.loads(hobbies)
    interests_list = json.loads(interests)

    doc_name = None
    doc_data = None
    if document and document.filename:
        doc_name = document.filename
        doc_data = await document.read()

    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """INSERT INTO profiles
                   (name, email, hobbies, interests, document_name, document_data)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    name,
                    email,
                    json.dumps(hobbies_list),
                    json.dumps(interests_list),
                    doc_name,
                    doc_data,
                ),
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


@app.get("/api/profiles/{profile_id}/document")
def download_document(profile_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT document_name, document_data FROM profiles WHERE id = ?",
            (profile_id,),
        ).fetchone()
    if not row or not row["document_data"]:
        raise HTTPException(status_code=404, detail="No document attached")
    return Response(
        content=bytes(row["document_data"]),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{row["document_name"]}"'
        },
    )


@app.delete("/api/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int):
    with get_connection() as conn:
        result = conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Profile not found")


def _row_to_dict(row) -> dict:
    d = dict(row)
    d["hobbies"] = json.loads(d["hobbies"])
    d["interests"] = json.loads(d["interests"])
    d.pop("document_data", None)
    return d
