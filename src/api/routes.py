import shutil
import time
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

from src.api.schemas import (
    QARequest, QAResponse, AsyncIngestResponse, JobStatusResponse, 
    DocumentListResponse, DeleteDocumentResponse, QAFilters, 
    FeedbackRequest, UserProfile, SessionListResponse, SessionDetailResponse
)
from src.api.services import get_indexed_documents, delete_document
from src.api.logs import log_qa_history, log_feedback, load_sessions_metadata, get_session_history, delete_session, update_session_metadata
from src.api.auth import verify_google_token, get_current_user
import asyncio
import uuid
from src.rag_pipeline.loader import load_pdf_as_documents
from src.rag_pipeline.thumbnail import create_thumbnails
from src.rag_pipeline.parser import parse_page_multimodal_async
from src.rag_pipeline.vector_db import get_vector_store, add_page_content_to_vector_db
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.generator import generate_answer_with_rag, generate_answer_with_rag_streaming, generate_session_title
from src.config import settings
from src.services.storage import storage_manager
import fitz

# HTTP 엔드포인트용 라우터 (개별 API에서 인증 처리)
router = APIRouter()
# WebSocket 엔드포인트용 라우터 (별도 인증)
ws_router = APIRouter()

# --- Background Task ---

async def process_document_background(
    job_id: str,
    file_path: str,
    filename: str,
    job_status_db: Dict[str, Any],
    app_state: Any,
    uid: str = None
):
    """
    PDF 문서 처리 백그라운드 작업 (비동기 병렬 처리).
    완료 후에는 메모리에 캐시된 리트리버를 업데이트합니다. (성능 로깅 포함)
    """
    print(f"\n--- Parallel Ingestion Pipeline Benchmark for {filename} ---")
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

        # GCS에서 기존 DB 다운로드 (기존 인덱스가 있는 경우 확보)
        if uid:
            try:
                storage_manager.sync_db_from_gcs(uid)
            except Exception as e:
                print(f"GCS DB 다운로드 실패 (신규 유저일 수 있음): {e}")

        vector_store = get_vector_store(uid=uid)
        original_pdf_doc = fitz.open(file_path)
        
        # 2. 썸네일 생성
        thumb_start_time = time.time()
        thumbnail_paths = create_thumbnails(original_pdf_doc, doc_name, uid=uid)
        thumb_time = time.time() - thumb_start_time
        print(f"[2] Thumbnail Creation Time: {thumb_time:.4f}s")

        # 3. 페이지별 처리 (비동기 병렬 파싱)
        page_processing_start_time = time.time()
        
        # 동시성 제어를 위한 세마포어 (150개 동시 처리로 상향)
        semaphore = asyncio.Semaphore(150)
        
        tasks = []
        page_data_list = [] # (page_num, bytes, thumbnail_path)

        # 페이지 바이트 미리 추출 (fitz는 동기 함수이므로 미리 추출)
        for i in range(total_pages):
            page_num = i + 1
            writer = fitz.open()
            writer.insert_pdf(original_pdf_doc, from_page=i, to_page=i)
            page_bytes = writer.write()
            writer.close()
            
            page_thumbnail_path = next((p for p in thumbnail_paths if f"page_{page_num:03d}" in p), None)
            if page_thumbnail_path:
                page_data_list.append((page_num, page_bytes, page_thumbnail_path))

        processed_count = 0

        async def parse_and_track(p_num, p_bytes, p_thumb):
            nonlocal processed_count
            result = await parse_page_multimodal_async(p_bytes, semaphore, doc_name=doc_name, page_num=p_num)
            
            processed_count += 1
            progress = round(processed_count / total_pages * 100)
            # 상태 업데이트 (비동기 환경에서 dict 업데이트는 안전함)
            job_status_db[job_id]["details"]["progress"] = progress
            
            return p_num, p_thumb, result

        tasks = [parse_and_track(pn, pb, pt) for pn, pb, pt in page_data_list]
        
        # 모든 태스크 동시 실행
        results = await asyncio.gather(*tasks)
        
        # 결과 처리: 문서 제목 추출 (타이틀은 보통 첫 페이지에 있으므로 첫 페이지 결과를 우선 확인)
        extracted_title = None
        # results는 (page_num, thumbnail_path, parsed_content) 튜플의 리스트
        # page_num 기준으로 정렬 (병렬 처리로 순서가 섞였을 수 있음)
        sorted_results = sorted(results, key=lambda x: x[0])
        
        for page_num, thumbnail_path, parsed_content in sorted_results:
             if parsed_content and parsed_content.document_title:
                 extracted_title = parsed_content.document_title
                 print(f"Extracted Document Title: {extracted_title}")
                 break
        
        # DB 저장 (추출된 타이틀을 모든 청크에 메타데이터로 적용)
        success_count = 0
        for page_num, thumbnail_path, parsed_content in results:
            if parsed_content:
                try:
                    add_page_content_to_vector_db(parsed_content, page_num, thumbnail_path, vector_store, document_title=extracted_title)
                    success_count += 1
                except Exception as e:
                    print(f"Error adding page {page_num} to DB: {e}")

        page_processing_time = time.time() - page_processing_start_time
        print(f"[3] Parallel Pages Processing Time ({total_pages} pages): {page_processing_time:.4f}s")

        original_pdf_doc.close()
        
        # 4. 디스크의 인덱스 업데이트
        get_retriever(uid=uid, force_update=True)
        
        # 4.1 GCS로 업데이트된 DB 업로드 (영구 저장)
        if uid:
            try:
                storage_manager.sync_db_to_gcs(uid)
                print(f"GCS DB 업로드 완료 (UID: {uid})")
            except Exception as e:
                print(f"GCS DB 업로드 실패: {e}")

        # 5. 메모리에 캐시된 리트리버 업데이트
        new_retriever = get_retriever(uid=uid, force_update=False)
        if not hasattr(app_state, "retrievers"):
            app_state.retrievers = {}
        app_state.retrievers[uid] = new_retriever
        print(f"[5] In-Memory Retriever Updated (UID: {uid})")

        # 6. 생성된 썸네일 GCS 업로드 (영구 저장)
        if uid:
            try:
                local_thumb_dir = os.path.join("assets/images", uid, doc_name)
                storage_manager.upload_directory(local_thumb_dir, f"{uid}/thumbnails/{doc_name}")
                print(f"Thumbnails uploaded for {doc_name} (UID: {uid})")
            except Exception as e:
                print(f"Thumbnail GCS upload failed: {e}")

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
    file: UploadFile = File(...),
    force: bool = Query(False, description="이미 존재하는 문서라도 강제로 다시 인제스트할지 여부"),
    current_user: dict = Depends(get_current_user)
):
    """
    PDF 파일을 업로드하여 RAG 시스템에 등록하는 작업을 시작합니다.
    GCS의 유저별 격리 폴더에 저장됩니다.
    """
    uid = current_user.get("sub")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    uid = current_user.get("sub")
    doc_name = Path(file.filename).stem
    indexed_docs = get_indexed_documents(uid=uid)
    if not force and any(d["filename"] == doc_name for d in indexed_docs):
        raise HTTPException(
            status_code=409, 
            detail=f"이미 '{doc_name}' 문서가 인덱싱되어 있습니다. 다시 인제스트하려면 force=true 파라미터를 사용하세요."
        )

    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")

    # GCS 업로드
    try:
        remote_path = f"{uid}/uploads/{file_id}_{file.filename}"
        storage_manager.upload_file(str(file_path), remote_path)
    except Exception as e:
        print(f"GCS 업로드 실패: {e}")
        # 로컬에는 저장되어 있으므로 계속 진행 (추후 GCS 기반 인제스션 고려)

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
        request.app.state,
        uid # UID 전달
    )

    return AsyncIngestResponse(
        job_id=job_id,
        message="문서 처리 작업이 시작되었습니다. 상태 확인 API를 통해 진행 상황을 확인하세요."
    )

