"""
메인 CLI 애플리케이션 파일입니다.
Typer를 사용하여 문서 업로드(ingest)와 질문(qa) 기능을 제공합니다.
"""
import typer
import uvicorn
from pathlib import Path
from tqdm import tqdm
import fitz # PyMuPDF for page byte extraction
import concurrent.futures

# 각 모듈에서 필요한 함수들을 임포트합니다.
from src.rag_pipeline.loader import load_pdf_as_documents
from src.rag_pipeline.thumbnail import create_thumbnails
from src.rag_pipeline.parser import parse_page_multimodal
from src.rag_pipeline.vector_db import get_vector_store, add_page_content_to_vector_db
from src.api.services import get_indexed_documents
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.generator import generate_answer_with_rag

# Typer 앱 생성
app = typer.Typer(help="Multimodal RAG CLI 애플리케이션")

def process_page_task(page_num, page_bytes, thumbnail_path, vector_store, doc_name):
    """
    개별 페이지를 파싱하고 벡터 스토어에 저장하는 작업 단위 함수입니다.
    스레드 풀에서 실행됩니다.
    """
    try:
        # 1. 사전 검사 (Pre-check): 빈 페이지 또는 의미 없는 페이지 건너뛰기
        # fitz는 스레드 안전하지 않을 수 있으므로, 여기서 바이트로부터 새로운 문서를 엽니다.
        with fitz.open("pdf", page_bytes) as doc:
            page = doc[0]
            text = page.get_text()
            images = page.get_images()
            
            # 조건: 텍스트가 50자 미만이고 이미지가 없는 경우 스킵
            # (이 조건은 문서의 특성에 따라 조절 가능)
            if len(text.strip()) < 50 and not images:
                return False, page_num, "SKIPPED: 내용 부족 (텍스트 < 50자, 이미지 없음)"

        # 2. 멀티모달 파싱 (API 호출 - 병목 구간 또는 로컬 JSON 로드)
        parsed_content = parse_page_multimodal(page_bytes, doc_name=doc_name, page_num=page_num)

        if parsed_content and thumbnail_path:
            # 벡터 스토어에 적재
            # ChromaDB add_documents는 스레드 안전하지 않을 수 있으므로 주의가 필요하나, 
            # 일반적인 사용에서는 락이 걸리거나 순차 처리됨. 
            # 만약 문제가 생기면 Lock을 사용해야 함. 여기서는 일단 진행.
            add_page_content_to_vector_db(parsed_content, page_num, thumbnail_path, vector_store)
            return True, page_num, None
        else:
            return False, page_num, "파싱 실패 또는 썸네일 없음"
    except Exception as e:
        return False, page_num, str(e)

