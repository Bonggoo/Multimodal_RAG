# Multimodal RAG 시스템 설계 문서

## 1. 개요

이 문서는 PDF 문서 기반의 멀티모달(Multimodal) 질의응답(RAG) 시스템의 아키텍처와 구성 요소, 데이터 흐름을 상세히 설명합니다.

본 시스템의 주요 목적은 텍스트와 이미지가 혼합된 PDF 문서의 내용을 이해하고, 사용자의 질문에 대해 문서 기반의 정확한 답변을 생성하는 것입니다. 이를 위해 LangChain 프레임워크를 기반으로 파이프라인을 구축하고, FastAPI를 통해 API 인터페이스를 제공합니다.

## 2. 시스템 아키텍처

전체 시스템은 **CLI**와 **API** 두 개의 진입점을 통해 핵심 **RAG 파이프라인**을 사용합니다.

```mermaid
graph TD
    subgraph "입력 소"
        A[PDF 문서]
        B[사용자 질문]
    end

    subgraph "진입점 (Entrypoints)"
        C[CLI<br>(main.py)]
        D[API<br>(src/api/main.py)]
    end

    subgraph "핵심 파이프라인 (src/rag_pipeline)"
        E(1. 로딩 및 전처리<br>/loader.py, /thumbnail.py)
        F(2. 파싱 및 구조화<br>/parser.py, /schema.py)
        G(3. 임베딩 및 저장<br>/vector_db.py)
        H(4. 검색<br>/retriever.py, /query_expansion.py)
        I(5. 답변 생성<br>/generator.py)
    end
    
    subgraph "데이터 저장소"
        J[Chroma 벡터 DB]
        K[BM25 인덱스]
    end

    L[최종 답변]

    A --> C -- Ingest --> E
    E --> F
    F --> G --> J
    F --> K

    B --> C -- QA --> H
    B --> D -- QA --> H
    H -- 하이브리드 검색 --> J
    H -- 하이브리드 검색 --> K
    J --> I
    K --> I
    I --> L
```

## 3. 주요 구성 요소

### 3.1. RAG 파이프라인 (`src/rag_pipeline`)

핵심 RAG 로직을 수행하는 모듈 집합입니다. 각 모듈은 파이프라인의 특정 단계를 담당합니다.

-   **`loader.py`**: `PyMuPDFLoader`를 사용하여 PDF 문서를 페이지별 `Document` 객체로 로드합니다.
-   **`thumbnail.py`**: 문서 각 페이지의 썸네일 이미지를 생성하여 시각적 출처로 활용합니다.
-   **`parser.py`**: `Gemini Pro` 멀티모달 모델과 `with_structured_output`을 사용하여 각 페이지에서 텍스트, 테이블, 이미지를 분석하고 구조화된 `PageContent` 객체로 변환합니다.
-   **`schema.py`**: 파이프라인 전체에서 사용되는 데이터 구조를 Pydantic 모델로 정의합니다. (예: `PageContent`)
-   **`vector_db.py`**: `Chroma`와 `GoogleGenerativeAIEmbeddings`를 사용하여 파싱된 데이터를 벡터로 변환하고 DB에 저장/검색하는 인터페이스를 제공합니다.
-   **`retriever.py`**: `EnsembleRetriever`를 사용하여 BM25(키워드 기반) 검색과 벡터(의미 기반) 검색을 결합한 하이브리드 검색을 수행합니다.
-   **`query_expansion.py`**: LLM을 사용하여 사용자 질문을 검색에 유리한 여러 하위 질문으로 확장합니다.
-   **`generator.py`**: LangChain Expression Language (LCEL)을 사용하여 검색된 컨텍스트를 바탕으로 최종 답변을 생성하는 RAG 체인을 구성합니다.

### 3.2. API (`src/api`)

FastAPI를 사용하여 RAG 파이프라인을 웹 서비스로 제공합니다.

-   **`main.py`**: FastAPI 앱을 초기화하고 서버를 실행하는 진입점입니다.
-   **`routes.py`**: `/ingest`, `/qa` 등 API 엔드포인트를 정의하고, `rag_pipeline`의 기능을 호출하여 결과를 반환합니다.
-   **`schemas.py`**: API의 요청 및 응답에 사용되는 데이터 모델을 정의합니다.

### 3.3. 설정 (`src/config.py`)

`pydantic-settings`를 사용하여 프로젝트의 모든 설정을 중앙에서 관리합니다. `.env` 파일에서 환경 변수를 로드하며, 타입 안정성을 보장합니다.

## 4. 기술 스택

-   **코어 프레임워크**: `LangChain`, `FastAPI`
-   **CLI**: `Typer`
-   **웹 서버**: `Uvicorn`
-   **임베딩 모델**: Google `text-embedding-004`
-   **생성/파싱 모델**: Google `Gemini` 계열 모델
-   **벡터 데이터베이스**: `ChromaDB`
-   **한국어 자연어 처리**: `konlpy` (Okt)
-   **설정 관리**: `pydantic-settings`
-   **의존성 관리**: `Poetry`

## 5. 환경 설정 및 실행

### 5.1. 환경 설정

-   **의존성 설치**: `poetry install` 명령어로 `pyproject.toml`에 명시된 모든 패키지를 설치합니다.
-   **API 키**: 프로젝트 루트에 `.env` 파일을 생성하고 `GOOGLE_API_KEY`를 설정합니다.
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

### 5.2. 실행

-   **CLI**: `main.py`를 직접 실행하여 문서를 처리하거나 질문합니다.
    ```bash
    # 문서 처리
    python main.py ingest "path/to/doc.pdf"

    # 질의응답
    python main.py qa "Your question here"
    ```
-   **API 서버**: `uvicorn`을 사용하여 FastAPI 서버를 실행합니다.
    ```bash
    uvicorn src.api.main:app --reload
    ```
