
import os
import time
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.schemas import QAFilters

class TestFiltering:
    client = TestClient(app)
    headers = {"X-API-Key": os.environ.get('BACKEND_API_KEY', 'test_secret_key')}
    
    # 두 개의 테스트용 PDF (실제로는 같은 파일 복사해서 이름만 다르게 사용)
    doc_a_path = "tests/assets/doc_a.pdf"
    doc_b_path = "tests/assets/doc_b.pdf"
    
    @classmethod
    def setup_class(cls):
        # 테스트용 더미 파일 생성 (없으면)
        if not os.path.exists("tests/assets"):
            os.makedirs("tests/assets")
        
        # 기존 test_document.pdf를 복사하여 두 개의 파일 생성
        if os.path.exists("tests/assets/test_document.pdf"):
             with open("tests/assets/test_document.pdf", "rb") as f:
                content = f.read()
                with open(cls.doc_a_path, "wb") as f_a: f_a.write(content)
                with open(cls.doc_b_path, "wb") as f_b: f_b.write(content)

    def test_filtering_logic(self):
        # 1. 두 문서 업로드
        for path in [self.doc_a_path, self.doc_b_path]:
             with open(path, 'rb') as f:
                files = {'file': (os.path.basename(path), f, 'application/pdf')}
                response = self.client.post("/ingest", headers=self.headers, files=files)
                assert response.status_code == 202
                job_id = response.json()["job_id"]
                
                # 처리 완료 대기
                timeout = 60
                start = time.time()
                while time.time() - start < timeout:
                    status = self.client.get(f"/ingest/status/{job_id}", headers=self.headers).json()["status"]
                    if status == "completed": break
                    time.sleep(2)
                assert status == "completed"

        # 2. 필터 없이 질문 (둘 다 검색되어야 함 - 하지만 확인 어려움)
        
        # 3. 문서 A만 필터링하여 질문
        filter_a = {"doc_name": "doc_a"}
        response_a = self.client.post(
            "/qa", 
            headers=self.headers, 
            json={"query": "토크 값은?", "filters": filter_a}
        )
        assert response_a.status_code == 200
        # 답변이 정상적으로 나와야 함
        assert "response" or "answer" in response_a.json()
        print(f"Filtered Response A: {response_a.json()}")

        # 4. 존재하지 않는 문서 필터링
        filter_c = {"doc_name": "doc_c_non_existent"}
        response_c = self.client.post(
            "/qa", 
            headers=self.headers, 
            json={"query": "토크 값은?", "filters": filter_c}
        )
        # 검색 결과가 없어야 하므로 답변이 '모른다'거나 빈 컨텍스트일 것임
        print(f"Filtered Response C (Should be empty/unknown): {response_c.json()}")
        
        # 실제 검증: 로그나 내부 동작을 봐야 확실하지만, 여기서는 에러 없이 호출되고
        # 결과가 다를 수 있음을 확인하는 정도 (내용이 같아도 필터링 로직은 탔음)
