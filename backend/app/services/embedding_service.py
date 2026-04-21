from openai import OpenAI
from app.config import settings
from app.repositories import chunk_repository

client = OpenAI(api_key=settings.OPENAI_API_KEY)

EMBEDDING_MODEL = "text-embedding-ada-002"
BATCH_SIZE = 20  # OpenAI allows up to 2048, but smaller batches are safer


async def generate_embeddings_for_document(document_id: int):
    """Generate and store embeddings for all chunks of a document."""

    # Get all chunks for this document
    chunks = await chunk_repository.find_chunks_by_document(document_id)

    if not chunks:
        return 0

    # Process in batches
    total_embedded = 0

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]

        # Extract text content from each chunk
        texts = [chunk["content"] for chunk in batch]
        chunk_ids = [chunk["id"] for chunk in batch]

        # Call OpenAI embedding API
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )

        # Extract embedding vectors from response
        embeddings = [item.embedding for item in response.data]

        # Store embeddings in database
        await chunk_repository.update_embeddings_batch(chunk_ids, embeddings)

        total_embedded += len(batch)

    return total_embedded


async def get_query_embedding(query: str) -> list[float]:
    """Generate an embedding for a user's question."""

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
    )

    return response.data[0].embedding