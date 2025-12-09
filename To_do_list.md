# 📝 To-Do List for Low-Resource Multimodal RAG (Phase 1)

**목표:** 단일 PDF 문서를 입력받아 페이지별로 분할 및 파싱하고, ChromaDB에 벡터로 저장하여, 질문에 대해 텍스트와 원본 이미지를 함께 답변하는 CLI 시스템 구축.

## 1. 프로젝트 설정 및 환경 구성 (Setup)
- [x] **프로젝트 초기화:** `poetry` 또는 `pip`를 사용한 가상환경 생성 및 `.gitignore` 설정
- [x] **필요 라이브러리 설치:**
    - `pymupdf` (PDF 처리)
    - `google-genai` (Gemini API & Embeddings)
    - `chromadb` (Vector DB)
    - `python-dotenv` (환경변수 관리)
- [x] **API 키 설정:** `.env` 파일 생성 및 `GOOGLE_API_KEY` 등록
- [x] **Git 저장소 초기화:** `git init` 및 초기 커밋

## 2. 전처리 모듈 구현 (Preprocessing Layer)
- [x] **PDF 로더 구현:** PyMuPDF(`fitz`)를 이용하여 PDF 파일 로드 기능 구현
- [x] **페이지 분할기(Splitter) 구현:**
    - PDF를 1페이지 단위의 개별 PDF 파일(bytes)로 분리하는 함수 작성
- [x] **썸네일 생성기 구현:**
    - 각 페이지를 이미지(PNG/WebP)로 렌더링하여 `./assets/images` 에 저장하는 기능
    - 파일명 규칙 정의 (예: `doc_name_p001.png`)
- [x] **단위 테스트 작성:** `pytest`를 사용하여 전처리 모듈의 각 함수 테스트
- [x] **Commit:** `git commit -m "feat: 전처리 모듈 구현"`

## 3. 파싱 및 구조화 모듈 구현 (Parsing Layer)
- [x] **Gemini 클라이언트 설정:** `google-genai` 라이브러리로 Gemini 2.5 Flash 모델 연결
- [x] **멀티모달 파싱 함수 구현:**
    - 입력: 단일 페이지 PDF (Bytes)
    - 프롬프트: "텍스트, 표(Markdown), 이미지 묘사 추출 및 챕터 정보(`chapter_path`) 태깅"
    - 출력: 정형화된 JSON 객체 반환
- [x] **구조화 데이터 정제:** 파싱된 JSON 결과에서 오류 처리 및 데이터 검증 로직 추가
- [x] **단위 테스트 작성:** `pytest`를 사용하여 파싱 및 구조화 모듈 테스트
- [x] **Commit:** `git commit -m "feat: 파싱 및 구조화 모듈 구현"`

## 4. 저장소 모듈 구현 (Storage Layer)
- [x] **ChromaDB 초기화:** Persistent Client 설정 및 Collection 생성 (`manual_rag`)
- [x] **임베딩 함수 구현:** Google GenAI Embeddings API 연동
- [x] **데이터 적재(Indexing) 함수:**
    - 파싱된 텍스트/표/이미지 설명을 각각 별도의 Document로 변환
    - Metadata에 `page`, `chapter_path`, `image_path`(썸네일 경로) 매핑
    - DB에 `add()` 하는 로직 구현
- [x] **단위 테스트 작성:** `pytest`를 사용하여 저장소 모듈 테스트
- [x] **Commit:** `git commit -m "feat: 저장소 모듈 구현"`

## 5. 검색 및 답변 모듈 구현 (Retrieval & Generation Layer)
- [x] **검색기(Retriever) 구현:**
    - 사용자 질문을 임베딩하여 ChromaDB에서 유사 청크(Top-K) 검색
    - (옵션) `where` 필터를 이용한 메타데이터 검색 기능 준비
- [x] **답변 생성기(Generator) 구현:**
    - 검색된 Context(텍스트+표)와 질문을 합쳐 LLM 프롬프트 구성
    - 검색된 결과에 '이미지' 타입이 있다면, 해당 `image_path`를 답변 끝에 첨부하도록 로직 작성
- [x] **단위 테스트 작성:** `pytest`를 사용하여 검색 및 답변 모듈 테스트
- [-] **Commit:** `git commit -m "feat: 검색 및 답변 모듈 구현"`

## 6. 메인 로직 및 CLI 인터페이스 (Application)
- [ ] **파이프라인 통합:** `Ingestion`(PDF->DB)과 `QA`(질문->답변) 프로세스를 연결하는 메인 스크립트(`main.py`) 작성
- [ ] **CLI 구현:**
    - 모드 선택: `1. 문서 업로드(적재)`, `2. 질문하기`
    - 사용자 입력 처리 및 결과 출력 (Markdown 포맷 지원)
- [ ] **테스트 및 디버깅:** 샘플 PDF(매뉴얼 등)를 이용한 전체 흐름 테스트
- [ ] **단위 테스트 작성:** `pytest`를 사용하여 전체 파이프라인 통합 테스트
- [ ] **Commit:** `git commit -m "feat: 메인 로직 및 CLI 구현"`

## 7. 문서화 및 마무리
- [ ] **README.md 작성:** 설치 및 실행 방법 가이드
- [ ] **Commit:** `git commit -m "docs: README 작성 및 최종 마무리"`
