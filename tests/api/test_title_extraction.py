
import os
import time
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from tests.create_dummy_pdf import create_simple_pdf

class TestTitleExtraction:
    client = TestClient(app)
    headers = {"X-API-Key": os.environ.get('BACKEND_API_KEY', 'test_secret_key')}
    pdf_path = "tests/assets/title_test_doc.pdf"

    @classmethod
    def setup_class(cls):
        # 테스트용 더미 PDF 생성 (타이틀 포함)
        if not os.path.exists("tests/assets"):
            os.makedirs("tests/assets")
        create_simple_pdf(cls.pdf_path)

    @classmethod
    def teardown_class(cls):
        # 파일 삭제는 선택 사항 (디버깅 위해 유지하거나 삭제)
        if os.path.exists(cls.pdf_path):
            os.remove(cls.pdf_path)

    def test_title_extraction(self):
        # 1. 문서 업로드
        with open(self.pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(self.pdf_path), f, 'application/pdf')}
            response = self.client.post("/ingest", headers=self.headers, files=files)
            assert response.status_code == 202
            job_id = response.json()["job_id"]
        
        # 2. 처리 완료 대기
        timeout = 60
        start = time.time()
        while time.time() - start < timeout:
            status_resp = self.client.get(f"/ingest/status/{job_id}", headers=self.headers)
            status = status_resp.json()["status"]
            if status == "completed": break
            if status == "failed":
                pytest.fail(f"Ingestion failed: {status_resp.json().get('message')}")
            time.sleep(2)
        assert status == "completed"

        # 3. 문서 목록 조회 및 타이틀 확인
        list_resp = self.client.get("/documents", headers=self.headers)
        assert list_resp.status_code == 200
        documents = list_resp.json()["documents"]
        
        print(f"Documents List: {documents}")

        # 업로드한 파일 찾기
        target_filename = os.path.basename(self.pdf_path).replace(".pdf", "") # services.py returns doc_name which is stem
        
        found_doc = next((doc for doc in documents if doc["filename"] == target_filename), None)
        assert found_doc is not None, "Uploaded document not found in list"
        
        # 타이틀 검증 (Gemini가 추출한 값)
        # 예상: "RAG System User Manual" (create_dummy_pdf.py에서 넣은 값)
        # LLM이므로 정확히 일치하지 않을 수 있으니 포함 여부 확인
        extracted_title = found_doc.get("title")
        print(f"Extracted Title: {extracted_title}")
        
        assert extracted_title is not None
        assert "RAG System" in extracted_title or "User Manual" in extracted_title
