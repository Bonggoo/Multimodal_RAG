from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field

class Settings(BaseSettings):
    """
    애플리케이션 전체 설정을 관리하는 클래스입니다.
    .env 파일 및 환경 변수에서 값을 로드하며, 기본값을 제공합니다.
    """
    
    # 필수 설정 (환경 변수에 없으면 오류 발생)
    GOOGLE_API_KEY: SecretStr = Field(..., description="Google Generative AI API 키")
    BACKEND_API_KEY: SecretStr = Field("FASTAPI_SECRET_KEY", description="백엔드 API 보호용 키")
    GOOGLE_OAUTH_CLIENT_ID: str = Field("206500529944-g65qi9u1p55udr3nq255ac0rablp5j1v.apps.googleusercontent.com", description="Google OAuth2 Client ID")

    # 모델 설정
    GEMINI_MODEL: str = Field("gemini-2.5-flash-lite", description="사용할 Gemini 모델 이름")
    GEMINI_EVAL_MODEL: str = Field("gemini-2.5-flash-lite", description="평가(Ragas)에 사용할 심판(Judge) 용 Gemini 모델")
    EMBEDDING_MODEL: str = Field("models/text-embedding-004", description="사용할 Google 임베딩 모델 이름")

    # 데이터베이스 및 스토리지 설정
    CHROMA_DB_DIR: str = Field("chroma_db", description="ChromaDB 데이터 저장 경로")
    COLLECTION_NAME: str = Field("manual_rag", description="ChromaDB 컬렉션 이름")
    BM25_INDEX_PATH: str = Field("data/bm25_index.pkl", description="BM25 인덱스 파일 저장 경로")
    PARSED_DATA_DIR: str = Field("data/parsed", description="파싱된 페이지 JSON 데이터 저장 경로")
    GCS_BUCKET_NAME: str = Field("multimodal-rag-user-data", description="GCS 버킷 이름")

    # .env 파일 로드 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# 설정 객체 인스턴스 생성 (싱글톤처럼 사용)
# 호출 시점에 .env 파일을 로드하고 유효성을 검사합니다.
try:
    settings = Settings()
except Exception as e:
    # API 키가 없는 경우 등 초기화 실패 시 처리 (선택적)
    # 여기서는 로그만 남기거나 에러를 다시 발생시킬 수 있습니다.
    # CI/CD 환경 등 .env가 없는 경우를 위해 예외 처리를 유연하게 할 수도 있습니다.
    print(f"설정 로드 중 경고: {e}")
    # 기본값으로라도 실행되게 하려면 아래와 같이 할 수 있으나, 필수값(API KEY) 때문에 실패할 것입니다.
    # raise e 
