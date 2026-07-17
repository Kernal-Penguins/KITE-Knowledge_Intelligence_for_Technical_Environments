"""
evaluation/metrics.py
─────────────────────
Computes evaluation metrics like citation coverage and latency.
"""
from app.infrastructure.logger import log

def evaluate_response(query_time: float, expected_entities: list[str], answer: str, citations: dict) -> dict:
    log.info("evaluation.metrics.computing")
    
    latency_score = 1.0 if query_time < 2.0 else (2.0 / query_time)
    
    answer_lower = answer.lower()
    recall = sum(1 for e in expected_entities if e.lower() in answer_lower) / len(expected_entities) if expected_entities else 1.0
    
    has_doc_cite = "[Doc" in answer
    has_graph_cite = "[Graph" in answer
    citation_score = 1.0 if (has_doc_cite and has_graph_cite) else (0.5 if has_doc_cite or has_graph_cite else 0.0)
    
    return {
        "latency_sec": round(query_time, 2),
        "latency_score": round(latency_score, 2),
        "entity_recall": round(recall, 2),
        "citation_score": round(citation_score, 2),
        "overall_score": round((latency_score + recall + citation_score) / 3, 2)
    }
