import os
import shutil
from typing import List, Dict, Any

from src.rag_pipeline.vector_db import get_vector_store
from src.rag_pipeline.retriever import get_retriever

def get_indexed_documents() -> List[str]:
    """
    현재 벡터 스토어에 인덱싱된 모든 문서의 고유한 이름 목록을 반환합니다.
    """
    vector_store = get_vector_store()
    results = vector_store.get(include=["metadatas"])
    
    metadatas = results.get("metadatas", [])
    if not metadatas:
        return []

    doc_names = {metadata.get("doc_name") for metadata in metadatas if metadata.get("doc_name")}
    
    return sorted(list(doc_names))

def delete_document(doc_name: str, app_state: Any) -> Dict[str, Any]:
    """
    지정된 문서 이름과 관련된 모든 데이터를 삭제합니다.
    (ChromaDB, 썸네일 파일, 검색 인덱스)
    """
    # 1. ChromaDB에서 데이터 삭제
    vector_store = get_vector_store()
    collection = vector_store._collection
    
    # 삭제 전 문서 개수 확인
    initial_count = collection.count()
    existing_docs = collection.get(where={"doc_name": doc_name})
    if not existing_docs or not existing_docs.get("ids"):
        raise ValueError(f"'{doc_name}' 문서를 찾을 수 없습니다.")
        
    collection.delete(where={"doc_name": doc_name})
    deleted_count = initial_count - collection.count()

    # 2. 썸네일 에셋 디렉토리 삭제
    thumbnail_dir = os.path.join("assets/images", doc_name)
    if os.path.isdir(thumbnail_dir):
        shutil.rmtree(thumbnail_dir)
        thumbnail_deleted = True
    else:
        thumbnail_deleted = False

    # 3. 검색 인덱스 및 메모리 리트리버 갱신
    get_retriever(force_update=True)
    app_state.retriever = get_retriever(force_update=False)

    return {
        "message": f"'{doc_name}' 문서가 성공적으로 삭제되었습니다.",
        "deleted_db_entries": deleted_count,
        "thumbnail_deleted": thumbnail_deleted
    }
