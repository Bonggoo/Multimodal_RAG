# 🧠 Multimodal RAG Chatbot (v2.0)

생산 설비 매뉴얼(PDF)을 위한 **멀티모달 RAG(Retrieval-Augmented Generation)** 시스템입니다.
텍스트뿐만 아니라 **표(Table)**와 **이미지(Image)**까지 이해하며, **Gemini 2.5/3.0** 모델을 활용하여 전문가 수준의 답변을 제공합니다.

---

## 🚀 주요 기능 (Key Features)

### 1. 고성능 멀티모달 파싱 (High-Performance Parsing)
*   **병렬 처리(Parallel Ingestion)**: `asyncio`와 `semaphore`를 사용하여 대용량 PDF를 기존 대비 **3.5배 빠르게** 처리합니다.
*   **Gemini Vision 기반**: PDF의 표 구조와 다이어그램을 텍스트로 변환하여 벡터 DB에 인덱싱합니다.
*   **JSON 캐싱 시스템**: 파싱 결과를 로컬에 JSON으로 저장하여, 동일 문서 재처리 시 **API 비용을 0원으로** 만듭니다.
*   **문서 제목 및 중복 체크**: AI 기반 제목 자동 추출 및 기존 문서 중복 업로드 방지 로직을 지원합니다.

### 2. 정밀 검색 & 필터링 (Advanced Retrieval)
*   **고급 청킹(Semantic Chunking)**: `RecursiveCharacterTextSplitter`를 사용하여 문맥 유지를 최적화했습니다.
*   **메타데이터 필터링**: 특정 문서(`doc_name`)를 지정하여 검색 범위를 좁히고 환각(Hallucination)을 방지합니다.
*   **로컬 임베딩**: `jhgan/ko-sroberta-multitask` 모델을 사용하여 한국어 검색 정확도를 극대화했습니다.

### 3. 품질 보증 & 피드백 (QA & Feedback)
*   **Ragas 평가**: Faithfulness, Answer Relevancy 등 정량적 지표로 RAG 성능을 지속적으로 모니터링합니다.
*   **사용자 피드백 루프**: `trace_id`를 통해 답변에 대한 좋아요/싫어요 피드백을 수집하여 성능 데이터베이스를 구축합니다.

---

## 🛠 기술 스택 (Tech Stack)
*   **LLM**: Google Gemini 2.5 Flash / Pro
*   **Embedding**: HuggingFace (`ko-sroberta`)
*   **Vector DB**: ChromaDB (Persistent)
*   **Framework**: FastAPI, LangChain, Typer
*   **Tooling**: Poetry, Pytest, Ragas

---

## 📦 설치 및 실행 (Setup & Run)

### 1. 환경 설정
```bash
# 레포지토리 클론
git clone <URL>
cd Multimodal_RAG

# 의존성 설치
poetry install
```

### 2. API 키 설정
`.env` 파일을 생성하고 키를 입력하세요.
```ini
GOOGLE_API_KEY=your_gemini_api_key
BACKEND_API_KEY=your_backend_secret_key
GEMINI_MODEL=gemini-2.5-flash-lite
EMBEDDING_DEVICE=cpu  # or mps, cuda
```

### 3. 서버 실행
```bash
# CLI 명령어 사용 (권장)
poetry run python main.py serve

# 또는 Uvicorn 직접 실행
poetry run uvicorn src.api.main:app --reload
```

---

## 📚 문서 (Documentation)
프로젝트 상세 문서는 다음 파일들을 참고하세요:
*   **[API_GUIDE.md](API_GUIDE.md)**: API 엔드포인트 상세 명세 및 사용 예시.
*   **[walkthrough.md](walkthrough.md)**: v2.0 업데이트 내역 및 성능 검증 보고서.
*   **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**: 전체 시스템 아키텍처 다이어그램.

---

## 🧪 테스트 (Testing)
전체 시스템 검증을 위해 `pytest`를 실행합니다.
```bash
# 전체 테스트 실행
poetry run python -m pytest tests/api/

# Ragas 검증 실행 (비용 발생 주의)
poetry run python tests/evaluation/run_eval.py
```
