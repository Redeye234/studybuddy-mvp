from typing import Optional
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from .models import User


def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    # Expect Authorization: Bearer fake.{user_id}
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1]
    parts = token.split(".")
    if len(parts) != 2 or parts[0] != "fake":
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = parts[1]
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

