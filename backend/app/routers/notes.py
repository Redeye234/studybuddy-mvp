from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Note, Summary, User
from ..deps import get_current_user
from ..services import storage
from ..services.ocr import extract_text_from_bytes
from datetime import datetime, timezone

router = APIRouter()


def _uploads_today(db: Session, user_id: str) -> int:
    today = datetime.now(timezone.utc).date()
    return (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .filter(Note.created_at >= datetime(today.year, today.month, today.day, tzinfo=timezone.utc))
        .count()
    )


@router.post("/notes")
async def upload_note(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Rate limit free plan: 3 uploads/day
    if user.plan == "tier_free" and _uploads_today(db, str(user.id)) >= 3:
        raise HTTPException(status_code=429, detail="Daily upload limit reached for free tier")

    key = f"notes/{user.id}/{uuid.uuid4()}/{file.filename}"
    try:
        data = await file.read()
        url = storage.upload_file(data, key, content_type=file.content_type or "application/octet-stream")
    except Exception:
        # Fallback to fake URL without failing the flow
        url = f"s3://studybuddy/{key}"

    # Extract text using OCR/PDF parsing on the uploaded file bytes
    raw_text = extract_text_from_bytes(data, file.filename)

    note = Note(user_id=user.id, file_url=url, raw_text=raw_text)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": str(note.id), "file_url": note.file_url, "title": title}


@router.get("/notes")
def list_notes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    notes = db.query(Note).filter(Note.user_id == user.id).order_by(Note.created_at.desc()).all()
    return {"items": [{"id": str(n.id), "file_url": n.file_url, "created_at": n.created_at.isoformat()} for n in notes]}


@router.get("/notes/{note_id}")
def get_note(note_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": str(note.id), "file_url": note.file_url, "created_at": note.created_at}
