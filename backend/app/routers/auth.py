from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
import uuid

router = APIRouter()


class EmailIn(BaseModel):
    email: str


@router.post("/auth/email")
def auth_email(payload: EmailIn, db: Session = Depends(get_db)):
    # Find or create user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(email=payload.email, plan="tier_free")
        db.add(user)
        db.commit()
        db.refresh(user)
    token = f"fake.{user.id}"
    return {"token": token, "user": {"id": str(user.id), "email": user.email, "plan": user.plan}}


@router.get("/me")
def me(db: Session = Depends(get_db)):
    # For simplicity in MVP, return a placeholder if no auth in UI flow
    return {"ok": True}
