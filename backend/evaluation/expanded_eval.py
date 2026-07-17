"""
evaluation/expanded_eval.py
───────────────────────────
Script to run expanded evaluation metrics on benchmark questions.
"""
import asyncio
import json
from pathlib import Path

from app.infrastructure.logger import log
from app.providers.gemini_provider import GeminiProvider
from evaluation.metrics import (
    evaluate_counterfactual,
    evaluate_provenance,
    evaluate_structural_validity,
    evaluate_temporal_alignment,
)


async def run_expanded_evaluation():
    log.info("expanded_eval.started")
    provider = GeminiProvider()
    
    questions_path = Path(__file__).parent / "benchmark_questions.json"
    if not questions_path.exists():
        log.error("expanded_eval.failed", error="benchmark_questions.json not found")
        return
        
    with open(questions_path, "r") as f:
        questions = json.load(f)
        
    results = []
    
    for q in questions:
        query = q.get("question", "")
        log.info("expanded_eval.processing_query", query=query)
        
        # In a real run, we would call the actual /query endpoint or pipeline to get 
        # the generated answer, context chunks, and graph context.
        # For this script, we simulate retrieving that data.
        simulated_answer = "The most recent failure recorded for equipment P-104 was a seal leak on 2026-05-12 [Doc 1] [Graph Path 1]."
        simulated_context = ["P-104 maintenance log notes a seal leak on 2026-05-12."]
        simulated_graph = ["Equipment('P-104') -[HAS_FAILURE]-> Failure('F-999')"]
        
        score_prov = await evaluate_provenance(query, simulated_answer, simulated_context, provider)
        score_struc = await evaluate_structural_validity(simulated_answer, simulated_graph, provider)
        score_temp = await evaluate_temporal_alignment(simulated_answer, provider)
        score_count = await evaluate_counterfactual(query, simulated_answer, provider)
        
        results.append({
            "query": query,
            "provenance_score": score_prov,
            "structural_validity_score": score_struc,
            "temporal_alignment_score": score_temp,
            "counterfactual_score": score_count,
            "overall_expanded_score": (score_prov + score_struc + score_temp + score_count) / 4.0
        })
        
    log.info("expanded_eval.completed", total_questions=len(questions), results=results)
    
if __name__ == "__main__":
    asyncio.run(run_expanded_evaluation())
