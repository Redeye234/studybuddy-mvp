from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    plan: str
    created_at: datetime


class NoteOut(BaseModel):
    id: str
    file_url: str
    created_at: datetime


class SummaryOut(BaseModel):
    id: str
    note_id: str
    summary_text: Optional[str]
    flashcards_json: Optional[list]
    created_at: datetime


class FocusRoomIn(BaseModel):
    name: str
    type: str


class FocusRoomOut(BaseModel):
    id: str
    name: str
    type: str
    status: str
    created_at: datetime


class MemeOut(BaseModel):
    id: str
    category: str
    url: str
    created_at: datetime


class SubscriptionOut(BaseModel):
    plan: str
    expires_at: Optional[datetime]

