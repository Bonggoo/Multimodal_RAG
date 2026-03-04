# 🧠 Multimodal RAG Chatbot (v2.4)

생산 설비 매뉴얼(PDF)을 위한 **멀티모달 RAG(Retrieval-Augmented Generation)** 시스템입니다.
텍스트뿐만 아니라 **표(Table)**와 **이미지(Image)**까지 이해하며, **Gemini 2.5 Flash Lite** 모델을 활용하여 전문가 수준의 답변을 제공합니다.

---

## 🚀 주요 기능 (Key Features)

### 1. 고성능 멀티모달 파싱 (High-Performance Parsing)
*   **병렬 처리(Parallel Ingestion)**: `asyncio`와 `semaphore`를 사용하여 대용량 PDF를 기존 대비 **3.5배 빠르게** 처리합니다.
*   **Gemini Vision 기반**: PDF의 표 구조와 다이어그램을 텍스트로 변환하여 벡터 DB에 인덱싱합니다.
*   **JSON 캐싱 시스템**: 파싱 결과를 로컬에 JSON으로 저장하여, 동일 문서 재처리 시 **API 비용을 0원으로** 만듭니다.

### 2. 정밀 검색 & 필터링 (Advanced Retrieval)
*   **하이브리드 리트리버**: BM25(형태소 분석기 Okt 통합)와 시맨틱 검색을 결합하여 한국어 기술 용어 검색 정확도를 극대화했습니다.
*   **스마트 라우팅**: 질문에서 페이지 번호를 자동으로 추출하여 검색 범위를 최적화합니다.

### 3. 프리미엄 사용자 경험 (User Experience)
*   **Flutter macOS 클라이언트**: 프리미엄 Glassmorphism 테마와 다이나믹 애니메이션이 적용된 네이티브 앱을 제공합니다.
*   **상태 보존 네비게이션**: `StatefulShellRoute`를 통해 탭 전환 시에도 채팅 내용과 스크롤 위치가 유지됩니다.
*   **구글 로그인 (OAuth 2.0)**: 안전하고 편리한 구글 인증 및 자동 로그인 기능을 지원합니다.

---

## 🛠 기술 스택 (Tech Stack)

### Backend
*   **LLM**: Google Gemini 2.5 Flash Lite
*   **Orchestration**: LangChain, FastAPI
*   **Vector DB**: ChromaDB (Persistent)
*   **Embedding**: Google Generative AI (`gemini-embedding-001`)

### Frontend
*   **Framework**: Flutter (macOS)
*   **State Management**: Riverpod (Generator)
*   **Navigation**: GoRouter (StatefulShellRoute)

---

## 📦 설치 및 실행 (Setup & Run)

### 1. 환경 설정
```bash
# 레포지토리 클론
git clone <URL>
cd Multimodal_RAG

# 백엔드 의존성 설치
poetry install

# 프론트엔드 의존성 설치
cd frontend
flutter pub get
```

### 2. API 키 설정
`.env` 파일을 생성하고 키를 입력하세요.
```ini
GOOGLE_API_KEY=your_gemini_api_key
GCS_BUCKET_NAME=your_gcs_bucket
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
```

### 3. 서버 실행
```bash
# 백엔드 실행
poetry run python main.py serve

# 프론트엔드 실행 (다른 터미널)
cd frontend
flutter run -d macos
```

---

## 📚 문서 (Documentation)
프로젝트 상세 문서는 다음 파일들을 참고하세요:
*   **[API_GUIDE.md](docs/API_GUIDE.md)**: API 엔드포인트 상세 명세 및 인증 방법.
*   **[SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md)**: 전체 시스템 및 프론트엔드 아키텍처.
*   **[walkthrough.md](docs/walkthrough.md)**: 최신 업데이트 내역 보고서.

---

## 🧪 테스트 (Testing)
```bash
# 백엔드 테스트
poetry run python -m pytest tests/api/

# 프론트엔드 테스트 (준비 중)
cd frontend
flutter test
```
