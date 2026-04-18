from app.database import get_pool


async def insert_chunk(document_id: int, content: str, chunk_index: int, page_number: int = None):
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO chunks (document_id, content, chunk_index, page_number)
        VALUES ($1, $2, $3, $4)
        RETURNING id, document_id, content, chunk_index, page_number, created_at
        """,
        document_id, content, chunk_index, page_number
    )
    return dict(row)


async def insert_chunks_batch(chunks: list[dict]):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO chunks (document_id, content, chunk_index, page_number)
            VALUES ($1, $2, $3, $4)
            """,
            [(c["document_id"], c["content"], c["chunk_index"], c.get("page_number")) for c in chunks]
        )


async def update_chunk_embedding(chunk_id: int, embedding: list[float]):
    pool = get_pool()
    await pool.execute(
        "UPDATE chunks SET embedding = $2 WHERE id = $1",
        chunk_id, str(embedding)
    )


async def update_embeddings_batch(chunk_ids: list[int], embeddings: list[list[float]]):
    pool = get_pool()
    async with pool.acquire() as conn:
        for chunk_id, embedding in zip(chunk_ids, embeddings):
            await conn.execute(
                "UPDATE chunks SET embedding = $2 WHERE id = $1",
                chunk_id, str(embedding)
            )


async def find_similar_chunks(query_embedding: list[float], top_k: int = 5):
    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT c.id, c.content, c.chunk_index, c.page_number,
               c.document_id, d.original_filename,
               1 - (c.embedding <=> $1::vector) AS similarity
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.embedding IS NOT NULL
        ORDER BY c.embedding <=> $1::vector
        LIMIT $2
        """,
        str(query_embedding), top_k
    )
    return [dict(row) for row in rows]


async def find_chunks_by_document(document_id: int):
    pool = get_pool()
    rows = await pool.fetch(
        "SELECT * FROM chunks WHERE document_id = $1 ORDER BY chunk_index",
        document_id
    )
    return [dict(row) for row in rows]