import fitz  # PyMuPDF
import os
from typing import List

def create_thumbnails(document: fitz.Document, doc_name: str, output_dir: str = "assets/images") -> List[str]:
    """
    PDF 문서의 각 페이지를 이미지(PNG)로 렌더링하여 저장하고, 생성된 파일 경로 리스트를 반환합니다.

    Args:
        document (fitz.Document): PDF 문서의 fitz.Document 객체
        doc_name (str): 출력 파일명에 사용할 문서 이름 (예: 'my_document')
        output_dir (str): 이미지를 저장할 디렉토리 경로

    Returns:
        List[str]: 생성된 썸네일 이미지 파일의 경로 리스트
    """
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_paths = []
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        # 페이지를 이미지로 렌더링합니다.
        pix = page.get_pixmap()
        output_path = os.path.join(output_dir, f"{doc_name}_p{page_num+1:03d}.png")
        # 이미지를 파일로 저장합니다.
        pix.save(output_path)
        thumbnail_paths.append(output_path)
    return thumbnail_paths
