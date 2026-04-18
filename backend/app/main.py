from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_db, disconnect_db
from app.repositories.document_repository import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await create_tables()
    yield
    await disconnect_db()


app = FastAPI(
    title="ThinkDocs",
    description="AI-Powered Document Q&A Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ThinkDocs API"}