import pytest
from unittest.mock import patch, MagicMock, call

# 테스트 대상 모듈 및 클래스 임포트
from src.parsing.parser import PageContent, Image
from src.storage.vector_db import (
    get_google_embedding_function,
    get_chroma_collection,
    add_page_content_to_db,
    COLLECTION_NAME,
    CHROMA_DB_PATH,
)

# --- get_google_embedding_function 테스트 ---

@patch('src.storage.vector_db.load_dotenv')
@patch.dict('os.environ', {'GOOGLE_API_KEY': 'fake_api_key'})
@patch('src.storage.vector_db.embedding_functions.GoogleGenerativeAiEmbeddingFunction')
def test_get_google_embedding_function(mock_embedding_class, mock_load_dotenv):
    """Google 임베딩 함수 생성 테스트"""
    ef = get_google_embedding_function()
    mock_load_dotenv.assert_called_once()
    mock_embedding_class.assert_called_once_with(api_key='fake_api_key')
    assert ef == mock_embedding_class.return_value


# --- get_chroma_collection 테스트 ---

@patch('src.storage.vector_db.get_google_embedding_function')
@patch('src.storage.vector_db.chromadb.PersistentClient')
def test_get_chroma_collection(mock_persistent_client, mock_get_ef):
    """ChromaDB 컬렉션 가져오기/생성 테스트"""
    mock_client_instance = mock_persistent_client.return_value
    mock_collection = MagicMock()
    mock_client_instance.get_or_create_collection.return_value = mock_collection
    mock_ef_instance = mock_get_ef.return_value

    collection = get_chroma_collection()

    mock_persistent_client.assert_called_once_with(path=CHROMA_DB_PATH)
    mock_get_ef.assert_called_once()
    mock_client_instance.get_or_create_collection.assert_called_once_with(
        name=COLLECTION_NAME,
        embedding_function=mock_ef_instance
    )
    assert collection == mock_collection


# --- add_page_content_to_db 테스트 ---

@pytest.fixture
def sample_page_content():
    """테스트용 PageContent 객체 Fixture"""
    return PageContent(
        text="This is the main text.",
        tables=["| col1 | col2 |\n|---|---|"],
        images=[Image(description="A description of an image.", caption="A caption.")],
        chapter_path="Chapter 1"
    )

def test_add_page_content_to_db(sample_page_content):
    """DB에 페이지 콘텐츠 적재 기능 테스트"""
    mock_collection = MagicMock()
    page_num = 1
    img_path = "/path/to/image.png"

    add_page_content_to_db(sample_page_content, page_num, img_path, mock_collection)

    # collection.add가 호출되었는지, 그리고 올바른 인자와 함께 호출되었는지 확인
    mock_collection.add.assert_called_once()
    
    # 호출 인자 추출
    args, kwargs = mock_collection.add.call_args
    
    # 키워드 인자로 호출되었으므로 kwargs 검사
    expected_documents = [
        "This is the main text.",
        "| col1 | col2 |\n|---|---|",
        "A description of an image."
    ]
    expected_ids = [
        "p1_text_0",
        "p1_table_0",
        "p1_image_0"
    ]
    expected_metadatas = [
        {
            "page_number": 1,
            "content_type": "text",
            "chapter_path": "Chapter 1",
            "image_path": "/path/to/image.png",
        },
        {
            "page_number": 1,
            "content_type": "table",
            "chapter_path": "Chapter 1",
            "image_path": "/path/to/image.png",
        },
        {
            "page_number": 1,
            "content_type": "image_description",
            "chapter_path": "Chapter 1",
            "image_path": "/path/to/image.png",
            "image_caption": "A caption."
        },
    ]

    assert kwargs['documents'] == expected_documents
    assert kwargs['ids'] == expected_ids
    assert kwargs['metadatas'] == expected_metadatas

def test_add_page_content_to_db_empty():
    """콘텐츠가 없을 때 DB에 추가하지 않는 기능 테스트"""
    empty_content = PageContent(text="", tables=[], images=[], chapter_path=None)
    mock_collection = MagicMock()

    add_page_content_to_db(empty_content, 1, "/path/to/image.png", mock_collection)

    mock_collection.add.assert_not_called()
