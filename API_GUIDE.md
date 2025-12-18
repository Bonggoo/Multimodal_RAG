# Multimodal RAG API 가이드

이 문서는 Multimodal RAG API의 사용법을 상세히 안내합니다.

## 1. 개요

본 API는 PDF 문서를 기반으로 질의응답을 수행하는 RAG(검색 증강 생성) 시스템을 제공합니다. 주요 기능은 다음과 같습니다.

-   PDF 문서 비동기 업로드 및 처리
-   문서 처리 상태 추적
-   일반 및 스트리밍 방식의 질의응답

## 2. 인증

모든 API 요청은 HTTP 헤더에 API 키를 포함해야 합니다.

-   **Header:** `X-API-Key`
-   **Value:** 서버에 설정된 `BACKEND_API_KEY`

서버 시작 시 이 키를 환경 변수로 설정해야 합니다. (`.env` 파일 사용 가능)

```
# .env 파일 예시
BACKEND_API_KEY="your_secret_api_key"
GOOGLE_API_KEY="your_google_api_key"
```

## 3. API 엔드포인트 상세

### 3.1. 문서 업로드

PDF 문서를 시스템에 등록하고 처리 작업을 시작합니다. 처리는 비동기적으로 수행됩니다.

-   **Endpoint:** `POST /ingest`
-   **Description:** PDF 파일을 업로드하여 처리 작업을 시작합니다.
-   **Request:**
    -   `Content-Type`: `multipart/form-data`
    -   **Body:**
        -   `file`: (file) 업로드할 PDF 파일

-   **Success Response (`202 Accepted`):**
    처리 작업이 성공적으로 시작되면, 추적 가능한 `job_id`를 반환합니다.
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "message": "문서 처리 작업이 시작되었습니다. 상태 확인 API를 통해 진행 상황을 확인하세요."
    }
    ```

### 3.2. 처리 상태 확인

문서 처리 작업의 현재 상태를 확인합니다.

-   **Endpoint:** `GET /ingest/status/{job_id}`
-   **Description:** 주어진 `job_id`에 해당하는 문서 처리 작업의 상태를 반환합니다.
-   **URL Parameters:**
    -   `job_id`: (string, required) `/ingest` 요청 시 반환된 작업 ID

-   **Success Response (`200 OK`):**
    `status` 필드는 `pending`, `processing`, `completed`, `failed` 중 하나의 값을 가집니다.
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "completed",
      "message": "3페이지 중 3페이지 처리 완료.",
      "details": {
        "filename": "test_document.pdf",
        "total_pages": 3,
        "success_count": 3
      }
    }
    ```

### 3.3. 일반 질의응답 (HTTP)

질문을 보내고 전체 답변을 한 번에 받습니다.

-   **Endpoint:** `POST /qa`
-   **Description:** RAG 파이프라인을 통해 질문에 대한 답변을 생성합니다.
-   **Request Body (`application/json`):**
    ```json
    {
      "query": "Your question about the document"
    }
    ```

-   **Success Response (`200 OK`):**
    ```json
    {
      "answer": "This is the generated answer based on the document content.",
      "image_paths": [
        "assets/images/test_document/page_001_thumb.png"
      ],
      "expanded_query": "your question document content expanded for better search"
    }
    ```

### 3.4. 스트리밍 질의응답 (WebSocket)

WebSocket을 통해 실시간으로 답변을 스트리밍 받습니다.

-   **Endpoint:** `WEBSOCKET /ws/qa`
-   **Description:** 실시간 질의응답을 위한 WebSocket 연결을 수립합니다.

-   **메시지 형식:**
    -   **클라이언트 -> 서버:**
        질문을 JSON 형식으로 전송합니다.
        ```json
        {"query": "Your question about the document"}
        ```
    -   **서버 -> 클라이언트:**
        서버는 여러 개의 JSON 메시지를 순차적으로 전송합니다. 각 메시지는 `type` 필드를 가집니다.
        1.  `token`: 답변의 텍스트 조각. 여러 번 전송될 수 있습니다.
            ```json
            {"type": "token", "payload": "This is the first part of the answer"}
            ```
        2.  `metadata`: 답변 생성에 사용된 추가 정보. 스트림의 끝부분에 한 번 전송됩니다.
            ```json
            {
              "type": "metadata",
              "payload": {
                "image_paths": ["assets/images/test_document/page_001_thumb.png"],
                "expanded_query": "your question expanded...",
                "final_answer": "The complete final answer text."
              }
            }
            ```
        3.  `end`: 스트림의 끝을 알립니다.
            ```json
            {"type": "end", "payload": "Stream ended"}
            ```
        4.  `error`: 오류 발생 시 전송됩니다.
            ```json
            {"type": "error", "payload": "An error occurred during processing."}
            ```

## 4. 사용 예제

### 4.1. `curl`을 이용한 HTTP API 테스트

```bash
# 1. 문서 업로드
curl -X POST "http://127.0.0.1:8000/ingest" \
     -H "X-API-Key: your_secret_api_key" \
     -F "file=@/path/to/your/document.pdf"

# 위 명령의 결과에서 "job_id"를 복사합니다.
# 예: "a1b2c3d4-e5f6-7890-1234-567890abcdef"

# 2. 상태 확인 (완료될 때까지 반복)
curl -X GET "http://127.0.0.1:8000/ingest/status/a1b2c3d4-e5f6-7890-1234-567890abcdef" \
     -H "X-API-Key: your_secret_api_key"

# 3. 질의응답
curl -X POST "http://127.0.0.1:8000/qa" \
     -H "X-API-Key: your_secret_api_key" \
     -H "Content-Type: application/json" \
     -d '{"query": "문서의 주요 내용이 무엇인가요?"}'
```

### 4.2. Python을 이용한 WebSocket 테스트

`websocket-client` 라이브러리가 필요합니다. (`pip install websocket-client`)

```python
import websocket
import json

# --- 설정 ---
WS_URL = "ws://127.0.0.1:8000/ws/qa"
API_KEY = "your_secret_api_key"
HEADERS = {"X-API-Key": API_KEY}
QUERY = "문서의 주요 내용이 무엇인가요?"
# ---

ws = None
try:
    ws = websocket.create_connection(WS_URL, header=HEADERS)
    
    print(f"Sending query: '{QUERY}'")
    ws.send(json.dumps({"query": QUERY}))

    print("\n--- Streaming Response ---")
    while True:
        message = json.loads(ws.recv())
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "token":
            print(payload, end="", flush=True)
        elif msg_type == "metadata":
            print("\n\n--- Metadata ---")
            print(f"Cited Images: {payload.get('image_paths')}")
            print("------------------")
        elif msg_type == "end":
            print("\n--- Stream Ended ---")
            break
        elif msg_type == "error":
            print(f"\n\n--- Error: {payload} ---")
            break
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if ws:
        ws.close()

```