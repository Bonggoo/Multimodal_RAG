import pytest
import os
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

# 테스트 대상 모듈 및 클래스 임포트
from src.rag_pipeline.parser import parse_page_multimodal
from src.rag_pipeline.schema import PageContent, Image

# --- parse_page_multimodal 테스트 ---

@pytest.fixture
def mock_chat_google_generative_ai():
    """LangChain의 ChatGoogleGenerativeAI와 structured_output, invoke 메서드를 모킹하는 Fixture"""
    with patch('src.rag_pipeline.parser.ChatGoogleGenerativeAI') as MockChatGoogleGenerativeAI:
        mock_llm_instance = MagicMock()
        mock_structured_output_instance = MagicMock()
        
        # .with_structured_output() 호출 시 mock 객체 반환
        MockChatGoogleGenerativeAI.return_value.with_structured_output.return_value = mock_structured_output_instance
        
        yield mock_structured_output_instance

@patch('src.rag_pipeline.parser.settings')
def test_parse_page_success(mock_settings, mock_chat_google_generative_ai):
    """성공적인 파싱 및 유효성 검사 테스트"""
    # Mock settings
    mock_settings.GEMINI_MODEL = "mock-model"
    mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "mock-key"

    # Mock 응답 설정
    valid_page_content = PageContent(
        text="This is a sample text.",
        tables=["| Header |\n| --- |\n| Cell |"],
        images=[Image(description="An image of a cat.", caption="A cute cat")],
        chapter_path="1. Introduction"
    )
    mock_chat_google_generative_ai.invoke.return_value = valid_page_content

    # 함수 실행
    result = parse_page_multimodal(b"dummy pdf bytes")

    # Assertions
    assert isinstance(result, PageContent)
    assert result.text == valid_page_content.text
    assert result.tables[0] == valid_page_content.tables[0]
    assert result.images[0].description == valid_page_content.images[0].description
    mock_chat_google_generative_ai.invoke.assert_called_once()

@patch('src.rag_pipeline.parser.time.sleep', MagicMock()) # retry delay 스킵
@patch('src.rag_pipeline.parser.settings')
def test_parse_page_validation_error(mock_settings, mock_chat_google_generative_ai):
    """Pydantic 유효성 검사 실패 테스트 (LangChain의 structured_output이 ValidationError를 발생시키는 경우)"""
    # Mock settings
    mock_settings.GEMINI_MODEL = "mock-model"
    mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "mock-key"

    # LangChain의 structured_output 내부에서 Pydantic ValidationError 발생 시뮬레이션
    mock_chat_google_generative_ai.invoke.side_effect = Exception("Mock Pydantic Validation Error")

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None
    # Retry logic: 1 initial call + 3 retries = 4 calls
    assert mock_chat_google_generative_ai.invoke.call_count == 4

@patch('src.rag_pipeline.parser.time.sleep', MagicMock()) # retry delay 스킵
@patch('src.rag_pipeline.parser.settings')
def test_parse_page_api_exception(mock_settings, mock_chat_google_generative_ai):
    """API 호출 시 예외 발생 테스트"""
    # Mock settings
    mock_settings.GEMINI_MODEL = "mock-model"
    mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "mock-key"

    mock_chat_google_generative_ai.invoke.side_effect = Exception("API limit reached")

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None
    # Retry logic: 1 initial call + 3 retries = 4 calls
    assert mock_chat_google_generative_ai.invoke.call_count == 4