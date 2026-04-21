from openai import OpenAI
from app.config import settings
from app.services.embedding_service import get_query_embedding
from app.repositories import chunk_repository

client = OpenAI(api_key=settings.OPENAI_API_KEY)

LLM_MODEL = "gpt-4o-mini"


async def retrieve_relevant_chunks(question: str, top_k: int = 5) -> list[dict]:
    """Find the most relevant chunks for a user's question."""

    query_embedding = await get_query_embedding(question)

    similar_chunks = await chunk_repository.find_similar_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
    )

    return similar_chunks


async def ask_question(question: str, top_k: int = 5) -> dict:
    """Full RAG pipeline: retrieve relevant chunks and generate an answer.

    1. Embed the question
    2. Retrieve top-K similar chunks from pgvector
    3. Build a prompt with the chunks as context
    4. Call GPT-4o-mini to generate an answer
    5. Return the answer with source citations
    """

    # Step 1 & 2: Retrieve relevant chunks
    chunks = await retrieve_relevant_chunks(question, top_k)

    # If no chunks found or very low similarity, acknowledge it
    if not chunks or chunks[0]["similarity"] < 0.3:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents to answer your question. Please make sure you've uploaded documents that contain information related to your question.",
            "sources": [],
        }

    # Step 3: Build the prompt with retrieved context
    context = _build_context(chunks)
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(question, context)

    # Step 4: Call GPT-4o-mini
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    answer = response.choices[0].message.content

    # Step 5: Build source citations
    sources = [
        {
            "content": chunk["content"],
            "page_number": chunk["page_number"],
            "document_name": chunk["original_filename"],
            "similarity": round(chunk["similarity"], 4),
        }
        for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }


def _build_system_prompt() -> str:
    """Build the system prompt that instructs the LLM how to behave."""

    return """You are ThinkDocs, an AI assistant that answers questions based ONLY on the provided document context.

Rules you MUST follow:
1. Read ALL provided context sources carefully before answering. The answer may be in any of the provided sources, not just the first one.
2. Answer ONLY based on the provided context. Do not use any external knowledge.
3. If the context does not contain enough information to answer the question, say "The provided documents do not contain enough information to answer this question."
4. When referencing information, cite the source document name and page number in this format: [Source: filename, Page X]
5. Keep your answers clear, concise, and well-structured.
6. If the question is ambiguous, interpret it in the most reasonable way based on the available context.
7. Do not make up or infer information that is not explicitly stated in the context.
8. Look for the answer across ALL provided sources — it may appear in any source, including the last one."""


def _build_user_prompt(question: str, context: str) -> str:
    """Build the user prompt with the question and retrieved context."""

    return f"""Based on the following document context, answer the question.

--- DOCUMENT CONTEXT ---
{context}
--- END CONTEXT ---

Question: {question}

Answer:"""


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string for the LLM prompt."""

    context_parts = []

    for i, chunk in enumerate(chunks):
        source = chunk["original_filename"]
        page = chunk["page_number"]
        content = chunk["content"]
        similarity = round(chunk["similarity"], 4)

        context_parts.append(
            f"[Source {i+1}: {source}, Page {page}, Relevance: {similarity}]\n{content}"
        )

    return "\n\n".join(context_parts)