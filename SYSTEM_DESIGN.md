# Multimodal RAG 시스템 설계 문서

## 1. 개요

이 문서는 PDF 문서 기반의 멀티모달(Multimodal) 질의응답(RAG) 시스템의 아키텍처와 구성 요소, 데이터 흐름을 상세히 설명합니다.

본 시스템의 주요 목적은 텍스트와 이미지가 혼합된 PDF 문서의 내용을 이해하고, 사용자의 질문에 대해 문서 기반의 정확한 답변을 생성하는 것입니다. 이를 위해 LangChain 프레임워크를 기반으로 파이프라인을 구축하고, FastAPI를 통해 API 인터페이스를 제공합니다.

## 2. 시스템 아키텍처

전체 시스템은 **API 서버**를 중심으로 구성되며, 개발 및 데이터 관리 목적으로 **CLI 도구**를 함께 제공합니다.

```mermaid
graph TD
    subgraph "사용자 인터페이스"
        UI_HTTP["HTTP 클라이언트<br>(웹 앱, curl 등)"]
        UI_WS["WebSocket 클라이언트<br>(실시간 웹 앱 등)"]
        UI_CLI["개발자/운영자<br>(CLI)"]
    end

    subgraph "진입점 (Entrypoints)"
        D[FastAPI 서버<br>(src/api/main.py)]
        C[CLI 도구<br>(main.py)]
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
    M[작업 상태 DB<br>(In-Memory)]

    UI_HTTP -- "/ingest (PDF)" --> D
    UI_HTTP -- "/qa" --> D
    UI_WS -- "/ws/qa" --> D
    
    D -- "/ingest (비동기)" --> E
    D -- "상태 조회" --> M
    D -- "QA 요청" --> H

    UI_CLI -- "ingest" --> C
    C -- "직접 처리" --> E
    
    E --> F
    F --> G --> J
    F --> K
    
    H -- "하이브리드 검색" --> J
    H -- "하이브리드 검색" --> K
    J & K --> I --> L
```

## 3. 주요 구성 요소

### 3.1. RAG 파이프라인 (`src/rag_pipeline`)

핵심 RAG 로직을 수행하는 모듈 집합입니다. 각 모듈은 파이프라인의 특정 단계를 담당합니다.

-   **`loader.py`**: `PyMuPDFLoader`를 사용하여 PDF 문서를 페이지별 `Document` 객체로 로드합니다.
-   **`thumbnail.py`**: 문서 각 페이지의 썸네일 이미지를 생성하여 시각적 출처로 활용합니다.
-   **`parser.py`**: `Gemini Pro` 멀티모달 모델과 `with_structured_output`을 사용하여 각 페이지에서 텍스트, 테이블, 이미지를 분석하고 구조화된 `PageContent` 객체로 변환합니다.
-   **`schema.py`**: 파이프라인 전체에서 사용되는 데이터 구조를 Pydantic 모델로 정의합니다. (예: `PageContent`)
-   **`vector_db.py`**: `Chroma`와 `GoogleGenerativeAIEmbeddings`를 사용하여 파싱된 데이터를 벡터로 변환하고 DB에 저장/검색하는 인터페이스를 제공합니다.
-   **`retriever.py`**: `EnsembleRetriever`를 사용하여 BM25(키워드 기반) 검색과 벡터(의미 기반) 검색을 결합한 하이브리드 검색을 수행합니다. 또한, 문서 ID 집합을 비교하여 BM25 인덱스가 변경되었을 때만 재생성하도록 최적화되어 있습니다.
-   **`query_expansion.py`**: LLM을 사용하여 사용자 질문을 검색에 유리한 여러 하위 질문으로 확장합니다.
-   **`generator.py`**: LangChain Expression Language (LCEL)을 사용하여 검색된 컨텍스트를 바탕으로 최종 답변을 생성하는 RAG 체인을 구성합니다. (일반 및 스트리밍 답변 포함)

### 3.2. API 서버 (`src/api`)

FastAPI를 사용하여 RAG 파이프라인을 웹 서비스로 제공합니다.

