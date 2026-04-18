from fastapi import APIRouter, UploadFile, File
from app.models.document_models import DocumentResponse
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document."""
    return await document_service.upload_document(file)


@router.get("", response_model=list[DocumentResponse])
async def list_documents():
    """List all uploaded documents."""
    return await document_service.get_all_documents()


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int):
    """Get a specific document by ID."""
    return await document_service.get_document(doc_id)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: int):
    """Delete a document and all its chunks."""
    await document_service.remove_document(doc_id)