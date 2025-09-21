from fastapi import APIRouter
import random

router = APIRouter()

MEMES = [
    {"id": "1", "category": "focus", "url": "https://i.imgflip.com/30b1gx.jpg"},
    {"id": "2", "category": "focus", "url": "https://i.imgflip.com/1bij.jpg"},
]


@router.get("/memes/random")
def random_meme(category: str = "focus"):
    candidates = [m for m in MEMES if m["category"] == category]
    return random.choice(candidates) if candidates else random.choice(MEMES)


@router.post("/memes/{meme_id}/share")
def share_meme(meme_id: str):
    return {"ok": True, "meme_id": meme_id, "shared": True}

