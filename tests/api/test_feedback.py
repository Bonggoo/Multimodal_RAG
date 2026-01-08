
import os
import json
import uuid
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

class TestFeedbackLoop:
    client = TestClient(app)
    headers = {"X-API-Key": os.environ.get('BACKEND_API_KEY', 'test_secret_key')}
    
    def test_qa_logging_and_feedback(self):
        # 1. QA 요청
        qa_response = self.client.post(
            "/qa", 
            headers=self.headers, 
            json={"query": "테스트 질문입니다."}
        )
        assert qa_response.status_code == 200
        data = qa_response.json()
        assert "trace_id" in data
        trace_id = data["trace_id"]
        print(f"Received Trace ID: {trace_id}")
        
        # 2. QA 로그 파일 확인
        qa_log_path = "data/qa_history.jsonl"
        assert os.path.exists(qa_log_path)
        
        # 마지막 줄 읽어서 trace_id 확인
        found_trace = False
        with open(qa_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                log = json.loads(line)
                if log["trace_id"] == trace_id:
                    found_trace = True
                    assert log["query"] == "테스트 질문입니다."
                    break
        assert found_trace, "QA log not found for the trace_id"

        # 3. 피드백 전송
        feedback_data = {
            "trace_id": trace_id,
            "score": 1,
            "comment": "Good answer!"
        }
        feedback_response = self.client.post(
            "/feedback",
            headers=self.headers,
            json=feedback_data
        )
        assert feedback_response.status_code == 200
        
        # 4. 피드백 로그 파일 확인
        feedback_log_path = "data/feedback_logs.jsonl"
        assert os.path.exists(feedback_log_path)
        
        found_feedback = False
        with open(feedback_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                log = json.loads(line)
                if log["trace_id"] == trace_id:
                    found_feedback = True
                    assert log["score"] == 1
                    assert log["comment"] == "Good answer!"
                    break
        assert found_feedback, "Feedback log not found for the trace_id"
