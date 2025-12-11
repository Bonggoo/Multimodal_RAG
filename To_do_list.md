# 멀티모달 RAG 프로젝트 LangChain 리팩토링 작업 목록

> LangChain을 사용하여 프로젝트를 현대화하고, 코드의 복잡성을 줄이며, 유지보수성을 향상시키는 것을 목표로 합니다.

- [x] **1. 프로젝트 설정 및 의존성 업데이트**
    - [x] `requirements.txt`에 LangChain 관련 라이브러리 추가 (`langchain-core`, `langchain-google-genai`, `langchain-community`, `langchain`, `langchain-chroma`, `langchain-text-splitters`, `pymupdf`)
    - [x] 새로운 의존성 설치

- [x] **2. `parsing` 모듈 리팩토링**
    - [x] `src/parsing/schema.py` 파일 생성 및 Pydantic 모델(`PageContent`) 정의
    - [x] `src/parsing/parser.py`를 `ChatGoogleGenerativeAI`와 `.with_structured_output()`을 사용하도록 수정
    - [x] 불필요해진 `src/parsing/client.py` 파일 삭제

- [x] **3. `preprocessing` 모듈 리팩토링**
    - [x] `src/preprocessing/loader.py`를 LangChain의 `PyMuPDFLoader`를 사용하도록 수정
    - [x] 페이지별 처리를 위해 LangChain `Document` 객체를 생성하는 로직으로 변경

- [x] **4. `storage` 모듈 리팩토링**
    - [x] `src/storage/vector_db.py`에서 `GoogleGenerativeAIEmbeddings`와 `Chroma`를 사용하도록 수정
    - [x] `add_page_content_to_db` 함수를 `PageContent` 스키마로부터 LangChain `Document`를 생성하고 ChromaDB에 추가하도록 수정 (의미 기반 청킹 로직 유지)

- [x] **5. `retrieval` 모듈 리팩토링**
    - [x] `src/retrieval/retriever.py`에서 `Chroma.as_retriever()`를 사용하도록 수정
    - [x] `src/retrieval/generator.py`를 LangChain Expression Language (LCEL)을 사용하여 RAG 체인을 생성하도록 수정

- [x] **6. `main.py` 리팩토링**
    - [x] `main.py`가 새로운 LangChain 기반 파이프라인을 사용하도록 로직 업데이트

- [x] **7. 테스트 코드 리팩토링**
    - [x] `tests/parsing/test_parsing.py` 업데이트
    - [x] `tests/preprocessing/test_preprocessing.py` 업데이트
    - [x] `tests/storage/test_storage.py` 업데이트
    - [x] `tests/retrieval/test_retrieval.py` 업데이트

- [x] **8. 문서 업데이트**
    - [x] `개발설계문서.md`를 새로운 LangChain 기반 아키텍처에 맞게 내용 수정

- [x] **9. 최종 정리**
    - [x] 사용하지 않는 파일 및 디렉토리 삭제
    - [x] 최종 코드 리뷰 및 테스트 실행


# 프로젝트 고도화 및 개선 작업 (2025-12-11 추가)

> `개선점.md`에 기술된 검색 성능 향상, 안정성 확보, UX 개선을 목표로 합니다.

- [x] **1. 검색 성능 개선 (Retrieval)**
    - [x] `EnsembleRetriever` 구현: `BM25Retriever` (키워드) + `VectorStoreRetriever` (벡터) 결합
    - [x] 쿼리 확장(Query Expansion) 로직 구현: 사용자 질문을 검색 친화적으로 재작성하는 LLM 체인 추가
    - [x] 파싱 프롬프트 고도화: 핵심 키워드, 챕터 요약 추출 및 메타데이터 추가 로직 반영

- [x] **2. 파싱 안정성 강화 (Parsing)**
    - [x] 복잡한 페이지(이미지 다수)에 대한 JSON 파싱 재시도(Retry) 및 에러 핸들링 로직 강화
    - [x] 파싱 실패 시 대체 로직 또는 로깅 강화

- [x] **3. 사용자 경험 개선 (UX)**
    - [x] 문서 처리 진행률 표시(Progress Bar) 고도화 및 예상 소요 시간 안내 기능 추가