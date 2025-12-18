# Multimodal RAG for Technical Manuals

## 📖 프로젝트 개요 (Overview)

본 프로젝트는 복잡한 기술 매뉴얼(PDF 형식)을 위한 **API 중심의 고급 멀티모달 RAG(Retrieval-Augmented Generation) 시스템**입니다. Google Gemini Pro 멀티모달 모델을 활용하여 텍스트뿐만 아니라 문서 내의 이미지, 테이블까지 깊이 이해하고, 이를 바탕으로 사용자의 질문에 정확하게 답변하는 FastAPI 기반의 웹 서비스를 제공합니다.

## ✨ 주요 기능 (Key Features)

-   **API 중심 설계**: FastAPI를 통해 모든 RAG 기능을 RESTful API와 WebSocket으로 제공하여 어떤 애플리케이션과도 쉽게 통합할 수 있습니다.
-   **비동기 문서 처리**: 대용량 PDF 파일을 업로드하면 백그라운드에서 처리(`ingest`)하고, 작업 ID를 통해 실시간으로 처리 상태를 추적할 수 있습니다.
-   **실시간 스트리밍 답변**: WebSocket을 지원하여 RAG 파이프라인의 답변을 실시간으로 스트리밍받을 수 있어 사용자 경험(UX)을 극대화합니다.
-   **멀티모달 문서 이해**: Gemini 모델을 통해 PDF 페이지의 텍스트, 테이블, 이미지를 동시에 분석하고 구조화된 데이터(`Pydantic` 모델)로 변환합니다.
-   **하이브리드 검색 (Hybrid Search)**: 의미 기반의 벡터 검색(Dense)과 키워드 기반의 BM25 검색(Sparse)을 결합한 `EnsembleRetriever`를 사용하여 검색 정확도를 높입니다.
-   **쿼리 확장 (Query Expansion)**: LLM을 사용하여 사용자의 질문을 검색에 최적화된 여러 키워드로 확장하여 관련성 높은 문서를 효과적으로 찾습니다.
-   **정확한 출처 인용**: 답변 생성 시, LLM이 실제로 참고한 문서 페이지의 이미지를 정확히 식별하고 출처로 함께 제공합니다.

## 🏛️ 아키텍처 (Architecture)

API 서버를 중심으로 사용자와 핵심 RAG 파이프라인이 상호작용합니다.

```mermaid
graph TD
    subgraph "사용자 인터페이스"
        UI_HTTP["HTTP 클라이언트<br>(웹 앱, curl 등)"]
        UI_WS["WebSocket 클라이언트<br>(실시간 웹 앱 등)"]
    end

    subgraph "진입점: FastAPI 서버"
        D[FastAPI 서버<br>(src/api/main.py)]
    end

    subgraph "핵심 파이프라인 (src/rag_pipeline)"
        P["RAG 파이프라인"]
    end
    
    subgraph "데이터 저장소"
        DS["벡터 DB (Chroma)<br>BM25 인덱스"]
    end

    L["최종 답변"]
    M["작업 상태 DB<br>(In-Memory)"]

    UI_HTTP -- "POST /ingest (비동기)" --> D
    UI_HTTP -- "GET /ingest/status/{job_id}" --> D
    UI_HTTP -- "POST /qa" --> D
    UI_WS -- "WEBSOCKET /ws/qa" --> D
    
    D -- "RAG 작업 수행" --> P
    D -- "상태 조회/업데이트" --> M
    P -- "데이터 저장/검색" --> DS
    P -- "답변 생성" --> L
```

## 🛠️ 설치 (Installation)

1.  **Git 저장소 복제:**
    ```bash
    git clone https://github.com/your-username/Multimodal_RAG.git
    cd Multimodal_RAG
    ```

2.  **Poetry를 사용하여 의존성 패키지 설치:**
    *Poetry가 설치되어 있어야 합니다.*
    ```bash
    poetry install
    ```

3.  **가상환경 활성화:**
    ```bash
    poetry shell
    ```

4.  **환경 변수 설정:**
    `.env` 파일을 프로젝트 루트 디렉터리에 생성하고 필요한 API 키를 추가합니다.
    
    ```dotenv
    # .env 파일 예시
    
    # Google Gemini API 키
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    
    # 백엔드 API 접근을 위한 보안 키
    BACKEND_API_KEY="YOUR_CHOSEN_SECRET_KEY"
    ```

## 🚀 사용법 (Usage)

API 서버를 실행하면 모든 기능을 사용할 수 있습니다.

### 1. API 서버 실행