@app.command(name="ingest", help="PDF 문서를 데이터베이스에 업로드하고 처리합니다.")
def ingest_pdf(
    file_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="처리할 PDF 파일의 경로"),
    workers: int = typer.Option(50, help="동시 처리를 위한 작업자 스레드 수 (기본값: 50)")
):
    """
    PDF 파일을 받아 전처리, 파싱, 데이터베이스 적재까지의 전체 파이프라인을 실행합니다.
    병렬 처리를 통해 속도를 개선했습니다.
    """
    typer.echo(f"'{file_path.name}' 파일 처리를 시작합니다... (Workers: {workers})")
    
    # 중복 체크
    doc_name = file_path.stem
    indexed_docs = get_indexed_documents()
    existing_doc = next((d for d in indexed_docs if d["filename"] == doc_name), None)
    
    if existing_doc:
        overwrite = typer.confirm(f"⚠️  이미 '{doc_name}' 문서가 인덱싱되어 있습니다. 다시 인제스트 하시겠습니까? (기존 데이터가 중복될 수 있습니다)", default=False)
        if not overwrite:
            typer.echo("작업을 취소합니다.")
            raise typer.Exit()

    try:
        # 1. PDF 로드 (LangChain Document 객체 리스트로)
        doc_name = file_path.stem
        pages = load_pdf_as_documents(str(file_path)) # 각 Document는 한 페이지를 의미
        if not pages:
            typer.secho("PDF 파일을 로드할 수 없습니다.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        
        typer.echo(f"PDF 로드 완료. 총 {len(pages)} 페이지.")

        # 2. 썸네일 생성 (원본 PDF 문서 필요)
        original_pdf_doc = fitz.open(file_path)
        thumbnail_paths = create_thumbnails(original_pdf_doc, doc_name)
        # original_pdf_doc is kept open for byte extraction loop
        
        typer.echo(f"썸네일 {len(thumbnail_paths)}개 생성 완료.")

        # 3. Chroma 벡터 스토어 가져오기
        vector_store = get_vector_store()
        initial_count = vector_store._collection.count()
        typer.echo(f"Chroma 벡터 스토어 준비 완료. (현재 데이터: {initial_count}개)")

        # 4. 페이지별 파싱 및 적재 (병렬 처리)
        typer.echo("페이지별 파싱 및 벡터 스토어 적재를 시작합니다 (병렬 처리)...")
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        # 스레드 풀 실행자 생성
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_page = {}
            
            # 작업 제출 루프
            # PDF 바이트 추출은 메모리 내에서 빠르게 수행되므로 메인 스레드에서 순차적으로 처리하여 안전성 확보
            for i, page_doc in enumerate(pages):
                page_num = i + 1
                
                try:
                    # 원본 PDF 문서에서 페이지 바이트 추출
                    writer = fitz.open()
                    writer.insert_pdf(original_pdf_doc, from_page=i, to_page=i)
                    page_bytes = writer.write()
                    writer.close()

                    # 해당 페이지의 썸네일 경로 찾기
                    page_thumbnail_path = next((p for p in thumbnail_paths if f"page_{page_num:03d}" in p), None)

                    # 작업 제출
                    future = executor.submit(process_page_task, page_num, page_bytes, page_thumbnail_path, vector_store, doc_name)
                    future_to_page[future] = page_num
                
                except Exception as e:
                    tqdm.write(f"페이지 바이트 추출 오류 ({page_num}페이지): {e}")
                    fail_count += 1

            original_pdf_doc.close() # 바이트 추출 완료 후 닫기

            # 결과 처리 루프 (tqdm 연동)
            with tqdm(total=len(future_to_page), desc="문서 처리 중", unit="page") as pbar:
                for future in concurrent.futures.as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        is_success, p_num, error_msg = future.result()
                        if is_success:
                            success_count += 1
                        elif error_msg and error_msg.startswith("SKIPPED"):
                            skip_count += 1
                            # tqdm.write(f"스킵 ({p_num}페이지): {error_msg}")
                        else:
                            fail_count += 1
                            # tqdm.write(f"실패 ({p_num}페이지): {error_msg}")
                    except Exception as e:
                        fail_count += 1
                        tqdm.write(f"작업 처리 중 예외 발생 ({page_num}페이지): {e}")
                    finally:
                        pbar.update(1)

        typer.secho(f"\n'{file_path.name}' 파일 처리가 완료되었습니다.", fg=typer.colors.GREEN)
        typer.echo(f"성공: {success_count} 페이지, 스킵: {skip_count} 페이지, 실패: {fail_count} 페이지")
        
        final_count = vector_store._collection.count()
        added_count = final_count - initial_count
        typer.echo(f"이번 작업으로 {added_count}개 데이터 추가 완료. 현재 총 데이터: {final_count}개")

        # 5. 검색 인덱스 갱신 (BM25)
        typer.echo("검색 인덱스(BM25)를 갱신합니다...")
        get_retriever(force_update=True)
        typer.echo("검색 인덱스 갱신 완료.")

    except Exception as e:
        typer.secho(f"오류 발생: {e}", fg=typer.colors.RED)
        if 'original_pdf_doc' in locals() and original_pdf_doc.doc: # Check if open
             # fitz doc object doesn't have .closed attribute easily accessible/reliable in all versions, 
             # usually close() is idempotent or check validity.
             # Here we just try closing if error happened before explicit close
             try: original_pdf_doc.close() 
             except: pass
        raise typer.Exit(code=1)


@app.command(name="qa", help="업로드된 문서에 대해 질문합니다.")
def ask_question(
    query: str = typer.Argument(..., help="문서에 대해 질문할 내용")
):
    """
    사용자 질문을 받아 검색 및 답변 생성 파이프라인을 실행합니다.
    """
    typer.echo(f"질문: '{query}'")
    
    try:
        # 1. Retriever 가져오기
        typer.echo("Retriever를 준비 중입니다...")
        retriever = get_retriever()
        typer.echo("Retriever 준비 완료. 답변을 생성합니다...")
        
        # 2. Query Expander 준비
        from src.rag_pipeline.query_expansion import QueryExpander
        from src.config import settings
        query_expander = QueryExpander(model_name=settings.GEMINI_MODEL)
        
        # 3. RAG 체인을 사용하여 답변 생성
        result = generate_answer_with_rag(query, retriever, query_expander)
        answer = result["answer"]
        image_paths = result["image_paths"]
        
        # 3. 결과 출력
        typer.echo("\n---")
        typer.secho("답변:", fg=typer.colors.BRIGHT_GREEN)
        typer.echo(answer)
        
        if image_paths:
            typer.secho("\n관련 이미지:", fg=typer.colors.CYAN)
            for path in image_paths:
                typer.echo(f"- {path}")
        typer.echo("---\n")

    except Exception as e:
        typer.secho(f"질문 처리 중 오류 발생: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command(name="serve", help="FastAPI 서버를 실행합니다.")
def serve_api(
    host: str = typer.Option("0.0.0.0", help="서버 호스트"),
    port: int = typer.Option(8000, help="서버 포트"),
    reload: bool = typer.Option(True, help="코드 변경 시 자동 재시작 (개발 모드)")
):
    """
    Multimodal RAG API 서버를 실행합니다.
    """
    typer.echo(f"API 서버를 시작합니다... http://{host}:{port}")
    uvicorn.run("src.api.main:app", host=host, port=port, reload=reload, reload_dirs=["src"])


if __name__ == "__main__":
    app()
