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