from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    page_count: int
    chunk_count: int
    status: str
    created_at: datetime