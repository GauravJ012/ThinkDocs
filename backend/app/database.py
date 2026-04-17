import asyncpg
from app.config import settings

pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        min_size=2,
        max_size=10,
    )

    # Enable pgvector extension
    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")


async def disconnect_db():
    global pool
    if pool:
        await pool.close()


def get_pool():
    return pool