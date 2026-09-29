"""Benchmark runner for the assignment test questions."""

import json
import requests

BASE_URL = "http://127.0.0.1:8000"

QUERIES = [
    "What is Agentic AI according to the eBook?",
    "How do AI agents differ from traditional automation systems?",
    "What are the core components of an Agentic Architecture?",
    "What role does memory play in Agentic AI workflows?",
    "Who won the 2022 FIFA World Cup?",
    "What are the key characteristics of Agentic AI?",
]

for question in QUERIES:
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": question},
        timeout=60,
    )
    print("\nQUESTION:", question)
    print("STATUS:", response.status_code)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
