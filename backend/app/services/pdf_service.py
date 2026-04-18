import os
import uuid
from fastapi import UploadFile
from app.config import settings


async def save_uploaded_file(file: UploadFile) -> dict:
    """Save the uploaded PDF to disk and return file info."""

    # Generate a unique filename to avoid collisions
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Ensure the uploads directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Read file content and save to disk
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