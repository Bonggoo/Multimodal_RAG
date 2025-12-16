import shutil
import tempfile
import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from src.api.schemas import QARequest, QAResponse, IngestResponse
from src.rag_pipeline.loader import load_pdf_as_documents
from src.rag_pipeline.thumbnail import create_thumbnails
from src.rag_pipeline.parser import parse_page_multimodal
from src.rag_pipeline.vector_db import get_vector_store, add_page_content_to_vector_db
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.generator import generate_answer_with_rag
import fitz

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    PDF 파일을 업로드하여 RAG 시스템에 등록합니다.
    (비동기 처리를 위해 BackgroundTasks를 사용할 수도 있지만, 여기서는 동기적으로 처리 후 응답합니다.
    실제 운영 환경에서는 Celery 등을 사용한 비동기 작업 큐가 권장됩니다.)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    # 임시 파일로 저장
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = Path(tmp_file.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {e}")

    try:
        # 1. PDF 로드 확인
        doc_name = Path(file.filename).stem
        pages = load_pdf_as_documents(str(tmp_file_path))
        if not pages:
             raise HTTPException(status_code=400, detail="PDF 파일을 읽을 수 없거나 빈 파일입니다.")
        
        total_pages = len(pages)

        # 2. 썸네일 생성 및 파싱 (간소화된 로직)
        # 주의: API에서 대용량 파일 처리는 타임아웃 위험이 있습니다.
        # 여기서는 CLI 로직을 간소화하여 순차 처리합니다.
        
        vector_store = get_vector_store()
        original_pdf_doc = fitz.open(tmp_file_path)
        thumbnail_paths = create_thumbnails(original_pdf_doc, doc_name)
        
        success_count = 0
        
        for i, page_doc in enumerate(pages):
            page_num = i + 1
            try:
                # 페이지 바이트 추출
                writer = fitz.open()
                writer.insert_pdf(original_pdf_doc, from_page=i, to_page=i)
                page_bytes = writer.write()
                writer.close()
                
                # 썸네일 경로
                # thumbnail_paths 리스트에서 현재 페이지에 해당하는 경로 찾기
                page_thumbnail_path = next((p for p in thumbnail_paths if f"page_{page_num:03d}" in p), None)
                
                if not page_thumbnail_path:
                    continue

                # 파싱
                parsed_content = parse_page_multimodal(page_bytes)
                if parsed_content:
                    add_page_content_to_vector_db(parsed_content, page_num, page_thumbnail_path, vector_store)
                    success_count += 1
                    
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                continue
        
        original_pdf_doc.close()
        
        # 검색 인덱스 갱신 (선택적 - 데이터 양이 많으면 비동기로 빼야 함)
        get_retriever(force_update=True)

        return IngestResponse(
            filename=file.filename,
            total_pages=total_pages,
            status="success",
            message=f"{total_pages}페이지 중 {success_count}페이지 처리 완료."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 처리 중 오류 발생: {e}")
    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


@router.post("/qa", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    RAG 파이프라인을 통해 질문에 대한 답변을 생성합니다.
    """
    try:
        retriever = get_retriever()
        result = generate_answer_with_rag(request.query, retriever)
        
        return QAResponse(
            answer=result["answer"],
            image_paths=result["image_paths"],
            expanded_query=result.get("expanded_query")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {e}")
