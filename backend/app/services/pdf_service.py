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
        if text:
            pages.append({
                "page_number": page_num + 1,
                "text": text,
            })

    doc.close()
    return pages


def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """Split extracted pages into overlapping text chunks using sentence-aware grouping.

    Instead of cutting at raw character positions, this function:
    1. Splits text into sentences first
    2. Groups sentences until they approach the target chunk_size
    3. Builds overlap by carrying forward trailing sentences from the previous chunk

    This guarantees no chunk ever starts or ends mid-sentence.

    Args:
        pages: list of {"page_number": int, "text": str}
        chunk_size: target size of each chunk in characters
        overlap: approximate overlap between consecutive chunks in characters

    Returns:
        list of {"content": str, "chunk_index": int, "page_number": int}
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        # Step 1: Split text into sentences
        sentences = _split_into_sentences(text)

        if not sentences:
            continue

        # Step 2: Group sentences into chunks of ~chunk_size characters
        current_chunk = ""
        sentence_buffer = []

        for sentence in sentences:
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_chunk and len(current_chunk) + len(sentence) > chunk_size:
                chunks.append({
                    "content": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                })
                chunk_index += 1

                # Build overlap from recent sentences
                overlap_text = ""
                for prev_sentence in reversed(sentence_buffer):
                    if len(overlap_text) + len(prev_sentence) > overlap:
                        break
                    overlap_text = prev_sentence + " " + overlap_text

                current_chunk = overlap_text.strip() + " " + sentence
                sentence_buffer = [s for s in sentence_buffer if s in overlap_text] + [sentence]
            else:
                current_chunk = (current_chunk + " " + sentence).strip()
                sentence_buffer.append(sentence)

        # Don't forget the last chunk on the page
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "chunk_index": chunk_index,
                "page_number": page_number,
            })
            chunk_index += 1

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences based on punctuation boundaries.

    Handles periods, exclamation marks, question marks, and newlines
    as sentence terminators.
    """
    sentences = []
    current = ""

    for char in text:
        current += char
        if char in ".!?\n" and len(current.strip()) > 1:
            stripped = current.strip()
            if stripped:
                sentences.append(stripped)
            current = ""

    # Add any remaining text as the final sentence
    if current.strip():
        sentences.append(current.strip())

    return sentences