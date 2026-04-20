from fastapi import UploadFile, HTTPException
from app.services.pdf_service import (
    save_uploaded_file,
    delete_file_from_disk,
    extract_text_from_pdf,
    chunk_text,
)
from app.repositories import document_repository, chunk_repository


async def upload_document(file: UploadFile):
    """Handle PDF upload: validate, save, extract text, chunk, and store."""

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

    # Extract text from PDF
    pages = extract_text_from_pdf(file_info["filename"])

    if not pages:
        await document_repository.update_document_status(
            document["id"], status="empty", page_count=0, chunk_count=0
        )
        return document

    # Chunk the extracted text
    chunks = chunk_text(pages)

    # Store chunks in database
    chunk_records = [
        {
            "document_id": document["id"],
            "content": chunk["content"],
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk["page_number"],
        }
        for chunk in chunks
    ]
    await chunk_repository.insert_chunks_batch(chunk_records)

    # Update document with processing results
    await document_repository.update_document_status(
        document["id"],
        status="chunked",
        page_count=len(pages),
        chunk_count=len(chunks),
    )

    # Return updated document
    document = await document_repository.find_document_by_id(document["id"])
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

    await document_repository.delete_document(doc_id)
    delete_file_from_disk(document["filename"])