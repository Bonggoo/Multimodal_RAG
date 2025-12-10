"""
메인 CLI 애플리케이션 파일입니다.
Typer를 사용하여 문서 업로드(ingest)와 질문(qa) 기능을 제공합니다.
"""
import typer
from pathlib import Path
from tqdm import tqdm
import fitz # PyMuPDF for page byte extraction

# 각 모듈에서 필요한 함수들을 임포트합니다.
from src.preprocessing.loader import load_pdf_as_documents
from src.preprocessing.thumbnail import create_thumbnails
from src.parsing.parser import parse_page_multimodal
from src.storage.vector_db import get_vector_store, add_page_content_to_vector_db
from src.retrieval.retriever import get_retriever
from src.retrieval.generator import generate_answer_with_rag

# Typer 앱 생성
app = typer.Typer(help="Multimodal RAG CLI 애플리케이션")

@app.command(name="ingest", help="PDF 문서를 데이터베이스에 업로드하고 처리합니다.")
def ingest_pdf(
    file_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="처리할 PDF 파일의 경로")
):
    """
    PDF 파일을 받아 전처리, 파싱, 데이터베이스 적재까지의 전체 파이프라인을 실행합니다.
    """
    typer.echo(f"'{file_path.name}' 파일 처리를 시작합니다...")
    
    try:
        # 1. PDF 로드 (LangChain Document 객체 리스트로)
        doc_name = file_path.stem
        pages = load_pdf_as_documents(str(file_path)) # 각 Document는 한 페이지를 의미
        if not pages:
            typer.secho("PDF 파일을 로드할 수 없습니다.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        
        typer.echo(f"PDF 로드 완료. 총 {len(pages)} 페이지.")

        # 2. 썸네일 생성 (원본 PDF 문서 필요)
        # PyMuPDFLoader로 로드한 Document 객체는 원본 PDF Document 객체가 아니므로,
        # 썸네일 생성을 위해 다시 fitz로 로드
        original_pdf_doc = fitz.open(file_path)
        thumbnail_paths = create_thumbnails(original_pdf_doc, doc_name)
        original_pdf_doc.close() # 사용 후 닫기
        typer.echo(f"썸네일 {len(thumbnail_paths)}개 생성 완료.")

        # 3. Chroma 벡터 스토어 가져오기
        vector_store = get_vector_store()
        typer.echo(f"Chroma 벡터 스토어 준비 완료.")

        # 4. 페이지별 파싱 및 적재
        typer.echo("페이지별 파싱 및 벡터 스토어 적재를 시작합니다...")
        for i, page_doc in enumerate(tqdm(pages, desc="페이지 처리 중")):
            page_num = i + 1
            
            # LangChain Document에서 페이지 내용 (바이트) 추출
            # PyMuPDFLoader가 `page_content`에 텍스트를 넣으므로, 원본 페이지 바이트를 얻기 위해 fitz 다시 사용
            # 이 부분은 개선의 여지가 있지만, 현재 parse_page_multimodal이 bytes를 받으므로 유지
            # page_doc.metadata에서 'page_number'와 같은 정보를 활용할 수 있습니다.
            
            # 원본 PDF 문서에서 페이지 바이트 추출
            original_pdf_doc_for_bytes = fitz.open(file_path) # 매 페이지마다 다시 여는 것은 비효율적, 추후 개선
            writer = fitz.open()
            writer.insert_pdf(original_pdf_doc_for_bytes, from_page=i, to_page=i)
            page_bytes = writer.write()
            writer.close()
            original_pdf_doc_for_bytes.close()

            # 해당 페이지의 썸네일 경로 찾기
            page_thumbnail_path = next((p for p in thumbnail_paths if f"_p{page_num:03d}" in p), None)

            # 멀티모달 파싱
            typer.echo(f"\n- {page_num}페이지 파싱 시작...")
            parsed_content = parse_page_multimodal(page_bytes)
            typer.echo(f"- {page_num}페이지 파싱 완료.")

            if parsed_content and page_thumbnail_path:
                # 벡터 스토어에 적재
                add_page_content_to_vector_db(parsed_content, page_num, page_thumbnail_path, vector_store)
            else:
                typer.echo(f"경고: {page_num}페이지를 파싱하거나 썸네일 경로를 찾지 못했습니다. 건너뜁니다.")

        typer.secho(f"\n'{file_path.name}' 파일 처리가 성공적으로 완료되었습니다.", fg=typer.colors.GREEN)
        typer.echo(f"총 {vector_store._collection.count()}개의 데이터가 벡터 스토어에 저장되었습니다.")

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
        
        # 2. RAG 체인을 사용하여 답변 생성
        result = generate_answer_with_rag(query, retriever)
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


if __name__ == "__main__":
    app()
