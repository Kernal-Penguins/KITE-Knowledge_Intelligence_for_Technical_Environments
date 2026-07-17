"""
evaluation/benchmark.py
────────────────────────
Runs the benchmark question set against the live KITE /query endpoint
and records results to PostgreSQL.

Usage:
    python scripts/run_evaluation.py
"""
import asyncio
import json
import time
import uuid
from pathlib import Path

import httpx

from app.db.models import EvaluationResult, EvaluationRun
from app.infrastructure.logger import log
from app.infrastructure.postgres_client import get_db_session, init_db

BENCHMARK_QUESTIONS_PATH = Path(__file__).parent / "benchmark_questions.json"
API_BASE = "http://localhost:8000"


async def run_benchmark() -> None:
    """Run all benchmark questions and persist results."""
    await init_db()

    questions = json.loads(BENCHMARK_QUESTIONS_PATH.read_text())
    run_id = str(uuid.uuid4())

    log.info("benchmark.started", run_id=run_id, question_count=len(questions))

    results: list[dict] = []

    async with httpx.AsyncClient(base_url=API_BASE, timeout=120) as client:
        for q in questions:
            t0 = time.monotonic()
            try:
                resp = await client.post("/api/v1/query", json={"query": q["question"]})
                resp.raise_for_status()
                data = resp.json()
                elapsed = round((time.monotonic() - t0) * 1000, 1)

                results.append({
                    "question_id": q["id"],
                    "question": q["question"],
                    "answer": data.get("answer", ""),
                    "confidence": data.get("confidence", 0.0),
                    "has_citations": len(data.get("citations", [])) > 0,
                    "has_graph_path": len(data.get("graph_paths", [])) > 0,
                    "response_ms": elapsed,
                })
                log.info(
                    "benchmark.question_done",
                    question_id=q["id"],
                    response_ms=elapsed,
                    confidence=data.get("confidence"),
                )
            except Exception as exc:
                results.append({
                    "question_id": q["id"],
                    "question": q["question"],
                    "answer": None,
                    "error": str(exc),
                    "response_ms": round((time.monotonic() - t0) * 1000, 1),
                })
                log.error("benchmark.question_failed", question_id=q["id"], error=str(exc))

    # Persist to PostgreSQL
    async with get_db_session() as db:
        run = EvaluationRun(
            id=run_id,
            question_count=len(questions),
            llm_provider="gemini",
            llm_model="gemini-2.5-flash / gemini-2.5-pro",
        )
        db.add(run)
        await db.flush()

        for r in results:
            db.add(EvaluationResult(
                run_id=run_id,
                question_id=r["question_id"],
                question=r["question"],
                answer=r.get("answer"),
                is_correct=None,   # set manually after human review
                metrics_json=r,
                response_ms=r.get("response_ms"),
            ))

    log.info("benchmark.complete", run_id=run_id, results=len(results))


if __name__ == "__main__":
    asyncio.run(run_benchmark())
