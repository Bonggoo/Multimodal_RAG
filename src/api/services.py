import os
import shutil
from typing import List, Dict, Any

from src.rag_pipeline.vector_db import get_vector_store
from src.rag_pipeline.retriever import get_retriever

def get_indexed_documents(uid: str = "default") -> List[Dict[str, Any]]:
    """
    특정 유저의 벡터 스토어에 인덱싱된 모든 문서의 목록을 반환합니다.
    """
    vector_store = get_vector_store(uid=uid)
    results = vector_store.get(include=["metadatas"])
    
    metadatas = results.get("metadatas", [])
    if not metadatas:
        return []

    # doc_name을 키로 하고, title을 값으로 하는 딕셔너리 생성 (중복 제거)
    docs_map = {}
    for metadata in metadatas:
        doc_name = metadata.get("doc_name")
        title = metadata.get("title")
        if doc_name:
            # 이미 있는 문서라도 타이틀이 없으면(또는 빈 문자열이면) 현재 타이틀로 업데이트 (있는 경우 우선)
            if doc_name not in docs_map or (not docs_map[doc_name] and title):
                docs_map[doc_name] = title

    # DocumentInfo 형태의 딕셔너리 리스트로 변환
    document_list = [
        {"filename": doc_name, "title": title} 
        for doc_name, title in docs_map.items()
    ]
    
    return sorted(document_list, key=lambda x: x["filename"])

def delete_document(uid: str, doc_name: str, app_state: Any) -> Dict[str, Any]:
    """
    지정된 유저의 문서 데이터를 삭제합니다.
    """
    # 1. ChromaDB에서 데이터 삭제
    vector_store = get_vector_store(uid=uid)
    collection = vector_store._collection
    
    # 삭제 전 문서 개수 확인
    initial_count = collection.count()
    existing_docs = collection.get(where={"doc_name": doc_name})
    if not existing_docs or not existing_docs.get("ids"):
        raise ValueError(f"'{doc_name}' 문서를 찾을 수 없습니다.")
        
    collection.delete(where={"doc_name": doc_name})
    deleted_count = initial_count - collection.count()

    # 2. 썸네일 에셋 디렉토리 삭제 (UID 자동 반영)
    thumbnail_dir = os.path.join("assets/images", uid, doc_name)
    if os.path.isdir(thumbnail_dir):
        shutil.rmtree(thumbnail_dir)
        thumbnail_deleted = True
    else:
        thumbnail_deleted = False

    # 3. 검색 인덱스 및 메모리 리트리버 갱신
    get_retriever(uid=uid, force_update=True)
    # app_state 업데이트는 멀티유저 환경에서는 유저별 캐시가 필요할 수 있으나,
    # 현재는 요청 시점에 get_retriever를 호출하는 방식으로 전환하거나 app_state를 유저별 dict로 관리해야 함.
    if hasattr(app_state, 'retrievers'):
        app_state.retrievers[uid] = get_retriever(uid=uid, force_update=False)

    return {
        "message": f"'{doc_name}' 문서가 성공적으로 삭제되었습니다.",
        "deleted_db_entries": deleted_count,
        "thumbnail_deleted": thumbnail_deleted
    }
