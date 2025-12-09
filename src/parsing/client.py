import os
import google.generativeai as genai
from dotenv import load_dotenv

def get_gemini_client(model_name: str = "gemini-2.5-flash") -> genai.GenerativeModel:
    """
    Google Gemini 클라이언트를 초기화하고 특정 모델을 로드합니다.

    .env 파일에서 GOOGLE_API_KEY를 로드하여 클라이언트를 설정합니다.

    Args:
        model_name (str): 사용할 Gemini 모델의 이름.

    Returns:
        genai.GenerativeModel: 설정된 Gemini 생성 모델 객체.
    
    Raises:
        ValueError: GOOGLE_API_KEY가 .env 파일에 설정되지 않은 경우.
    """
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY가 환경 변수에 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(model_name)
    return model

# 예시: 클라이언트 가져오기
if __name__ == '__main__':
    try:
        flash_model = get_gemini_client()
        print(f"성공적으로 '{flash_model.model_name}' 모델을 로드했습니다.")
        # print(flash_model)
    except ValueError as e:
        print(e)
