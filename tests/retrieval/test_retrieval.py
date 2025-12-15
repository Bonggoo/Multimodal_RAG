import pytest
from unittest.mock import patch, MagicMock, call
import os

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_chroma import Chroma

# 테스트 대상 모듈 임포트
from src.retrieval.retriever import get_retriever
from src.retrieval.generator import generate_answer_with_rag, format_docs, get_image_paths

# --- get_retriever 테스트 ---

@patch('src.retrieval.retriever.get_vector_store')
@patch('src.retrieval.retriever.BM25Retriever')
@patch('src.retrieval.retriever.EnsembleRetriever')
def test_get_retriever_success(mock_ensemble_retriever, mock_bm25_retriever, mock_get_vector_store):
    """Retriever 생성 성공 테스트 (EnsembleRetriever)"""
    mock_vector_store = MagicMock(spec=Chroma)
    mock_vector_retriever = MagicMock(spec=BaseRetriever)
    mock_vector_store.as_retriever.return_value = mock_vector_retriever
    
    # Mock collection data for BM25
    mock_vector_store.get.return_value = {
        "documents": ["doc1", "doc2"],
        "metadatas": [{"source": "1"}, {"source": "2"}]
    }
    
    mock_get_vector_store.return_value = mock_vector_store
    
    # Mock BM25 return
    mock_bm25_instance = MagicMock()
    mock_bm25_retriever.from_documents.return_value = mock_bm25_instance

    # Mock Ensemble return
    mock_ensemble_instance = MagicMock()
    mock_ensemble_retriever.return_value = mock_ensemble_instance
    
    # 함수 실행
    retriever = get_retriever(search_kwargs={"k": 3}, force_update=True)
    
    # Assertions
    mock_get_vector_store.assert_called_once()
    mock_vector_store.get.assert_called_once()
    mock_bm25_retriever.from_documents.assert_called_once()
    mock_ensemble_retriever.assert_called_once()
    assert retriever == mock_ensemble_instance


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

@patch('src.retrieval.generator.QueryExpander')
@patch('src.retrieval.generator.ChatGoogleGenerativeAI')
@patch('src.retrieval.generator.load_dotenv', MagicMock())
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_generate_answer_with_rag_success(mock_llm_class, mock_query_expander_class, mock_retriever_with_docs):
    """RAG 체인을 사용한 답변 생성 성공 테스트"""
    # Mock QueryExpander
    mock_expander_instance = MagicMock()
    mock_expander_instance.expand.return_value = "expanded query"
    mock_query_expander_class.return_value = mock_expander_instance

    # Mock LLM and Chain execution
    from langchain_core.messages import AIMessage
    mock_llm_instance = MagicMock()
    # LLM 응답에 인용구 포맷 추가
    expected_message = AIMessage(content="Generated answer. [[Cited Images: /img/p1.png, /img/p2.png]]")
    mock_llm_instance.invoke.return_value = expected_message
    mock_llm_instance.return_value = expected_message # RunnableSequence might call it as a callable
    mock_llm_class.return_value = mock_llm_instance

    query = "test query"
    result = generate_answer_with_rag(query, mock_retriever_with_docs)

    # Assertions
    assert isinstance(result, dict)
    assert "answer" in result
    assert "image_paths" in result
    assert "expanded_query" in result
    assert result["answer"] == "Generated answer."
    assert result["expanded_query"] == "expanded query"
    assert set(result["image_paths"]) == {'/img/p1.png', '/img/p2.png'}
    
    mock_expander_instance.expand.assert_called_once_with(query)
    mock_retriever_with_docs.invoke.assert_called_once_with("expanded query")


@patch('src.retrieval.generator.QueryExpander')
@patch('src.retrieval.generator.ChatGoogleGenerativeAI')
@patch('src.retrieval.generator.load_dotenv', MagicMock())
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_generate_answer_with_rag_no_results(mock_llm_class, mock_query_expander_class):
    """Retriever가 문서 없이 빈 리스트를 반환할 때의 테스트"""
    mock_retriever = MagicMock(spec=BaseRetriever)
    mock_retriever.invoke.return_value = [] # 빈 문서 리스트 반환
    
    mock_expander_instance = MagicMock()
    mock_expander_instance.expand.return_value = "expanded query"
    mock_query_expander_class.return_value = mock_expander_instance

    # Even with no context, the LLM is called (context string is empty)
    from langchain_core.messages import AIMessage
    mock_llm_instance = MagicMock()
    expected_message = AIMessage(content="I don't know.")
    mock_llm_instance.invoke.return_value = expected_message
    mock_llm_instance.return_value = expected_message
    mock_llm_class.return_value = mock_llm_instance
    
    query = "test query"
    result = generate_answer_with_rag(query, mock_retriever)

    assert result["answer"] == "I don't know."
    assert result["image_paths"] == []
    mock_retriever.invoke.assert_called_once_with("expanded query")

# Helper function tests
def test_format_docs():
    doc1 = Document(page_content="Content of doc1")
    doc2 = Document(page_content="Content of doc2")
    expected_output = "[Image Source: N/A]\nContent of doc1\n\n[Image Source: N/A]\nContent of doc2"
    assert format_docs([doc1, doc2]) == expected_output

def test_get_image_paths():
    doc1 = Document(page_content="Text", metadata={'image_path': 'path1.png'})
    doc2 = Document(page_content="Text", metadata={'image_path': 'path2.png'})
    doc3 = Document(page_content="Text", metadata={})
    doc4 = Document(page_content="Text", metadata={'image_path': 'path1.png'}) # Duplicate
    assert get_image_paths([doc1, doc2, doc3, doc4]) == ['path1.png', 'path2.png']
