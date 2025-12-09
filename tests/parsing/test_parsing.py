import pytest
import os
import json
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

# 테스트 대상 모듈 및 클래스 임포트
from src.parsing.client import get_gemini_client
from src.parsing.parser import parse_page_multimodal, PageContent

# --- get_gemini_client 테스트 ---

@patch('src.parsing.client.load_dotenv')
@patch('src.parsing.client.genai')
def test_get_gemini_client_success(mock_genai, mock_load_dotenv):
    """Gemini 클라이언트 생성 성공 테스트"""
    # 환경 변수 설정 Mock
    with patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake_api_key'}):
        model = get_gemini_client()

        # Assertions
        mock_load_dotenv.assert_called_once()
        mock_genai.configure.assert_called_once_with(api_key='fake_api_key')
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.5-flash')
        assert model == mock_genai.GenerativeModel.return_value

@patch('src.parsing.client.load_dotenv')
def test_get_gemini_client_no_key(mock_load_dotenv):
    """API 키가 없을 때 ValueError 발생 테스트"""
    # GOOGLE_API_KEY가 설정되지 않은 환경을 시뮬레이션
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="GOOGLE_API_KEY가 환경 변수에 설정되지 않았습니다."):
            get_gemini_client()
    mock_load_dotenv.assert_called_once()


# --- parse_page_multimodal 테스트 ---

@pytest.fixture
def mock_gemini_model():
    """Gemini 모델과 generate_content 메서드를 모킹하는 Fixture"""
    with patch('src.parsing.parser.get_gemini_client') as mock_get_client:
        mock_model = MagicMock()
        # mock_model.generate_content.return_value를 각 테스트에서 설정
        mock_get_client.return_value = mock_model
        yield mock_model

def test_parse_page_success(mock_gemini_model):
    """성공적인 파싱 및 유효성 검사 테스트"""
    # Mock 응답 설정
    valid_data = {
        "text": "This is a sample text.",
        "tables": ["| Header |\n| --- |\n| Cell |"],
        "images": [{"description": "An image of a cat.", "caption": "A cute cat"}],
        "chapter_path": "1. Introduction"
    }
    mock_response = MagicMock()
    mock_response.text = json.dumps(valid_data)
    mock_gemini_model.generate_content.return_value = mock_response

    # 함수 실행
    result = parse_page_multimodal(b"dummy pdf bytes")

    # Assertions
    assert isinstance(result, PageContent)
    assert result.text == valid_data["text"]
    assert result.tables[0] == valid_data["tables"][0]
    assert result.images[0].description == valid_data["images"][0]["description"]
    mock_gemini_model.generate_content.assert_called_once()

def test_parse_page_validation_error(mock_gemini_model):
    """Pydantic 유효성 검사 실패 테스트 (필수 필드 누락)"""
    invalid_data = {
        "text": "Missing other fields."
        # "tables", "images" 필드 누락
    }
    mock_response = MagicMock()
    mock_response.text = json.dumps(invalid_data)
    mock_gemini_model.generate_content.return_value = mock_response

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None

def test_parse_page_invalid_json(mock_gemini_model):
    """잘못된 JSON 형식 응답 테스트"""
    mock_response = MagicMock()
    mock_response.text = "this is not a valid json"
    mock_gemini_model.generate_content.return_value = mock_response

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None

def test_parse_page_api_exception(mock_gemini_model):
    """API 호출 시 예외 발생 테스트"""
    mock_gemini_model.generate_content.side_effect = Exception("API limit reached")

    result = parse_page_multimodal(b"dummy pdf bytes")
    assert result is None
