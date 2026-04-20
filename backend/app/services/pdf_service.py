import os
import uuid
import fitz  # PyMuPDF
from fastapi import UploadFile
from app.config import settings


async def save_uploaded_file(file: UploadFile) -> dict:
    """Save the uploaded PDF to disk and return file info."""

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_size": len(content),
        "file_path": file_path,
    }


def delete_file_from_disk(filename: str):
    """Delete a PDF file from the uploads directory."""
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def extract_text_from_pdf(filename: str) -> list[dict]:
    """Extract text from a PDF file, page by page.

    Returns a list of dicts: [{"page_number": 1, "text": "..."}, ...]
    """
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    doc = fitz.open(file_path)

    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if text:  # skip empty pages
            pages.append({
                "page_number": page_num + 1,  # 1-indexed for users
                "text": text,
            })

    doc.close()
    return pages


def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """Split extracted pages into overlapping text chunks.

    Args:
        pages: list of {"page_number": int, "text": str}
        chunk_size: target size of each chunk in characters
        overlap: number of overlapping characters between chunks

    Returns:
        list of {"content": str, "chunk_index": int, "page_number": int}
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at a sentence boundary (period, newline)
            if end < len(text):
                # Look for the last sentence-ending punctuation within the chunk
                last_period = text.rfind(". ", start, end)
                last_newline = text.rfind("\n", start, end)
                break_point = max(last_period, last_newline)

                if break_point > start:
                    end = break_point + 1  # include the period/newline

            chunk_content = text[start:end].strip()

            if chunk_content:  # skip empty chunks
                chunks.append({
                    "content": chunk_content,
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                })
                chunk_index += 1

            # Move forward by (chunk_size - overlap) to create overlap
            start = start + chunk_size - overlap

    return chunks