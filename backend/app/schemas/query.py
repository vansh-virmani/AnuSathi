from typing import List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    q: str
    document_id: Optional[str] = None


class Source(BaseModel):  #returns sources page metadata 
    document_id: str
    page: int


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source] = Field(default_factory=list)