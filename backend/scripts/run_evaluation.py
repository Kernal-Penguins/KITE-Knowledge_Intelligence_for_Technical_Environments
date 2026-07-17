"""
scripts/run_evaluation.py
─────────────────────────
Runs the evaluation suite and logs results to Postgres.
"""
import asyncio
import time
import sys
import json
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from evaluation.benchmark import BENCHMARK_QUESTIONS
from evaluation.metrics import evaluate_response
from app.pipeline.query_pipeline import run_query
from app.repositories.postgres_repo import postgres_repo
from app.infrastructure.logger import log

async def run_evaluations():
    log.info("evaluation.suite.started")
    total_score = 0
    
    for i, item in enumerate(BENCHMARK_QUESTIONS):
        query = item["q"]
        expected = item["expected_entities"]
        
        start_t = time.time()
        try:
            res = await run_query(query)
            query_time = time.time() - start_t
            
            metrics = evaluate_response(query_time, expected, res["answer"], res["citations"])
            total_score += metrics["overall_score"]
            
            log.info("evaluation.result", query=query, metrics=metrics)
            
            await postgres_repo.log_evaluation(
                query=query,
                latency=metrics["latency_sec"],
                score=metrics["overall_score"],
                details=json.dumps(metrics)
            )
        except Exception as e:
            log.error("evaluation.failed", query=query, error=str(e))
            
    avg_score = total_score / len(BENCHMARK_QUESTIONS)
    log.info("evaluation.suite.completed", avg_score=round(avg_score, 2))

if __name__ == "__main__":
    asyncio.run(run_evaluations())
