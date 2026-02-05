import fitz  # PyMuPDF
import os
from typing import List

def create_thumbnails(document: fitz.Document, doc_name: str, uid: str = "default", base_output_dir: str = "assets/images") -> List[str]:
    """
    PDF 문서 페이지의 썸네일을 유저별 격리 폴더에 저장합니다.
    """
    # UID와 문서 이름을 기반으로 디렉토리 생성
    output_dir = os.path.join(base_output_dir, uid, doc_name)
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
