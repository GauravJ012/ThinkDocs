from app.services.embedding_service import get_query_embedding
from app.repositories import chunk_repository


async def retrieve_relevant_chunks(question: str, top_k: int = 5) -> list[dict]:
    """Find the most relevant chunks for a user's question.

    1. Convert the question to an embedding vector
    2. Search pgvector for the most similar chunk embeddings
    3. Return the top-K chunks with similarity scores
    """

    # Step 1: Embed the question using the same model as document chunks
    query_embedding = await get_query_embedding(question)

    # Step 2: Find similar chunks via cosine similarity in pgvector
    similar_chunks = await chunk_repository.find_similar_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
    )

    return similar_chunks