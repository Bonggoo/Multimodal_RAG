
import json
import os
from datetime import datetime
from uuid import UUID
from typing import Any, Dict

DATA_DIR = "data"
QA_LOG_FILE = os.path.join(DATA_DIR, "qa_history.jsonl")
FEEDBACK_LOG_FILE = os.path.join(DATA_DIR, "feedback_logs.jsonl")

def ensure_log_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def log_qa_history(trace_id: str, query: str, answer: str, filters: Dict[str, Any] = None):
    ensure_log_dir()
    log_entry = {
        "trace_id": str(trace_id),
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "answer": answer,
        "filters": filters
    }
    with open(QA_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def log_feedback(trace_id: str, score: int, comment: str = None):
    ensure_log_dir()
    log_entry = {
        "trace_id": str(trace_id),
        "timestamp": datetime.utcnow().isoformat(),
        "score": score,
        "comment": comment
    }
    with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
