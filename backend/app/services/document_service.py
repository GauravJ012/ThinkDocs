from fastapi import UploadFile, HTTPException
from app.services.pdf_service import save_uploaded_file, delete_file_from_disk
from app.repositories import document_repository


async def upload_document(file: UploadFile):
    """Handle PDF upload: validate, save to disk, store metadata in DB."""

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if file.content_type not in ["application/pdf", "application/octet-stream"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted")

    # Save file to disk
    file_info = await save_uploaded_file(file)

    # Store metadata in database
    document = await document_repository.insert_document(
        filename=file_info["filename"],
        original_filename=file_info["original_filename"],
        file_size=file_info["file_size"],
    )

    return document


async def get_all_documents():
    """Return all uploaded documents."""
    return await document_repository.find_all_documents()


async def get_document(doc_id: int):
    """Return a single document by ID."""
    document = await document_repository.find_document_by_id(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


async def remove_document(doc_id: int):
    """Delete a document: remove from DB and disk."""
    document = await document_repository.find_document_by_id(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from database (chunks cascade-deleted automatically)
    await document_repository.delete_document(doc_id)

    # Delete file from disk
    delete_file_from_disk(document["filename"])