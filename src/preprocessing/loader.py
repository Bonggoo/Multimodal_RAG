import fitz  # PyMuPDF
from typing import Optional, List

def load_pdf(file_path: str) -> Optional[fitz.Document]:
    """
    PDF 파일을 로드하여 fitz.Document 객체를 반환합니다.

    Args:
        file_path (str): 로드할 PDF 파일의 경로

    Returns:
        Optional[fitz.Document]: 성공 시 fitz.Document 객체, 실패 시 None
    """
    try:
        document = fitz.open(file_path)
        return document
    except FileNotFoundError:
        print(f"오류: 파일 '{file_path}'를 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"PDF를 로드하는 중 오류가 발생했습니다: {e}")
        return None

def split_pdf_to_pages(document: fitz.Document) -> List[bytes]:
    """
    PDF 문서를 페이지별로 분리하여 각 페이지를 개별 PDF 파일(bytes)의 리스트로 반환합니다.

    Args:
        document (fitz.Document): 분할할 PDF의 fitz.Document 객체

    Returns:
        List[bytes]: 각 페이지가 담긴 PDF 파일(bytes)의 리스트
    """
    page_bytes_list = []
    for page_num in range(len(document)):
        # 새로운 빈 PDF 문서를 생성합니다.
        new_doc = fitz.open()
        # 현재 페이지만 새로운 문서에 삽입합니다.
        new_doc.insert_pdf(document, from_page=page_num, to_page=page_num)
        # PDF를 바이트로 저장합니다.
        pdf_bytes = new_doc.write()
        page_bytes_list.append(pdf_bytes)
        new_doc.close()
    return page_bytes_list
