from fastapi import APIRouter
from app.models.chat_models import QuestionRequest
from app.services.rag_service import retrieve_relevant_chunks

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/retrieve")
async def retrieve_chunks(request: QuestionRequest):
    """Test endpoint: retrieve relevant chunks without LLM answer.
    This will be replaced with the full Q&A endpoint in Step 7.
    """
    chunks = await retrieve_relevant_chunks(request.question)

    return {
        "question": request.question,
        "chunks_found": len(chunks),
        "chunks": [
            {
                "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "page_number": chunk["page_number"],
                "document": chunk["original_filename"],
                "similarity": round(chunk["similarity"], 4),
            }
            for chunk in chunks
        ],
    }