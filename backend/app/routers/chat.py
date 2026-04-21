from fastapi import APIRouter
from app.models.chat_models import QuestionRequest, AnswerResponse
from app.services.rag_service import retrieve_relevant_chunks, ask_question

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest):
    """Ask a question and get an AI-generated answer based on uploaded documents."""
    result = await ask_question(request.question)
    return result


@router.post("/retrieve")
async def retrieve_chunks(request: QuestionRequest):
    """Debug endpoint: retrieve relevant chunks without LLM answer."""
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