import os
import pytest
import fitz # 썸네일 생성을 위해 필요
from pathlib import Path

from langchain_core.documents import Document

# 테스트 대상 함수 임포트
from src.preprocessing.loader import load_pdf_as_documents
from src.preprocessing.thumbnail import create_thumbnails

# 테스트 설정
TEST_PDF_PATH = "tests/assets/test_document.pdf"
NON_EXISTENT_PDF_PATH = "tests/assets/non_existent.pdf"
DOC_NAME = "test_document"
EXPECTED_PAGE_COUNT = 3

@pytest.fixture(scope="module")
def fitz_pdf_document():
    """썸네일 생성을 위해 fitz.Document 객체를 로드하는 pytest fixture"""
    doc = fitz.open(TEST_PDF_PATH)
    assert doc is not None, f"테스트 PDF 파일을 로드할 수 없습니다: {TEST_PDF_PATH}"
    yield doc
    doc.close()

def test_load_pdf_as_documents_success():
    """성공적인 LangChain Document 로드 테스트"""
    documents = load_pdf_as_documents(TEST_PDF_PATH)
    assert isinstance(documents, list)
    assert len(documents) == EXPECTED_PAGE_COUNT
    for doc in documents:
        assert isinstance(doc, Document)
        assert "page" in doc.metadata # PyMuPDFLoader가 'page' 메타데이터를 추가

def test_load_pdf_as_documents_not_found():
    """존재하지 않는 파일 로드 시 빈 리스트 반환 테스트"""
    documents = load_pdf_as_documents(NON_EXISTENT_PDF_PATH)
    assert isinstance(documents, list)
    assert len(documents) == 0

def test_create_thumbnails(fitz_pdf_document, tmp_path):
    """썸네일 생성 기능 테스트"""
    # tmp_path는 pytest가 제공하는 임시 디렉토리 fixture
    output_dir = tmp_path / "thumbnails"
    
    thumbnail_paths = create_thumbnails(fitz_pdf_document, DOC_NAME, str(output_dir))
    
    assert isinstance(thumbnail_paths, list)
    assert len(thumbnail_paths) == EXPECTED_PAGE_COUNT
    
    # 생성된 파일 수와 경로 확인
    created_files = os.listdir(output_dir)
    assert len(created_files) == EXPECTED_PAGE_COUNT
    
    for i, path_str in enumerate(thumbnail_paths):
        page_num = i + 1
        expected_filename = f"{DOC_NAME}_p{page_num:03d}.png"
        
        # 반환된 경로가 올바른지 확인
        p = Path(path_str)
        assert p.name == expected_filename
        assert p.parent.name == output_dir.name
        
        # 해당 파일이 실제로 존재하는지 확인
        assert p.exists()
