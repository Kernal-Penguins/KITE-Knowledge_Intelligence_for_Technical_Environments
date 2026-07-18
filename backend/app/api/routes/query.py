"""
api/routes/query.py
───────────────────
Endpoints for GraphRAG querying (Copilot).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.infrastructure.logger import log
from app.pipeline.query_pipeline import run_query
from app.repositories.postgres_repo import postgres_repo

router = APIRouter(prefix="/query", tags=["Query"])


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000, description="User's natural-language question.")


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: dict


@router.post("", response_model=QueryResponse)
async def submit_query(request: QueryRequest) -> QueryResponse:
    """Submit a natural-language query and return a GraphRAG-grounded answer."""
    stripped = request.query.strip()
    if not stripped:
        raise HTTPException(status_code=422, detail="Query must not be blank.")

    try:
        result = await run_query(stripped)
    except Exception as exc:
        log.error("query_route.failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Query pipeline failed. Please try again.")

    # Log the exchange to Postgres (best-effort — don't fail the request if logging fails)
    try:
        await postgres_repo.log_chat_message(
            query=stripped,
            answer=result["answer"],
            confidence=result["confidence"],
        )
    except Exception as log_exc:
        log.warning("query_route.log_failed", error=str(log_exc))

    return QueryResponse(**result)
