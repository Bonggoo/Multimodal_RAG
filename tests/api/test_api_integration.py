import os
import time
import json
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

# Set environment variables before importing the app
# This ensures that the app's settings are loaded with these test values.
os.environ['BACKEND_API_KEY'] = 'test_secret_key'
# We might not need a real Google key if we mock the LLM calls,
# but for a true integration test, it's required. We can use a placeholder.
if 'GOOGLE_API_KEY' not in os.environ:
    print("Warning: GOOGLE_API_KEY not set. Real LLM calls will fail.")
    os.environ['GOOGLE_API_KEY'] = 'fake_google_key'

from src.api.main import app

@pytest.mark.integration
class TestApiIntegration:
    """
    Groups integration tests for the full API workflow.
    Tests are ordered (01, 02, 03) to follow a logical sequence:
    ingest -> qa_http -> qa_websocket.
    """

    client = TestClient(app)
    headers = {"X-API-Key": os.environ['BACKEND_API_KEY']}
    test_pdf_path = "tests/assets/test_document.pdf"
    test_query = "HPPF-12 모델의 조임 토크는 얼마인가?"
    expected_answer_part = "0.63"

    # This will be set by the first test and used by subsequent tests.
    job_id = None

    def test_01_ingest_document(self):
        """
        Tests the document ingestion process from upload to completion.
        1. Uploads a PDF file to /ingest.
        2. Polls the /ingest/status/{job_id} endpoint until the job is 'completed'.
        """
        assert os.path.exists(self.test_pdf_path), "Test PDF file not found."
        
        with open(self.test_pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(self.test_pdf_path), f, 'application/pdf')}
            response = self.client.post("/ingest", headers=self.headers, files=files)
        
        assert response.status_code == 202, "Expected 202 Accepted status for ingestion."
        data = response.json()
        assert "job_id" in data
        
        # Store job_id for the next tests in the class
        TestApiIntegration.job_id = data["job_id"]
        print(f"\nIngestion started. Job ID: {self.job_id}")

        # Poll for status
        timeout = 180  # 3-minute timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.client.get(f"/ingest/status/{self.job_id}", headers=self.headers)
            assert response.status_code == 200
            status_data = response.json()
            
            if status_data["status"] == "completed":
                print("Ingestion completed successfully.")
                return  # Test successful
            
            if status_data["status"] == "failed":
                pytest.fail(f"Ingestion failed: {status_data.get('message')}")
            
            print(f"Polling status... current: {status_data['status']}")
            time.sleep(5)
        
        pytest.fail("Ingestion process timed out after 3 minutes.")

    def test_02_qa_http(self):
        """
        Tests the standard HTTP /qa endpoint after document ingestion.
        """
        if not TestApiIntegration.job_id:
            pytest.skip("Skipping HTTP QA test because ingestion did not complete.")
        
        response = self.client.post(
            "/qa",
            headers=self.headers,
            json={"query": self.test_query}
        )
        
        if response.status_code != 200:
             print(f"QA Failed. Status: {response.status_code}, Body: {response.text}")
        assert response.status_code == 200
        data = response.json()
        print(f"HTTP QA Response: {data}")
        
        assert "answer" in data
        assert self.expected_answer_part in data["answer"], \
            f"Expected '{self.expected_answer_part}' in answer, but got '{data['answer']}'"

    def test_03_qa_websocket(self):
        """
        Tests the WebSocket /ws/qa endpoint for streaming Q&A.
        """
        if not TestApiIntegration.job_id:
            pytest.skip("Skipping WebSocket QA test because ingestion did not complete.")

        final_answer = ""
        try:
            with self.client.websocket_connect("/ws/qa", headers=self.headers) as websocket:
                websocket.send_json({"query": self.test_query})
                
                while True:
                    data = websocket.receive_json()
                    
                    if data["type"] == "token":
                        final_answer += data["payload"]
                    elif data["type"] == "metadata":
                        # The final answer is also in the metadata payload
                        assert self.expected_answer_part in data["payload"]["final_answer"]
                    elif data["type"] == "end":
                        break  # End of stream
                    elif data["type"] == "error":
                        pytest.fail(f"WebSocket QA returned an error: {data['payload']}")
        
        except WebSocketDisconnect:
            pytest.fail("WebSocket disconnected unexpectedly.")

        print(f"WebSocket final aggregated answer: {final_answer}")
        assert self.expected_answer_part in final_answer, \
            f"Expected '{self.expected_answer_part}' in WebSocket answer, but got '{final_answer}'"
