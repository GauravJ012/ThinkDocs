from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    content: str
    page_number: int | None
    document_name: str
    similarity: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]