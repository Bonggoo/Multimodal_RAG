import pytest
from unittest.mock import patch, MagicMock, call
import os

# 테스트 대상 모듈 및 클래스 임포트
from src.parsing.schema import PageContent, Image
from src.storage.vector_db import (
    get_vector_store,
    add_page_content_to_vector_db,
    COLLECTION_NAME,
    CHROMA_DB_PATH,
)

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# --- get_vector_store 테스트 ---

@patch('src.storage.vector_db.load_dotenv')
@patch('src.storage.vector_db.GoogleGenerativeAIEmbeddings')
@patch('src.storage.vector_db.Chroma')
def test_get_vector_store_success(mock_chroma, mock_embeddings_class, mock_load_dotenv):
    """Chroma 벡터 스토어 생성 성공 테스트"""
    # Simulate load_dotenv setting the environment variable
    def mock_load_dotenv_effect():
        os.environ['GOOGLE_API_KEY'] = 'fake_api_key'
    mock_load_dotenv.side_effect = mock_load_dotenv_effect

    vector_store = get_vector_store()
    
    mock_load_dotenv.assert_called_once()
    mock_embeddings_class.assert_called_once_with(model="models/text-embedding-004", google_api_key='fake_api_key')
    
    mock_chroma.assert_called_once_with(
        collection_name=COLLECTION_NAME,
        embedding_function=mock_embeddings_class.return_value,
        persist_directory=CHROMA_DB_PATH
    )
    
    assert isinstance(vector_store, MagicMock)
    assert vector_store == mock_chroma.return_value

@patch('src.storage.vector_db.load_dotenv')
@patch.dict('os.environ', {}, clear=True) # GOOGLE_API_KEY가 없는 환경 시뮬레이션
def test_get_vector_store_no_api_key(mock_load_dotenv):
    """API 키가 없을 때 ValueError 발생 테스트"""
    with pytest.raises(ValueError, match="GOOGLE_API_KEY가 환경 변수에 설정되지 않았습니다."):
        get_vector_store()
    mock_load_dotenv.assert_called_once()


# --- add_page_content_to_vector_db 테스트 ---

@pytest.fixture
def sample_page_content():
    """테스트용 PageContent 객체 Fixture"""
    return PageContent(
        text="This is the main text.",
        tables=["| col1 | col2 |\n|---|---|"],
        images=[Image(description="A description of an image.", caption="A caption.")],
        chapter_path="Chapter 1"
    )

def test_add_page_content_to_vector_db(sample_page_content):
    """벡터 스토어에 페이지 콘텐츠 적재 기능 테스트"""
    mock_vector_db = MagicMock(spec=Chroma) # Chroma 인스턴스처럼 보이도록 spec 지정
    page_num = 1
    img_path = "/path/to/image.png"

    add_page_content_to_vector_db(sample_page_content, page_num, img_path, mock_vector_db)

    # add_documents가 호출되었는지 확인
    mock_vector_db.add_documents.assert_called_once()
    
    # 호출 인자 추출 (첫 번째 인자는 문서 리스트)
    args, kwargs = mock_vector_db.add_documents.call_args
    added_documents = args[0]
    
    assert len(added_documents) == 3
    
    # 각 Document 객체의 내용과 메타데이터 검증
    # 텍스트 Document
    assert added_documents[0].page_content == "This is the main text."
    assert added_documents[0].metadata == {
        "page_number": 1, "content_type": "text", "chapter_path": "Chapter 1", "image_path": "/path/to/image.png"
    }

    # 테이블 Document
    assert added_documents[1].page_content == "| col1 | col2 |\n|---|---|"
    assert added_documents[1].metadata == {
        "page_number": 1, "content_type": "table", "table_index": 0, "chapter_path": "Chapter 1", "image_path": "/path/to/image.png"
    }

    # 이미지 설명 Document
    assert added_documents[2].page_content == "A description of an image."
    assert added_documents[2].metadata == {
        "page_number": 1, "content_type": "image_description", "image_index": 0,
        "chapter_path": "Chapter 1", "image_path": "/path/to/image.png", "image_caption": "A caption."
    }


def test_add_page_content_to_vector_db_empty():
    """콘텐츠가 없을 때 벡터 스토어에 추가하지 않는 기능 테스트"""
    empty_content = PageContent(text="", tables=[], images=[], chapter_path=None)
    mock_vector_db = MagicMock(spec=Chroma)

    add_page_content_to_vector_db(empty_content, 1, "/path/to/image.png", mock_vector_db)

    mock_vector_db.add_documents.assert_not_called()
