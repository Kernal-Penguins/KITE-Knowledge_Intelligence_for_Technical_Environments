"""
evaluation/benchmark.py
───────────────────────
Benchmark questions for evaluating GraphRAG performance.
"""

BENCHMARK_QUESTIONS = [
    {"q": "What procedure is used to inspect the V-205 vessel?", "expected_entities": ["V-205", "Procedure"]},
    {"q": "Who performed the LOTO on P-101 and when?", "expected_entities": ["P-101", "LOTO", "Person"]},
    {"q": "What was the root cause of the TT-304 sensor failure?", "expected_entities": ["TT-304", "Failure"]},
    {"q": "Which regulations govern the high-pressure steam lines?", "expected_entities": ["Regulation", "high-pressure"]},
    {"q": "List all unresolved incidents from the past month.", "expected_entities": ["Incident"]}
]
