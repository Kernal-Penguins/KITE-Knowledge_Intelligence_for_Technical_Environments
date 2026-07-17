"""
api/routes/query.py
───────────────────
Endpoints for GraphRAG querying.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pipeline.query_pipeline import run_query
from app.repositories.postgres_repo import postgres_repo

router = APIRouter(prefix="/query", tags=["Query"])

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: dict

@router.post("", response_model=QueryResponse)
async def submit_query(request: QueryRequest):
    try:
        result = await run_query(request.query)
        
        # Log to chat_messages via postgres
        await postgres_repo.log_chat_message(
            query=request.query,
            answer=result["answer"],
            confidence=result["confidence"]
        )
        
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
