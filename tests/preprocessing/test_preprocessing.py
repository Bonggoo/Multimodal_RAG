import os
import pytest
import fitz
from pathlib import Path

# 테스트 대상 함수 임포트
from src.preprocessing.loader import load_pdf, split_pdf_to_pages
from src.preprocessing.thumbnail import create_thumbnails

# 테스트 설정
TEST_PDF_PATH = "tests/assets/test_document.pdf"
NON_EXISTENT_PDF_PATH = "tests/assets/non_existent.pdf"
DOC_NAME = "test_document"
EXPECTED_PAGE_COUNT = 3

@pytest.fixture(scope="module")
def pdf_document():
    """테스트용 PDF 문서를 로드하는 pytest fixture"""
    doc = load_pdf(TEST_PDF_PATH)
    assert doc is not None, f"테스트 PDF 파일을 로드할 수 없습니다: {TEST_PDF_PATH}"
    yield doc
    doc.close()

def test_load_pdf_success(pdf_document):
    """성공적인 PDF 로드 테스트"""
    assert isinstance(pdf_document, fitz.Document)
    assert len(pdf_document) == EXPECTED_PAGE_COUNT

def test_load_pdf_not_found():
    """존재하지 않는 파일 로드 시 예외 처리 테스트"""
    assert load_pdf(NON_EXISTENT_PDF_PATH) is None

def test_split_pdf_to_pages(pdf_document):
    """PDF 페이지 분할 기능 테스트"""
    pages_as_bytes = split_pdf_to_pages(pdf_document)
    
    assert isinstance(pages_as_bytes, list)
    assert len(pages_as_bytes) == EXPECTED_PAGE_COUNT
    
    # 각 항목이 유효한 PDF 바이트인지 간단히 확인
    for page_bytes in pages_as_bytes:
        assert isinstance(page_bytes, bytes)
        # 바이트 스트림을 사용해 fitz 문서를 열어봄으로써 유효성 검사
        with fitz.open(stream=page_bytes, filetype="pdf") as doc:
            assert len(doc) == 1

def test_create_thumbnails(pdf_document, tmp_path):
    """썸네일 생성 기능 테스트"""
    # tmp_path는 pytest가 제공하는 임시 디렉토리 fixture
    output_dir = tmp_path / "thumbnails"
    
    thumbnail_paths = create_thumbnails(pdf_document, DOC_NAME, str(output_dir))
    
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
