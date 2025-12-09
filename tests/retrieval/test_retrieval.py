import pytest
from unittest.mock import patch, MagicMock

# 테스트 대상 모듈 임포트
from src.retrieval.retriever import search_documents
from src.retrieval.generator import generate_answer

# --- search_documents 테스트 ---

@patch('src.retrieval.retriever.get_chroma_collection')
def test_search_documents(mock_get_collection):
    """문서 검색 기능 테스트"""
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection
    
    query = "test query"
    n_results = 3
    where_filter = {"source": "test"}
    
    # 함수 실행
    search_documents(query, n_results, where_filter)
    
    # Assertions
    mock_get_collection.assert_called_once()
    mock_collection.query.assert_called_once_with(
        query_texts=[query],
        n_results=n_results,
        where=where_filter
    )

@patch('src.retrieval.retriever.get_chroma_collection')
def test_search_documents_no_collection_passed(mock_get_collection):
    """컬렉션이 인자로 전달되지 않았을 때의 동작 테스트"""
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection

    search_documents(query="test")
    
    mock_get_collection.assert_called_once()
    mock_collection.query.assert_called_once()

def test_search_documents_with_collection_passed():
    """컬렉션이 인자로 전달되었을 때의 동작 테스트"""
    mock_collection = MagicMock()
    
    with patch('src.retrieval.retriever.get_chroma_collection') as mock_get_collection:
        search_documents(query="test", collection=mock_collection)
        
        # get_chroma_collection이 호출되지 않아야 함
        mock_get_collection.assert_not_called()
        mock_collection.query.assert_called_once()


# --- generate_answer 테스트 ---

@patch('src.retrieval.generator.get_gemini_client')
def test_generate_answer_success(mock_get_client):
    """답변 생성 성공 테스트 (이미지 경로 포함)"""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is the generated answer."
    mock_model.generate_content.return_value = mock_response
    mock_get_client.return_value = mock_model

    query = "What is this?"
    search_results = {
        'documents': [['doc1 text', 'image desc 1', 'doc2 text']],
        'metadatas': [[
            {'source': 'p1', 'image_path': '/img/p1.png'},
            {'source': 'p1', 'image_path': '/img/p1.png'},
            {'source': 'p2', 'image_path': '/img/p2.png'}
        ]]
    }

    result = generate_answer(query, search_results)

    # Assertions
    mock_get_client.assert_called_once()
    mock_model.generate_content.assert_called_once()
    assert "This is the generated answer." in result
    assert "**관련 이미지:**" in result
    assert "/img/p1.png" in result
    assert "/img/p2.png" in result

def test_generate_answer_no_results():
    """검색 결과가 없을 때의 테스트"""
    result = generate_answer("any query", {})
    assert result == "죄송합니다, 관련 정보를 찾을 수 없습니다."

    result_empty_docs = generate_answer("any query", {'documents': [[]]})
    assert result == "죄송합니다, 관련 정보를 찾을 수 없습니다."
    
@patch('src.retrieval.generator.get_gemini_client')
def test_generate_answer_api_exception(mock_get_client):
    """API 예외 발생 시 테스트"""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_get_client.return_value = mock_model

    search_results = {
        'documents': [['doc1 text']],
        'metadatas': [[{'source': 'p1'}]]
    }
    
    result = generate_answer("query", search_results)
    assert "오류가 발생했습니다" in result

