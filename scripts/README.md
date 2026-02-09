# Utility Scripts

이 디렉토리는 프로젝트 관리를 위한 다양한 유틸리티 스크립트를 포함하고 있습니다.

## 실행 방법 (How to Run)
프로젝트 루트 디렉토리에서 다음 명령어로 실행하세요. `src` 모듈을 찾기 위해 `PYTHONPATH` 설정이 필요할 수 있습니다.

```bash
# 기본 실행
poetry run python scripts/utils/check_models.py

# 모듈 경로 문제 발생 시
PYTHONPATH=. poetry run python scripts/utils/check_models.py
```

## 스크립트 목록
*   **`check_models.py`**: Google Gemini 모델 목록 및 정보 조회.
*   **`check_dims.py`**: 임베딩 차원 확인.
*   **`check_gcs.py`**: Google Cloud Storage 연결 확인.
*   **`hard_reset.py`**: 벡터 DB(Chroma) 및 인덱스 초기화 (주의: 데이터 삭제됨).
*   **`list_all_models.py`**: 사용 가능한 모든 모델 나열.
*   **`parse_models.py`**: 모델 응답 파싱 테스트.
*   **`test_curl.sh`**: curl을 이용한 API 엔드포인트 테스트 쉘 스크립트.
