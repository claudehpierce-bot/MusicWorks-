"""MusicWorks™ V5 — Lyrics ingestion for the Campaign Wizard.

Extracts plain lyrics text from pasted input, .txt, .docx, or .pdf uploads.
Never raises — extraction failures return an error string so the wizard can
fall back to manual paste instead of crashing the step.
"""
import io
import re


def extract_from_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").strip()


def extract_from_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_from_pdf(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def clean_lyrics_text(text: str) -> str:
    """Normalize whitespace and collapse runs of blank lines."""
    if not text:
        return ""
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return cleaned.strip()


_EXTRACTORS = {
    "txt": extract_from_txt,
    "docx": extract_from_docx,
    "pdf": extract_from_pdf,
}


def extract_lyrics(uploaded_file) -> "tuple[str, str | None]":
    """Dispatch by uploaded_file.name extension. Returns (text, error).
    On success error is None; on failure text is '' and error explains why,
    so the caller can fall back to manual paste."""
    name = getattr(uploaded_file, "name", "") or ""
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    extractor = _EXTRACTORS.get(ext)
    if not extractor:
        return "", f"Unsupported lyrics file type '.{ext}'. Please use .txt, .docx, .pdf, or paste lyrics directly."
    try:
        data = uploaded_file.read()
        text = extractor(data)
        if not text:
            return "", f"No text could be extracted from this .{ext} file. Try pasting the lyrics directly."
        return clean_lyrics_text(text), None
    except Exception as e:
        return "", f"Could not read this .{ext} file: {e}"
