import pytest
import os
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

# 테스트 대상 모듈 및 클래스 임포트
from src.parsing.parser import parse_page_multimodal
from src.parsing.schema import PageContent, Image # PageContent 임포트 경로 변경

# --- parse_page_multimodal 테스트 ---

@pytest.fixture
def mock_chat_google_generative_ai():
    """LangChain의 ChatGoogleGenerativeAI와 structured_output, invoke 메서드를 모킹하는 Fixture"""
    with patch('src.parsing.parser.ChatGoogleGenerativeAI') as MockChatGoogleGenerativeAI:
        mock_llm_instance = MagicMock()
        mock_structured_output_instance = MagicMock()
        
        # .with_structured_output() 호출 시 mock 객체 반환
        MockChatGoogleGenerativeAI.return_value.with_structured_output.return_value = mock_structured_output_instance
        
        yield mock_structured_output_instance

@patch('src.parsing.parser.load_dotenv', MagicMock()) # load_dotenv 모킹
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'}) # 환경 변수 설정
def test_parse_page_success(mock_chat_google_generative_ai):
    """성공적인 파싱 및 유효성 검사 테스트"""
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
    # ChatGoogleGenerativeAI가 올바른 인자로 호출되었는지 확인하는 추가 검증이 필요할 수 있습니다.

@patch('src.parsing.parser.load_dotenv', MagicMock())
@patch('src.parsing.parser.time.sleep', MagicMock()) # retry delay 스킵
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_parse_page_validation_error(mock_chat_google_generative_ai):
    """Pydantic 유효성 검사 실패 테스트 (LangChain의 structured_output이 ValidationError를 발생시키는 경우)"""
    # LangChain의 structured_output 내부에서 Pydantic ValidationError 발생 시뮬레이션
    mock_chat_google_generative_ai.invoke.side_effect = Exception("Mock Pydantic Validation Error")

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None
    # Retry logic: 1 initial call + 3 retries = 4 calls
    assert mock_chat_google_generative_ai.invoke.call_count == 4

@patch('src.parsing.parser.load_dotenv', MagicMock())
@patch('src.parsing.parser.time.sleep', MagicMock()) # retry delay 스킵
@patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'})
def test_parse_page_api_exception(mock_chat_google_generative_ai):
    """API 호출 시 예외 발생 테스트"""
    mock_chat_google_generative_ai.invoke.side_effect = Exception("API limit reached")

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None
    # Retry logic: 1 initial call + 3 retries = 4 calls
    assert mock_chat_google_generative_ai.invoke.call_count == 4
