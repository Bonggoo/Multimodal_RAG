import pytest
from unittest.mock import patch, MagicMock, call
import os

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.messages import AIMessage # Added import
from langchain_chroma import Chroma

# 테스트 대상 모듈 임포트
from src.retrieval.retriever import get_retriever
from src.retrieval.generator import generate_answer_with_rag, format_docs, get_image_paths

# --- get_retriever 테스트 ---

@patch('src.retrieval.retriever.get_vector_store')
def test_get_retriever_success(mock_get_vector_store):
    """Retriever 생성 성공 테스트"""
    mock_vector_store = MagicMock(spec=Chroma)
    mock_retriever = MagicMock(spec=BaseRetriever)
    mock_vector_store.as_retriever.return_value = mock_retriever
    mock_get_vector_store.return_value = mock_vector_store
    
    # 함수 실행
    retriever = get_retriever(search_kwargs={"k": 3})
    
    # Assertions
    mock_get_vector_store.assert_called_once()
    mock_vector_store.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
    assert retriever == mock_retriever


# --- generate_answer_with_rag 테스트 ---

@pytest.fixture
def mock_retriever_with_docs():
    """Document를 반환하는 모의 Retriever Fixture"""
    mock_retriever = MagicMock(spec=BaseRetriever)
    mock_retriever.invoke.return_value = [
        Document(page_content="doc1 text", metadata={'page_number': 1, 'image_path': '/img/p1.png'}),
        Document(page_content="doc2 text", metadata={'page_number': 2, 'image_path': '/img/p2.png'}),
        Document(page_content="doc3 text", metadata={'page_number': 3})
    ]
    return mock_retriever

@patch('src.retrieval.generator.get_rag_chain') # Patch the function that returns the chain
@patch('src.retrieval.generator.load_dotenv', MagicMock())
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_generate_answer_with_rag_success(mock_get_rag_chain, mock_retriever_with_docs):
    """RAG 체인을 사용한 답변 생성 성공 테스트"""
    mock_rag_chain = MagicMock()
    mock_rag_chain.invoke.return_value = "Generated answer." # Mock the chain's final output
    mock_get_rag_chain.return_value = mock_rag_chain

    query = "test query"
    result = generate_answer_with_rag(query, mock_retriever_with_docs)

    # Assertions
    assert isinstance(result, dict)
    assert "answer" in result
    assert "image_paths" in result
    assert result["answer"] == "Generated answer."
    assert set(result["image_paths"]) == {'/img/p1.png', '/img/p2.png'}
    mock_retriever_with_docs.invoke.assert_called_once_with(query) # Retriever is still called for image paths
    mock_get_rag_chain.assert_called_once_with(mock_retriever_with_docs)
    mock_rag_chain.invoke.assert_called_once_with(query)
    # 추가적으로 prompt가 올바르게 구성되었는지 검증할 수 있지만, LCEL 내부 로직이므로 간소화


@patch('src.retrieval.generator.ChatGoogleGenerativeAI')
@patch('src.retrieval.generator.load_dotenv', MagicMock())
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_generate_answer_with_rag_no_results(mock_llm_class):
    """Retriever가 문서 없이 빈 리스트를 반환할 때의 테스트"""
    mock_retriever = MagicMock(spec=BaseRetriever)
    mock_retriever.invoke.return_value = [] # 빈 문서 리스트 반환
    
@patch('src.retrieval.generator.get_rag_chain')
@patch('src.retrieval.generator.load_dotenv', MagicMock())
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_generate_answer_with_rag_no_results(mock_get_rag_chain):
    """Retriever가 문서 없이 빈 리스트를 반환할 때의 테스트"""
    mock_retriever = MagicMock(spec=BaseRetriever)
    mock_retriever.invoke.return_value = [] # 빈 문서 리스트 반환

    mock_rag_chain = MagicMock()
    mock_rag_chain.invoke.return_value = "Generated answer based on no context."
    mock_get_rag_chain.return_value = mock_rag_chain
    
    query = "test query"
    result = generate_answer_with_rag(query, mock_retriever)

    assert result["answer"] == "Generated answer based on no context."
    assert result["image_paths"] == []
    mock_retriever.invoke.assert_called_once_with(query)
    mock_get_rag_chain.assert_called_once_with(mock_retriever)
    mock_rag_chain.invoke.assert_called_once_with(query)


@patch('src.retrieval.generator.get_rag_chain')
@patch('src.retrieval.generator.load_dotenv', MagicMock())
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_generate_answer_with_rag_api_exception(mock_get_rag_chain, mock_retriever_with_docs):
    """API 예외 발생 시 테스트"""
    mock_rag_chain = MagicMock()
    mock_rag_chain.invoke.side_effect = Exception("LLM API Error")
    mock_get_rag_chain.return_value = mock_rag_chain
    
    query = "test query"
    with pytest.raises(Exception, match="LLM API Error"):
        generate_answer_with_rag(query, mock_retriever_with_docs)
    
    mock_retriever_with_docs.invoke.assert_called_once_with(query)
    mock_get_rag_chain.assert_called_once_with(mock_retriever_with_docs)
    mock_rag_chain.invoke.assert_called_once_with(query)
# Helper function tests (optional, but good practice)
def test_format_docs():
    doc1 = Document(page_content="Content of doc1")
    doc2 = Document(page_content="Content of doc2")
    assert format_docs([doc1, doc2]) == "Content of doc1\n\nContent of doc2"

def test_get_image_paths():
    doc1 = Document(page_content="Text", metadata={'image_path': 'path1.png'})
    doc2 = Document(page_content="Text", metadata={'image_path': 'path2.png'})
    doc3 = Document(page_content="Text", metadata={})
    doc4 = Document(page_content="Text", metadata={'image_path': 'path1.png'}) # Duplicate
    assert get_image_paths([doc1, doc2, doc3, doc4]) == ['path1.png', 'path2.png']
