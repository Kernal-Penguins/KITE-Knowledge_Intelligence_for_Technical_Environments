"""
scripts/run_evaluation.py
─────────────────────────
Runs the evaluation suite and logs results to Postgres.
"""
import asyncio
import json
import sys
import time
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.infrastructure.postgres_client import init_db
from app.infrastructure.qdrant_client import qdrant_client
from app.pipeline.query_pipeline import run_query
from app.repositories.postgres_repo import postgres_repo
from evaluation.benchmark import BENCHMARK_QUESTIONS
from evaluation.metrics import evaluate_response


async def run_evaluations():
    log.info("evaluation.suite.started")

    # Connect infrastructure clients
    await init_db()
    await neo4j_client.connect()
    await qdrant_client.connect()

    total_score = 0.0

    for i, item in enumerate(BENCHMARK_QUESTIONS, 1):
        query = item["q"]
        expected = item["expected_entities"]

        start_t = time.time()
        try:
            res = await run_query(query)
            query_time = time.time() - start_t

            metrics = evaluate_response(query_time, expected, res["answer"], res["citations"])
            total_score += metrics["overall_score"]

            print(f"[{i}/{len(BENCHMARK_QUESTIONS)}] Q: '{query}' -> Score: {metrics['overall_score']:.2f}")

            await postgres_repo.log_evaluation(
                query=query,
                latency=metrics["latency_sec"],
                score=metrics["overall_score"],
                details=json.dumps(metrics),
            )
        except Exception as e:
            log.error("evaluation.failed", query=query, error=str(e))
            print(f"[{i}/{len(BENCHMARK_QUESTIONS)}] ERROR: {query} -> {e}")

    avg_score = total_score / len(BENCHMARK_QUESTIONS) if BENCHMARK_QUESTIONS else 0.0
    print("\n" + "=" * 50)
    print(f"Evaluation Suite Completed! Avg Score: {avg_score:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_evaluations())