@router.get("/ingest/status/{job_id}", response_model=JobStatusResponse)
async def get_ingest_status(request: Request, job_id: str, current_user: dict = Depends(get_current_user)):
    """주어진 작업 ID에 대한 문서 처리 상태를 반환합니다."""
    job_status_db = request.app.state.job_status
    status = job_status_db.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="작업 ID를 찾을 수 없습니다.")
    return JobStatusResponse(**status)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(current_user: dict = Depends(get_current_user)):
    """
    특정 유저의 RAG 시스템에 인덱싱된 모든 문서의 목록을 반환합니다.
    """
    try:
        uid = current_user.get("sub")
        # GCS 동기화 (기존 데이터 확인용)
        try:
            storage_manager.sync_db_from_gcs(uid)
            # 세션 목록도 GCS에서 동기화
            storage_manager.download_file(f"{uid}/sessions.json", f"data/{uid}/sessions.json")
        except: pass

        doc_names = get_indexed_documents(uid=uid)
        return DocumentListResponse(documents=doc_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록을 가져오는 중 오류 발생: {e}")


@router.delete("/documents/{doc_name}", response_model=DeleteDocumentResponse)
async def delete_document_endpoint(request: Request, doc_name: str, current_user: dict = Depends(get_current_user)):
    """
    지정된 문서를 해당 유저의 RAG 시스템에서 삭제합니다.
    """
    try:
        uid = current_user.get("sub")
        result = delete_document(uid, doc_name, request.app.state)
        # 삭제 후 GCS에도 반영
        storage_manager.sync_db_to_gcs(uid)
        return DeleteDocumentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 중 오류 발생: {e}")

@router.post("/feedback")
async def receive_feedback(feedback: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    """
    사용자 피드백을 수신하여 유저별 로그 폴더 및 GCS에 저장합니다.
    """
    try:
        uid = current_user.get("sub")
        log_feedback(uid, feedback.trace_id, feedback.score, feedback.comment)
        return {"status": "success", "message": "Feedback received"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# --- 세션 관리 API ---

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """유저의 채팅 세션 목록을 반환합니다."""
    uid = current_user.get("sub")
    # 최신 메타데이터 GCS에서 로드 시도
    try: storage_manager.download_file(f"{uid}/sessions.json", f"data/{uid}/sessions.json")
    except: pass
    
    sessions = load_sessions_metadata(uid)
    return SessionListResponse(sessions=sessions)

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str, current_user: dict = Depends(get_current_user)):
    """특정 세션의 상세 대화 내역을 반환합니다."""
    uid = current_user.get("sub")
    # 개별 세션 파일 GCS에서 로드 시도
    try: storage_manager.download_file(f"{uid}/sessions/{session_id}.jsonl", f"data/{uid}/sessions/{session_id}.jsonl")
    except: pass
    
    sessions = load_sessions_metadata(uid)
    title = next((s["title"] for s in sessions if s["session_id"] == session_id), "알 수 없는 채팅")
    
    messages = get_session_history(uid, session_id)
    return SessionDetailResponse(session_id=session_id, title=title, messages=messages)

@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str, current_user: dict = Depends(get_current_user)):
    """세션을 삭제합니다."""
    uid = current_user.get("sub")
    delete_session(uid, session_id)
    return {"status": "success", "message": "Session deleted"}

@router.post("/qa", response_model=QAResponse)
async def ask_question(request: Request, qa_request: QARequest, current_user: dict = Depends(get_current_user)):
    """
    RAG 파이프라인을 통해 질문에 대한 답변을 생성합니다. (유저별 리트리버 사용)
    """
    try:
        uid = current_user.get("sub")
        
        # 세션 ID 처리
        session_id = qa_request.session_id
        is_new_session = False
        if not session_id:
            session_id = str(uuid.uuid4())
            is_new_session = True
            
        # 유저별 리트리버 관리
        if not hasattr(request.app.state, "retrievers"):
            request.app.state.retrievers = {}
        
        if uid not in request.app.state.retrievers:
            # GCS 동기화 후 리트리버 생성
            try: storage_manager.sync_db_from_gcs(uid)
            except: pass
            request.app.state.retrievers[uid] = get_retriever(uid=uid)

        retriever = request.app.state.retrievers[uid]
        query_expander = request.app.state.query_expander
        if retriever is None or query_expander is None:
            raise HTTPException(status_code=503, detail="Retriever or Query Expander is not available.")

        result = generate_answer_with_rag(qa_request.query, retriever, query_expander, qa_request.filters, qa_request.history, qa_request.user_profile)
        
        # 새 세션인 경우 제목 생성
        if is_new_session:
            title = generate_session_title(qa_request.query)
            update_session_metadata(uid, session_id, title=title)

        # Trace ID 생성 및 로그 기록 (UID & Session ID 포함)
        trace_id = uuid.uuid4()
        log_qa_history(uid, session_id, str(trace_id), qa_request.query, result["answer"], qa_request.filters.dict() if qa_request.filters else None)

        return QAResponse(
            answer=result["answer"],
            retrieved_images=result["image_paths"],
            session_id=session_id,
            trace_id=trace_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {e}")

@ws_router.websocket("/ws/qa")
async def websocket_qa(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket을 통해 실시간으로 RAG 파이프라인에 질문하고 스트리밍 답변을 받습니다.
    'token' 쿼리 파라미터로 Google ID Token 인증을 수행합니다.
    """
    if not token:
        await websocket.close(code=1008, reason="Missing Token")
        return
        
    try:
        user_info = verify_google_token(token)
    except Exception as e:
        await websocket.close(code=1008, reason=f"Invalid Token: {str(e)}")
        return
        
    await websocket.accept()
    uid = user_info.get("sub")
    
    if not hasattr(websocket.app.state, "retrievers"):
        websocket.app.state.retrievers = {}
        
    if uid not in websocket.app.state.retrievers:
        try: storage_manager.sync_db_from_gcs(uid)
        except: pass
        websocket.app.state.retrievers[uid] = get_retriever(uid=uid)

    retriever = websocket.app.state.retrievers[uid]
    query_expander = websocket.app.state.query_expander

    if retriever is None or query_expander is None:
        await websocket.send_json({"type": "error", "payload": "Retriever or Query Expander is not available."})
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("query")
            filters_dict = data.get("filters")
            filters = QAFilters(**filters_dict) if filters_dict else None

            if not query:
                await websocket.send_json({"type": "error", "payload": "Query not provided"})
                continue

            try:
                session_id = data.get("session_id")
                is_new_session = False
                if not session_id:
                    session_id = str(uuid.uuid4())
                    is_new_session = True
                
                history = data.get("history")
                user_profile_dict = data.get("user_profile")
                user_profile = UserProfile(**user_profile_dict) if user_profile_dict else None
                
                final_answer = ""
                async for chunk in generate_answer_with_rag_streaming(query, retriever, query_expander, filters, history, user_profile):
                    # 세션 ID를 메타데이터에 포함시켜 전송
                    if chunk["type"] == "metadata":
                        chunk["payload"]["session_id"] = session_id
                        final_answer = chunk["payload"].get("final_answer", "")
                        
                        # 새 세션인 경우 제목 생성 및 메타데이터 업데이트
                        if is_new_session:
                            title = generate_session_title(query, final_answer)
                            update_session_metadata(uid, session_id, title=title)
                            chunk["payload"]["session_title"] = title
                            is_new_session = False # 제목은 한 번만 생성
                        
                        # 대화 로그 기록
                        trace_id = uuid.uuid4()
                        log_qa_history(uid, session_id, str(trace_id), query, final_answer, filters.dict() if filters else None)
                        chunk["payload"]["trace_id"] = str(trace_id)

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
