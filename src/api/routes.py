import shutil
import time
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

from src.api.schemas import QARequest, QAResponse, AsyncIngestResponse, JobStatusResponse, DocumentListResponse, DeleteDocumentResponse
from src.api.services import get_indexed_documents, delete_document
from src.rag_pipeline.loader import load_pdf_as_documents
from src.rag_pipeline.thumbnail import create_thumbnails
from src.rag_pipeline.parser import parse_page_multimodal
from src.rag_pipeline.vector_db import get_vector_store, add_page_content_to_vector_db
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.generator import generate_answer_with_rag, generate_answer_with_rag_streaming
from src.api.security import verify_api_key
from src.config import settings
import fitz

# HTTP 엔드포인트용 라우터 (API 키 인증 필요)
router = APIRouter(dependencies=[Depends(verify_api_key)])
# WebSocket 엔드포인트용 라우터 (별도 인증)
ws_router = APIRouter()

# --- Background Task ---

def process_document_background(
    job_id: str,
    file_path: str,
    filename: str,
    job_status_db: Dict[str, Any],
    app_state: Any
):
    """
    PDF 문서 처리 백그라운드 작업.
    완료 후에는 메모리에 캐시된 리트리버를 업데이트합니다. (성능 로깅 포함)
    """
    print(f"\n--- Ingestion Pipeline Benchmark for {filename} ---")
    total_start_time = time.time()
    try:
        job_status_db[job_id] = {
            "job_id": job_id, "status": "processing", "message": "문서 처리 시작",
            "details": {"filename": filename, "progress": 0}
        }

        doc_name = Path(filename).stem
        
        # 1. 문서 로드
        load_start_time = time.time()
        pages = load_pdf_as_documents(file_path)
        load_time = time.time() - load_start_time
        print(f"[1] PDF Loading Time: {load_time:.4f}s")
        total_pages = len(pages)
        if not pages:
            raise ValueError("PDF 파일을 읽을 수 없거나 빈 파일입니다.")

        vector_store = get_vector_store()
        original_pdf_doc = fitz.open(file_path)
        
        # 2. 썸네일 생성
        thumb_start_time = time.time()
        thumbnail_paths = create_thumbnails(original_pdf_doc, doc_name)
        thumb_time = time.time() - thumb_start_time
        print(f"[2] Thumbnail Creation Time: {thumb_time:.4f}s")

        # 3. 페이지별 처리 (파싱 및 벡터 저장)
        page_processing_start_time = time.time()
        success_count = 0
        for i, page_doc in enumerate(pages):
            page_num = i + 1
            try:
                writer = fitz.open()
                writer.insert_pdf(original_pdf_doc, from_page=i, to_page=i)
                page_bytes = writer.write()
                writer.close()

                page_thumbnail_path = next((p for p in thumbnail_paths if f"page_{page_num:03d}" in p), None)
                if not page_thumbnail_path:
                    continue

                parsed_content = parse_page_multimodal(page_bytes)
                if parsed_content:
                    add_page_content_to_vector_db(parsed_content, page_num, page_thumbnail_path, vector_store)
                    success_count += 1
                
                progress = round((i + 1) / total_pages * 100)
                job_status_db[job_id]["details"]["progress"] = progress

            except Exception as e:
                print(f"Error processing page {page_num} of {filename}: {e}")
                continue
        page_processing_time = time.time() - page_processing_start_time
        print(f"[3] All Pages Processing Time ({total_pages} pages): {page_processing_time:.4f}s")

        original_pdf_doc.close()
        
        # 4. 디스크의 인덱스 업데이트
        disk_update_start_time = time.time()
        get_retriever(force_update=True)
        disk_update_time = time.time() - disk_update_start_time
        print(f"[4] Retriever Index (Disk) Update Time: {disk_update_time:.4f}s")

        # 5. 메모리에 캐시된 리트리버 업데이트
        mem_update_start_time = time.time()
        app_state.retriever = get_retriever(force_update=False)
        mem_update_time = time.time() - mem_update_start_time
        print(f"[5] In-Memory Retriever Update Time: {mem_update_time:.4f}s")

        job_status_db[job_id] = {
            "job_id": job_id, "status": "completed", "message": f"{total_pages}페이지 중 {success_count}페이지 처리 완료.",
            "details": {"filename": filename, "total_pages": total_pages, "success_count": success_count}
        }

    except Exception as e:
        job_status_db[job_id] = {
            "job_id": job_id, "status": "failed", "message": f"문서 처리 중 오류 발생: {str(e)}",
            "details": {"filename": filename}
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        total_time = time.time() - total_start_time
        print(f"--- Total Ingestion Pipeline Time: {total_time:.4f}s ---")


# --- API Endpoints ---

@router.post("/ingest", response_model=AsyncIngestResponse, status_code=202)
async def ingest_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    PDF 파일을 업로드하여 RAG 시스템에 등록하는 작업을 시작합니다.
    작업 ID를 즉시 반환하며, 실제 처리는 백그라운드에서 수행됩니다.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")

    job_id = str(uuid.uuid4())
    job_status_db = request.app.state.job_status
    
    job_status_db[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "message": "작업 대기 중",
        "details": {"filename": file.filename}
    }

    background_tasks.add_task(
        process_document_background,
        job_id,
        str(file_path),
        file.filename,
        job_status_db,
        request.app.state  # 메모리 캐시 업데이트를 위해 app.state 전달
    )

    return AsyncIngestResponse(
        job_id=job_id,
        message="문서 처리 작업이 시작되었습니다. 상태 확인 API를 통해 진행 상황을 확인하세요."
    )

@router.get("/ingest/status/{job_id}", response_model=JobStatusResponse)
async def get_ingest_status(request: Request, job_id: str):
    """주어진 작업 ID에 대한 문서 처리 상태를 반환합니다."""
    job_status_db = request.app.state.job_status
    status = job_status_db.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="작업 ID를 찾을 수 없습니다.")
    return JobStatusResponse(**status)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    RAG 시스템에 현재 인덱싱된 모든 문서의 목록을 반환합니다.
    """
    try:
        doc_names = get_indexed_documents()
        return DocumentListResponse(documents=doc_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록을 가져오는 중 오류 발생: {e}")


@router.delete("/documents/{doc_name}", response_model=DeleteDocumentResponse)
async def delete_document_endpoint(request: Request, doc_name: str):
    """
    지정된 문서를 RAG 시스템에서 삭제합니다.
    """
    try:
        result = delete_document(doc_name, request.app.state)
        return DeleteDocumentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 중 오류 발생: {e}")


@router.post("/qa", response_model=QAResponse)
async def ask_question(request: Request, qa_request: QARequest):
    """
    RAG 파이프라인을 통해 질문에 대한 답변을 생성합니다. (메모리 캐시된 리트리버와 쿼리 확장기 사용)
    """
    try:
        retriever = request.app.state.retriever
        query_expander = request.app.state.query_expander
        if retriever is None or query_expander is None:
            raise HTTPException(status_code=503, detail="Retriever or Query Expander is not available.")

        result = generate_answer_with_rag(qa_request.query, retriever, query_expander)
        
        return QAResponse(
            answer=result["answer"],
            image_paths=result["image_paths"],
            expanded_query=result.get("expanded_query")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {e}")

@ws_router.websocket("/ws/qa")
async def websocket_qa(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket을 통해 실시간으로 RAG 파이프라인에 질문하고 스트리밍 답변을 받습니다.
    'token' 쿼리 파라미터로 API 키 인증을 수행합니다.
    """
    if not token or token != settings.BACKEND_API_KEY.get_secret_value():
        await websocket.close(code=1008, reason="Invalid API Key")
        return
        
    await websocket.accept()
    retriever = websocket.app.state.retriever
    query_expander = websocket.app.state.query_expander

    if retriever is None or query_expander is None:
        await websocket.send_json({"type": "error", "payload": "Retriever or Query Expander is not available."})
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("query")

            if not query:
                await websocket.send_json({"type": "error", "payload": "Query not provided"})
                continue

            try:
                async for chunk in generate_answer_with_rag_streaming(query, retriever, query_expander):
                    await websocket.send_json(chunk)

            except Exception as e:
                error_message = f"An error occurred: {e}"
                await websocket.send_json({"type": "error", "payload": error_message})
                break

    except WebSocketDisconnect:
        print("Client disconnected from /ws/qa")
    except Exception as e:
        print(f"An unexpected error occurred in /ws/qa: {e}")
    finally:
        print("WebSocket /ws/qa connection closed.")
