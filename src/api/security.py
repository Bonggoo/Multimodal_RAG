from fastapi import Header, HTTPException, status
from src.config import settings

async def verify_api_key(x_api_key: str = Header(..., description="API 키")):
    """
    API 키를 검증하는 의존성 함수입니다.
    요청 헤더의 X-API-Key 값이 설정된 백엔드 API 키와 일치하는지 확인합니다.
    """
    if x_api_key != settings.BACKEND_API_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
