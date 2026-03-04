import concurrent.futures
from pathlib import Path
from typing import List, Tuple, Optional
import fitz
from tqdm import tqdm

from src.rag_pipeline.loader import load_pdf_as_documents
from src.rag_pipeline.thumbnail import create_thumbnails
from src.rag_pipeline.parser import parse_page_multimodal
from src.rag_pipeline.vector_db import get_vector_store, add_page_content_to_vector_db
from src.rag_pipeline.retriever import get_retriever

class IngestionService:
    @staticmethod
    def _process_page_task(page_num: int, page_bytes: bytes, thumbnail_path: Optional[str], vector_store, doc_name: str) -> Tuple[bool, int, Optional[str]]:
        """
        개별 페이지를 파싱하고 벡터 스토어에 저장하는 작업 단위 함수입니다.
        """
        try:
            # 1. 사전 검사 (Pre-check): 빈 페이지 또는 의미 없는 페이지 건너뛰기
            with fitz.open("pdf", page_bytes) as doc:
                page = doc[0]
                text = page.get_text()
                images = page.get_images()
                
                if len(text.strip()) < 50 and not images:
                    return False, page_num, "SKIPPED: 내용 부족 (텍스트 < 50자, 이미지 없음)"

            # 2. 멀티모달 파싱
            parsed_content = parse_page_multimodal(page_bytes, doc_name=doc_name, page_num=page_num)

            if parsed_content and thumbnail_path:
                # 3. 벡터 스토어에 적재
                add_page_content_to_vector_db(parsed_content, page_num, thumbnail_path, vector_store)
                return True, page_num, None
            else:
                return False, page_num, "파싱 실패 또는 썸네일 없음"
        except Exception as e:
            return False, page_num, str(e)

    def run_ingestion_pipeline(self, file_path: Path, workers: int = 50, callback=None) -> dict:
        """
        전체 인제스트 파이프라인을 실행합니다.
        
        Args:
            file_path: PDF 파일 경로
            workers: 병렬 작업자 수
            callback: 진행 상황을 보고할 콜백 함수 (선택 사항)
            
        Returns:
            결과 리포트 딕셔너리
        """
        doc_name = file_path.stem
        pages = load_pdf_as_documents(str(file_path))
        if not pages:
            raise ValueError("PDF 파일을 로드할 수 없습니다.")

        # 1. 썸네일 생성
        original_pdf_doc = fitz.open(file_path)
        thumbnail_paths = create_thumbnails(original_pdf_doc, doc_name)
        
        # 2. 벡터 스토어 준비
        vector_store = get_vector_store()
        initial_count = vector_store._collection.count()

        success_count = 0
        fail_count = 0
        skip_count = 0

        # 3. 병렬 처리
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_page = {}
            for i, _ in enumerate(pages):
                page_num = i + 1
                try:
                    # 페이지 바이트 추출
                    writer = fitz.open()
                    writer.insert_pdf(original_pdf_doc, from_page=i, to_page=i)
                    page_bytes = writer.write()
                    writer.close()

                    page_thumbnail_path = next((p for p in thumbnail_paths if f"page_{page_num:03d}" in p), None)

                    # 작업 제출
                    future = executor.submit(
                        self._process_page_task, 
                        page_num, 
                        page_bytes, 
                        page_thumbnail_path, 
                        vector_store, 
                        doc_name
                    )
                    future_to_page[future] = page_num
                except Exception as e:
                    fail_count += 1

            original_pdf_doc.close()

            # 결과 처리
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    is_success, p_num, error_msg = future.result()
                    if is_success:
                        success_count += 1
                    elif error_msg and error_msg.startswith("SKIPPED"):
                        skip_count += 1
                    else:
                        fail_count += 1
                    
                    if callback:
                        callback(p_num, is_success, error_msg)
                except Exception:
                    fail_count += 1

        # 4. 검색 인덱스 갱신 (BM25)
        get_retriever(force_update=True)

        final_count = vector_store._collection.count()
        return {
            "success": success_count,
            "skip": skip_count,
            "fail": fail_count,
            "added": final_count - initial_count,
            "total": final_count
        }
