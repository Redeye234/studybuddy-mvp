from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..deps import get_current_user

router = APIRouter()


@router.get("/subscription")
def get_subscription(user: User = Depends(get_current_user)):
    return {"plan": user.plan, "expires_at": None}


@router.post("/subscription/activate")
def activate_subscription(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.plan = "tier_premium"
    db.add(user)
    db.commit()
    return {"plan": user.plan, "expires_at": None}


@router.post("/subscription/cancel")
def cancel_subscription(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.plan = "tier_free"
    db.add(user)
    db.commit()
    return {"plan": user.plan, "expires_at": None}
