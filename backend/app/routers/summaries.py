from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Note, Summary, User
from ..deps import get_current_user
from ..services.summarizer import summarize_text, generate_flashcards
from ..models import UploadJob
from ..tasks.tasks import ocr_and_summarize
from pydantic import BaseModel

router = APIRouter()


class SummarizeIn(BaseModel):
    page_start: int | None = None
    page_end: int | None = None
    max_pages: int | None = None


@router.post("/notes/{note_id}/summarize")
def summarize(note_id: str, payload: SummarizeIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    job = UploadJob(user_id=user.id, note_id=note.id, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    ocr_and_summarize.delay(str(job.id), str(note.id), payload.page_start, payload.page_end, payload.max_pages)
    return {"queued": True, "job_id": str(job.id)}


@router.get("/notes/{note_id}/summary")
def get_summary(note_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    s = db.query(Summary).filter(Summary.note_id == note.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {
        "id": str(s.id),
        "note_id": str(note.id),
        "summary_text": s.summary_text,
        "flashcards_json": s.flashcards_json,
        "created_at": s.created_at,
    }
