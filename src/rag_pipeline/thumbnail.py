import fitz  # PyMuPDF
import os
from typing import List

def create_thumbnails(document: fitz.Document, doc_name: str, base_output_dir: str = "assets/images") -> List[str]:
    """
    PDF 문서의 각 페이지를 이미지(PNG)로 렌더링하여 문서별 폴더에 저장하고, 
    생성된 파일 경로 리스트를 반환합니다.

    Args:
        document (fitz.Document): PDF 문서의 fitz.Document 객체
        doc_name (str): 출력 폴더명 및 파일명에 사용할 문서 이름 (예: 'my_document')
        base_output_dir (str): 이미지를 저장할 최상위 디렉토리 경로

    Returns:
        List[str]: 생성된 썸네일 이미지 파일의 경로 리스트
    """
    # 문서 이름을 기반으로 하위 디렉토리 경로를 생성합니다.
    output_dir = os.path.join(base_output_dir, doc_name)
    os.makedirs(output_dir, exist_ok=True)
    
    thumbnail_paths = []
    for page_num in range(len(document)):
        page_num_actual = page_num + 1
        output_path = os.path.join(output_dir, f"page_{page_num_actual:03d}.png")
        
        # 이미 파일이 존재하는지 확인
        if os.path.exists(output_path):
            # 파일이 존재하면 생성을 건너뛰고 경로만 추가
            thumbnail_paths.append(output_path)
            continue

        page = document.load_page(page_num)
        # 페이지를 이미지로 렌더링합니다.
        pix = page.get_pixmap()
        # 이미지를 파일로 저장합니다.
        pix.save(output_path)
        thumbnail_paths.append(output_path)
    return thumbnail_paths
