import uuid

MEMES = [
    {"id": str(uuid.uuid4()), "category": "focus", "url": "https://i.imgflip.com/30b1gx.jpg"},
    {"id": str(uuid.uuid4()), "category": "focus", "url": "https://i.imgflip.com/1bij.jpg"},
    {"id": str(uuid.uuid4()), "category": "study", "url": "https://i.imgflip.com/26am.jpg"},
]

if __name__ == "__main__":
    # Placeholder: connect DB and insert; for now, print SQL
    for m in MEMES:
        print(
            f"INSERT INTO memes (id, category, url) VALUES ('{m['id']}', '{m['category']}', '{m['url']}');"
        )

