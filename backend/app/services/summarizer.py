from typing import List, Dict
import json
import httpx
from ..config import settings


def _ollama_generate(prompt: str, model: str = None, json_mode: bool = False) -> str:
    url = f"{settings.OLLAMA_HOST}/api/generate"
    body = {
        "model": model or settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if json_mode:
        body["format"] = "json"
    try:
        r = httpx.post(url, json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "").strip()
    except Exception:
        return ""


def summarize_text(text: str) -> str:
    if not text or len(text.strip()) < 20:
        return "• Not enough content detected to summarize"
    prompt = (
        "You are a study summarizer. Summarize the following content in 5-7 concise bullet points.\n"
        "Then add a 'Quick Recall' section with 3 short Q&A prompts.\n\n"
        f"Content:\n{text[:8000]}\n\n"
        "Return only the formatted summary and recall section."
    )
    out = _ollama_generate(prompt)
    if not out:
        # Fallback template
        return "\n".join([
            "• Key concept 1",
            "• Key concept 2",
            "• Key concept 3",
            "\nQuick Recall:\n1) Q: ... A: ...\n2) Q: ... A: ...\n3) Q: ... A: ...",
        ])
    return out


def generate_flashcards(text: str) -> List[Dict]:
    if not text or len(text.strip()) < 20:
        return []
    prompt = (
        "Generate 10 study flashcards as JSON array of objects with keys: question, answer, tags (array), difficulty (easy|medium|hard).\n"
        "Keep questions atomic and answers short.\n\n"
        f"Source:\n{text[:6000]}\n\n"
        "Respond with JSON only."
    )
    out = _ollama_generate(prompt, json_mode=True)
    try:
        cards = json.loads(out)
        if isinstance(cards, list):
            return cards[:20]
    except Exception:
        pass
    # Fallback minimal cards
    return [
        {"question": "Define concept X", "answer": "Concept X means ...", "tags": ["core"], "difficulty": "easy"}
    ]
