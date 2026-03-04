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
from src.rag_pipeline.ingestion_service import IngestionService
from src.api.services import get_indexed_documents
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.generator import generate_answer_with_rag

# Typer 앱 생성
app = typer.Typer(help="Multimodal RAG CLI 애플리케이션")

@app.command(name="ingest", help="PDF 문서를 데이터베이스에 업로드하고 처리합니다.")
def ingest_pdf(
    file_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="처리할 PDF 파일의 경로"),
    workers: int = typer.Option(50, help="동시 처리를 위한 작업자 스레드 수 (기본값: 50)")
):
    """
    PDF 파일을 받아 전처리, 파싱, 데이터베이스 적재까지의 전체 파이프라인을 실행합니다.
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
        service = IngestionService()
        
        # tqdm 연동을 위한 프로그레스 바 준비
        # 정확한 페이지 수를 알기 위해 로직이 약간 중복되지만, CLI 사용자 경험을 위해 유지
        from src.rag_pipeline.loader import load_pdf_as_documents
        pages = load_pdf_as_documents(str(file_path))
        
        with tqdm(total=len(pages), desc="문서 처리 중", unit="page") as pbar:
            def progress_callback(page_num, is_success, error_msg):
                pbar.update(1)
                if not is_success and error_msg:
                    if not error_msg.startswith("SKIPPED"):
                        tqdm.write(f"⚠️  {page_num}페이지 오류: {error_msg}")

            results = service.run_ingestion_pipeline(
                file_path=file_path,
                workers=workers,
                callback=progress_callback
            )

        typer.secho(f"\n'{file_path.name}' 파일 처리가 완료되었습니다.", fg=typer.colors.GREEN)
        typer.echo(f"성공: {results['success']} 페이지, 스킵: {results['skip']} 페이지, 실패: {results['fail']} 페이지")
        typer.echo(f"이번 작업으로 {results['added']}개 데이터 추가 완료. 현재 총 데이터: {results['total']}개")

    except Exception as e:
        typer.secho(f"오류 발생: {e}", fg=typer.colors.RED)
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
