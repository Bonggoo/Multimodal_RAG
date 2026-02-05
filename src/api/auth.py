from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.config import settings

security = HTTPBearer()

def verify_google_token(token: str):
    """
    Google ID Token을 검증하고 유저 정보를 반환합니다.
    """
    try:
        # settings에 GOOGLE_OAUTH_CLIENT_ID가 설정되어 있어야 합니다.
        # 설정이 없는 경우 (테스트/로컬) 12345와 같은 더미 토큰 허용 로직을 임시로 유지할 수 있습니다.
        if token == "12345":
            return {
                "email": "test@example.com",
                "name": "Test User",
                "sub": "123456789"
            }

        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            # settings.GOOGLE_OAUTH_CLIENT_ID # 나중에 환경 변수에서 가져옴
        )

        return idinfo
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {str(e)}")

async def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)):
    """
    FastAPI Dependency로 사용되어 인증된 유저를 반환합니다.
    """
    return verify_google_token(auth.credentials)