-   **`main.py`**: FastAPI 앱을 초기화하고, `startup` 이벤트 시 리소스(Retriever, Query Expander)를 로드하며, 인메모리 작업 상태 DB를 관리합니다.
-   **`routes.py`**: API 엔드포인트를 정의합니다.
    -   `POST /ingest`: PDF 문서를 비동기적으로 처리하는 작업을 시작하고 `job_id`를 반환합니다.
    -   `GET /ingest/status/{job_id}`: 문서 처리 작업의 진행 상태를 조회합니다.
    -   `POST /qa`: 일반적인 HTTP 요청-응답 방식으로 질의응답을 수행합니다.
    -   `WEBSOCKET /ws/qa`: WebSocket을 통해 실시간 스트리밍 방식으로 질의응답을 수행합니다.
-   **`schemas.py`**: API의 요청 및 응답에 사용되는 데이터 모델(Pydantic)을 정의합니다.
-   **`security.py`**: `X-API-Key` 헤더를 검증하여 API 접근을 제어하는 인증 로직을 구현합니다.

### 3.3. CLI 도구 (`main.py`)

개발 및 운영 편의를 위해 Typer 기반의 CLI 도구를 제공합니다.
-   `ingest`: 로컬 PDF 파일을 직접 파싱하고 데이터베이스에 저장합니다. (병렬 처리 지원)
-   `qa`: CLI 환경에서 직접 질의응답을 테스트합니다.
-   `serve`: Uvicorn을 사용하여 FastAPI 서버를 실행합니다.

### 3.4. 설정 (`src/config.py`)

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
-   **API 키**: 프로젝트 루트에 `.env` 파일을 생성하고 `GOOGLE_API_KEY`와 `BACKEND_API_KEY`를 설정합니다.
    ```
    # .env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    BACKEND_API_KEY="YOUR_SECRET_KEY_FOR_API_ACCESS"
    ```

### 5.2. 실행

-   **API 서버 (권장)**:
    ```bash
    # main.py의 serve 커맨드 사용
    python main.py serve

    # 또는 uvicorn 직접 실행
    uvicorn src.api.main:app --reload
    ```
-   **CLI (테스트용)**:
    ```bash
    # 문서 처리
    python main.py ingest "path/to/doc.pdf"

    # 질의응답
    python main.py qa "Your question here"
    ```

## 6. 향후 개선 계획 (2025-12-18 업데이트)

### 6.1. 완료된 단계: API 서버 구축 및 보안 강화

-   사내 동료들을 대상으로 한 비공개 테스트를 위해, 회사 특화 데이터에 대해 질의응답할 수 있는 기반을 마련했습니다.
-   **백엔드**: FastAPI를 사용하여 모든 사용자가 동일한 데이터 소스를 공유하는 API 서버를 구축했습니다.
-   **인증**: 외부의 비인가 접근을 막기 위해, API 키 기반 인증을 도입하여 보안을 강화했습니다. (`완료`)

### 6.2. 다음 단계: 프론트엔드 웹 애플리케이션 개발

-   **목표**: 구축된 백엔드 API와 통신하는 반응형 웹 애플리케이션을 개발하여, 비전문가 사용자도 쉽게 RAG 시스템을 활용할 수 있도록 합니다.
-   **기술 스택 (프론트엔드)**:
    -   **프레임워크**: Next.js (React 기반)
    -   **UI 라이브러리**: Material-UI (MUI)
-   **주요 기능**:
    1.  사용자가 질문을 입력하고 답변을 볼 수 있는 **채팅 인터페이스**를 구현합니다.
    2.  WebSocket(`_ws/qa_`)을 우선적으로 사용하여 **실시간 스트리밍 답변**을 표시합니다.
    3.  답변과 함께 제공되는 **관련 이미지(썸네일)**를 시각적으로 표시합니다.
    4.  백엔드 API 호출 시, 미리 정의된 API 키를 HTTP 헤더에 포함하여 전송하는 로직을 안전하게 구현합니다.
