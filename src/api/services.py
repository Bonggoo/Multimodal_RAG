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
    # 성능 최적화: 모든 청크를 가져오지 않고, 각 문서의 1페이지에 해당하는 청크의 메타데이터만 가져옵니다.
    # 대규모 문서군에서 로딩 속도를 비약적으로 향상시킵니다.
    results = vector_store.get(where={"page": 1}, include=["metadatas"])
    
    metadatas = results.get("metadatas", [])
    if not metadatas:
        return []

    # doc_name을 키로 하고, (title, is_active)를 값으로 하는 딕셔너리 생성 (중복 제거)
    docs_map = {}
    for metadata in metadatas:
        doc_name = metadata.get("doc_name")
        title = metadata.get("title")
        is_active = metadata.get("is_active", True)
        if doc_name:
            if doc_name not in docs_map:
                docs_map[doc_name] = {"title": title, "is_active": is_active}
            else:
                if not docs_map[doc_name]["title"] and title:
                    docs_map[doc_name]["title"] = title

    # DocumentInfo 형태의 딕셔너리 리스트로 변환
    document_list = [
        {"filename": doc_name, "title": info["title"], "is_active": info["is_active"]} 
        for doc_name, info in docs_map.items()
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

def toggle_document_active_status(uid: str, doc_name: str, is_active: bool) -> Dict[str, Any]:
    """
    지정된 문서의 모든 페이지 메타데이터에서 is_active 상태를 업데이트합니다.
    """
    vector_store = get_vector_store(uid=uid)
    collection = vector_store._collection
    
    # 해당 문서의 모든 ID와 기존 메타데이터 가져오기 (limit 해제하여 전체 청크 대상)
    results = collection.get(where={"doc_name": doc_name}, include=["metadatas"], limit=10000)
    ids = results.get("ids", [])
    metadatas = results.get("metadatas", [])
    
    if not ids:
        raise ValueError(f"'{doc_name}' 문서를 찾을 수 없습니다.")
        
    # 메타데이터 업데이트
    new_metadatas = []
    for meta in metadatas:
        new_meta = meta.copy()
        new_meta["is_active"] = is_active
        new_metadatas.append(new_meta)
        
    collection.update(ids=ids, metadatas=new_metadatas)
    
    # 성능 최적화: 인덱스 전체를 다시 빌드하는 대신, 검색 시점에 필터링하도록 변경
    # get_retriever(uid=uid, force_update=True)  <- 너무 느려서 주석 처리/삭제
    
    # 만약 app_state가 있다면 해당 유저의 리트리버도 갱신
    # (FastAPI app.state를 통해 전달받는 경우를 대비)
    # 실제 endpoint(routes.py)에서 app_state를 넘겨주는지 확인 필요
    
    return {
        "status": "success",
        "message": f"'{doc_name}' 문서가 {'활성화' if is_active else '비활성화'} 되었습니다.",
        "is_active": is_active
    }
