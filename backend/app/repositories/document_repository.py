from app.database import get_pool


async def create_tables():
    pool = get_pool()
    async with pool.acquire() as conn:
        # Documents table — stores PDF metadata
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_size INTEGER NOT NULL,
                page_count INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'uploaded',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Chunks table — stores text chunks with vector embeddings
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                page_number INTEGER,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index for fast vector similarity search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding
            ON chunks USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)


async def insert_document(filename: str, original_filename: str, file_size: int):
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO documents (filename, original_filename, file_size)
        VALUES ($1, $2, $3)
        RETURNING id, filename, original_filename, file_size, page_count, chunk_count, status, created_at
        """,
        filename, original_filename, file_size
    )
    return dict(row)


async def find_all_documents():
    pool = get_pool()
    rows = await pool.fetch(
        "SELECT * FROM documents ORDER BY created_at DESC"
    )
    return [dict(row) for row in rows]


async def find_document_by_id(doc_id: int):
    pool = get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM documents WHERE id = $1",
        doc_id
    )
    return dict(row) if row else None


async def update_document_status(doc_id: int, status: str, page_count: int = None, chunk_count: int = None):
    pool = get_pool()
    if page_count is not None and chunk_count is not None:
        await pool.execute(
            """
            UPDATE documents
            SET status = $2, page_count = $3, chunk_count = $4
            WHERE id = $1
            """,
            doc_id, status, page_count, chunk_count
        )
    else:
        await pool.execute(
            "UPDATE documents SET status = $2 WHERE id = $1",
            doc_id, status
        )


async def delete_document(doc_id: int) -> bool:
    pool = get_pool()
    result = await pool.execute(
        "DELETE FROM documents WHERE id = $1",
        doc_id
    )
    return result != "DELETE 0"