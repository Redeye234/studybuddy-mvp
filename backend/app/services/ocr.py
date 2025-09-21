import json
import mimetypes
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from mistralai import Mistral
from pypdf import PdfReader, PdfWriter

from ..config import settings

_client: Optional[Mistral] = None


class OCRConfigurationError(RuntimeError):
    pass


def _get_client() -> Mistral:
    global _client
    if _client is None:
        if not settings.MISTRAL_API_KEY:
            raise OCRConfigurationError("MISTRAL_API_KEY is not configured")
        _client = Mistral(api_key=settings.MISTRAL_API_KEY)
    return _client


def _parse_ocr_response(response) -> str:
    try:
        payload = json.loads(response.model_dump_json())
    except Exception:
        return ""

    text_parts: List[str] = []

    if isinstance(payload, dict):
        primary_text = payload.get("text") or payload.get("content")
        if primary_text:
            text_parts.append(primary_text)

        pages = payload.get("pages") or payload.get("chunks") or payload.get("segments")
        if isinstance(pages, list):
            for page in pages:
                if isinstance(page, dict):
                    for key in ("text", "content", "value"):
                        value = page.get(key)
                        if value:
                            text_parts.append(str(value))
                elif isinstance(page, str):
                    text_parts.append(page)
    elif isinstance(payload, str):
        text_parts.append(payload)

    return "\n".join(part.strip() for part in text_parts if part and part.strip())


def _process_with_mistral(file_bytes: bytes, filename: str, mime_type: str) -> str:
    client = _get_client()
    upload = client.files.upload(
        file={"file_name": filename, "content": file_bytes},
        purpose="ocr",
    )
    try:
        response = client.ocr.process(
            document={"type": "file", "file_id": upload.id},
            model=settings.MISTRAL_OCR_MODEL,
            include_image_base64=False,
        )
        return _parse_ocr_response(response)
    finally:
        try:
            client.files.delete(upload.id)
        except Exception:
            pass


def _normalize_pdf_pages(
    pdf_bytes: bytes,
    page_start: Optional[int],
    page_end: Optional[int],
    max_pages: Optional[int],
) -> bytes:
    if not any([page_start, page_end, max_pages]):
        return pdf_bytes

    reader = PdfReader(BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    if total_pages == 0:
        return pdf_bytes

    start = (page_start or 1) - 1
    start = max(0, min(start, total_pages - 1))
    end_boundary = page_end if page_end is not None else total_pages
    end_boundary = max(start + 1, min(end_boundary, total_pages))

    indices = list(range(start, end_boundary))
    if max_pages is not None:
        indices = indices[: max_pages]

    if not indices:
        return pdf_bytes

    writer = PdfWriter()
    for idx in indices:
        writer.add_page(reader.pages[idx])

    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def extract_text_from_pdf(
    file_path: str,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None,
    max_pages: Optional[int] = None,
) -> str:
    pdf_path = Path(file_path)
    file_bytes = pdf_path.read_bytes()
    limited_bytes = _normalize_pdf_pages(file_bytes, page_start, page_end, max_pages)
    return _process_with_mistral(
        limited_bytes,
        filename=pdf_path.name,
        mime_type="application/pdf",
    )


def extract_text_from_image_bytes(data: bytes, filename: Optional[str] = None) -> str:
    name = filename or "image.png"
    mime_type, _ = mimetypes.guess_type(name)
    return _process_with_mistral(data, filename=name, mime_type=mime_type or "image/png")


def extract_text_from_bytes(
    data: bytes,
    filename: Optional[str],
    page_start: Optional[int] = None,
    page_end: Optional[int] = None,
    max_pages: Optional[int] = None,
) -> str:
    name = (filename or "document").lower()

    if name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    if name.endswith(".pdf"):
        normalized = _normalize_pdf_pages(data, page_start, page_end, max_pages)
        return _process_with_mistral(
            normalized,
            filename=filename or "document.pdf",
            mime_type="application/pdf",
        )

    if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")):
        return extract_text_from_image_bytes(data, filename=filename)

    mime_type, _ = mimetypes.guess_type(filename or "document")
    return _process_with_mistral(
        data,
        filename=filename or "document.bin",
        mime_type=mime_type or "application/octet-stream",
    )
