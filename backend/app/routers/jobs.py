from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import UploadJob
from ..deps import get_current_user

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = db.get(UploadJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # In a multi-tenant system, we would check ownership. Here we return raw record.
    return {
        "id": str(job.id),
        "status": job.status,
        "error": job.error,
        "note_id": str(job.note_id) if job.note_id else None,
        "created_at": job.created_at,
    }

