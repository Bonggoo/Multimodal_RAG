# Multimodal RAG API 가이드 📚

이 문서는 최적화된 RAG 시스템의 API 사용법을 설명합니다.

## Base URL
`http://localhost:8000`

## 인증 (Authentication)
모든 API 요청 헤더에 API 키를 포함해야 합니다.
`X-API-Key: FASTAPI_SECRET_KEY`

---

## 1. 질문하기 (QA) 🤖
RAG 시스템에 질문하고 답변을 받습니다.

**Endpoint:** `POST /qa`

**Request:**
```json
{
  "query": "HPPF-12 토크 값은?",
  "filters": {
    "doc_name": "QD77MS_위치결정_매뉴얼.pdf" // (선택) 특정 문서에서만 검색
  }
}
```

**Response:**
```json
{
  "answer": "HPPF-12 모델의 토크 값은 0.63 N·m입니다.",
  "retrieved_images": ["data/images/page_12_img_0.png"],
  "doc_name": "QD77MS_위치결정_매뉴얼.pdf",
  "trace_id": "a1b2c3d4-e5f6-..." // 피드백에 사용할 추적 ID
}
```

---

## 2. 문서 업로드 (Ingestion) 📤
PDF 문서를 업로드하여 인덱싱합니다. (비동기 처리)

**Endpoint:** `POST /ingest`
**Content-Type:** `multipart/form-data`

**Body:**
*   `file`: (Binary PDF File)

**Response:**
```json
{
  "job_id": "job_12345",
  "message": "문서 처리 작업이 시작되었습니다..."
}
```

---

## 3. 피드백 보내기 (Feedback) 👍👎
답변 품질에 대한 피드백을 보냅니다. `qa_history` 개선에 사용됩니다.

**Endpoint:** `POST /feedback`

**Request:**
```json
{
  "trace_id": "a1b2c3d4-e5f6-...", // /qa 응답에서 받은 ID
  "score": 1, // 1: 좋아요, -1: 싫어요
  "comment": "답변이 정확합니다!" // (선택)
}
```

---

## 4. 스트리밍 질문 (WebSocket) ⚡️
실시간으로 답변을 한 글자씩 받습니다.

**URL:** `ws://localhost:8000/ws/qa?token=FASTAPI_SECRET_KEY`

**Message (Send):**
```json
{
  "query": "토크 값 알려줘",
  "filters": {"doc_name": "..."}
}
```

**Message (Receive):**
```json
{"answer": "H"}
{"answer": "P"}
...
{"image_paths": [...], "trace_id": "..."} // 마지막 메시지
```

---

## 5. 관리자 도구 🛠

### 문서 목록 조회
`GET /documents`

**Response:**
```json
{
  "documents": [
    {
      "filename": "QD77MS_위치결정_매뉴얼.pdf",
      "title": "QD77MS 위치결정 모듈 사용자 매뉴얼"
    },
    {
      "filename": "test_document.pdf",
      "title": "RAG System User Manual"
    }
  ]
}
```

### 문서 삭제
`DELETE /documents/{doc_name}`

### 성능 평가 (개발자 전용)
터미널에서 실행:
```bash
poetry run python tests/evaluation/run_eval.py
```
*   `tests/evaluation/golden_dataset.json`에 정의된 질문셋으로 성능 측정.
*   결과는 `tests/evaluation/eval_report.csv`에 저장됨.
