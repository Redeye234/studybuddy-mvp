from celery import shared_task
from ..services.ocr import extract_text_from_pdf
from ..services.summarizer import summarize_text, generate_flashcards
from ..db import SessionLocal
from ..models import Note, Summary, UploadJob
from ..services.storage import key_from_url, download_object_to_path
import tempfile


@shared_task
def ocr_and_summarize(job_id: str, note_id: str, page_start: int | None = None, page_end: int | None = None, max_pages: int | None = None):
    db = SessionLocal()
    try:
        job = db.get(UploadJob, job_id)
        note = db.get(Note, note_id)
        if not note:
            if job:
                job.status = "error"; job.error = "note_not_found"; db.add(job); db.commit()
            return {"error": "note_not_found"}

        text = (note.raw_text or "").strip()
        if not text:
            # download from S3 and OCR
            key = key_from_url(note.file_url)
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = f"{tmpdir}/note.pdf"
                download_object_to_path(key, tmp_path)
                text = extract_text_from_pdf(tmp_path, page_start=page_start, page_end=page_end, max_pages=max_pages)

        summary_text = summarize_text(text)
        flashcards = generate_flashcards(text)

        existing = db.query(Summary).filter(Summary.note_id == note.id).first()
        if existing:
            existing.summary_text = summary_text
            existing.flashcards_json = flashcards
            db.add(existing)
            db.commit()
            sid = existing.id
        else:
            s = Summary(note_id=note.id, summary_text=summary_text, flashcards_json=flashcards)
            db.add(s)
            db.commit()
            db.refresh(s)
            sid = s.id

        if job:
            job.status = "completed"
            job.error = None
            db.add(job)
            db.commit()

        return {"note_id": str(note.id), "summary_id": str(sid)}
    except Exception as e:
        if 'db' in locals():
            job = db.get(UploadJob, job_id) if job_id else None
            if job:
                job.status = "error"; job.error = str(e)
                db.add(job); db.commit()
        return {"error": str(e)}
    finally:
        db.close()