Uvicorn을 사용하여 API 서버를 시작합니다. `main.py`의 `serve` 커맨드를 사용하는 것을 권장합니다.
```bash
python main.py serve
```
서버가 실행되면 브라우저에서 `http://127.0.0.1:8000/docs` 로 접속하여 모든 API 엔드포인트에 대한 상세 문서를 확인할 수 있습니다.

### 2. API 사용 예제

모든 요청의 HTTP 헤더에는 `X-API-Key: YOUR_CHOSEN_SECRET_KEY`가 포함되어야 합니다.

#### 1단계: 문서 업로드 (비동기)
PDF 파일을 업로드하여 처리 작업을 시작합니다. `job_id`가 즉시 반환됩니다.
```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
     -H "X-API-Key: YOUR_CHOSEN_SECRET_KEY" \
     -F "file=@/path/to/your/document.pdf"

# 응답 예시:
# {"job_id":"...","message":"문서 처리 작업이 시작되었습니다..."}
```

#### 2단계: 처리 상태 확인
반환된 `job_id`를 사용하여 문서 처리 상태를 확인합니다. `completed`가 될 때까지 주기적으로 확인할 수 있습니다.
```bash
curl -X GET "http://127.0.0.1:8000/ingest/status/{job_id}" \
     -H "X-API-Key: YOUR_CHOSEN_SECRET_KEY"

# 응답 예시 (완료 시):
# {"job_id":"...","status":"completed","message":"...페이지 처리 완료.","details":{...}}
```

#### 3단계 (옵션 A): 일반 질의응답 (HTTP)
전체 답변을 한 번에 받습니다.
```bash
curl -X POST "http://127.0.0.1:8000/qa" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_CHOSEN_SECRET_KEY" \
     -d '{"query": "문서의 주요 내용이 무엇인가요?"}'

# 응답 예시:
# {"answer":"...","image_paths":["..."],"expanded_query":"..."}
```

#### 3단계 (옵션 B): 스트리밍 질의응답 (WebSocket)
실시간으로 답변을 스트리밍 받습니다. (`pip install websocket-client`)
```python
import websocket
import json

WS_URL = "ws://127.0.0.1:8000/ws/qa"
HEADERS = {"X-API-Key": "YOUR_CHOSEN_SECRET_KEY"}
QUERY = "문서의 주요 내용이 무엇인가요?"

ws = websocket.create_connection(WS_URL, header=HEADERS)
ws.send(json.dumps({"query": QUERY}))

print("--- Streaming Response ---")
while True:
    message = json.loads(ws.recv())
    if message["type"] == "token":
        print(message["payload"], end="", flush=True)
    elif message["type"] == "end":
        print("\n--- Stream Ended ---")
        break
ws.close()
```

### 3. CLI (개발 및 관리용)

`typer`로 구현된 CLI는 API 서버를 통하지 않고 직접 RAG 파이프라인을 실행할 때 유용합니다.
```bash
# 문서 직접 처리 (DB에 저장)
python main.py ingest "path/to/your/document.pdf"

# 직접 질의응답 테스트
python main.py qa "원점 복귀 방식에는 어떤 종류가 있나요?"
```

## 📂 프로젝트 구조

```
/
├───main.py                 # Typer CLI 애플리케이션 진입점 (serve, ingest, qa)
├───pyproject.toml          # Poetry 의존성 및 프로젝트 설정
├───.env                    # 환경 변수 파일 (API 키 등)
├───assets/images/          # 문서 페이지별 썸네일 이미지 저장
├───chroma_db/              # ChromaDB 벡터 데이터베이스
├───data/                   # BM25 인덱스 등
├───src/
│   ├───config.py           # Pydantic을 이용한 중앙 설정 관리
│   ├───api/                # FastAPI 애플리케이션
│   │   ├───main.py         # API 서버 진입점 및 이벤트 핸들러
│   │   ├───routes.py       # API 라우트 정의
│   │   ├───schemas.py      # API 요청/응답 스키마
│   │   └───security.py     # API 키 인증 로직
│   └───rag_pipeline/       # 핵심 RAG 파이프라인 모듈
│       ├───generator.py    # 답변 생성 모듈
│       ├───loader.py       # 문서 로더
│       ├───parser.py       # 멀티모달 파서
│       ├───query_expansion.py # 쿼리 확장 모듈
│       ├───retriever.py    # 하이브리드 검색기
│       ├───schema.py       # 데이터 구조 (Pydantic 모델)
│       ├───thumbnail.py    # 썸네일 생성기
│       └───vector_db.py    # ChromaDB 인터페이스
└───tests/                  # 테스트 코드
```

