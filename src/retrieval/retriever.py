from typing import List, Dict, Optional, Any
import chromadb
from src.storage.vector_db import get_chroma_collection

def search_documents(
    query: str,
    n_results: int = 5,
    where_filter: Optional[Dict[str, Any]] = None,
    collection: Optional[chromadb.Collection] = None,
) -> Optional[Dict[str, List[Any]]]:
    """
    사용자 질문을 임베딩하여 ChromaDB에서 유사 문서를 검색합니다.

    Args:
        query (str): 사용자 검색어.
        n_results (int): 반환할 결과의 수 (Top-K).
        where_filter (Optional[Dict[str, Any]]): 메타데이터 필터.
        collection (Optional[chromadb.Collection]): 사용할 ChromaDB 컬렉션. 
                                                  제공되지 않으면 새로 가져옵니다.

    Returns:
        Optional[Dict[str, List[Any]]]: ChromaDB의 검색 결과. 
                                        오류 발생 시 None을 반환합니다.
    """
    try:
        if collection is None:
            collection = get_chroma_collection()

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else {}
        )
        return results

    except Exception as e:
        print(f"문서 검색 중 오류 발생: {e}")
        return None

if __name__ == '__main__':
    # 이 모듈을 직접 실행하여 테스트하는 예시
    # DB에 데이터가 있어야 유의미한 결과를 얻을 수 있습니다.
    test_query = "test" 
    print(f"'{test_query}'에 대한 검색 테스트:")
    
    # 먼저, 테스트를 위해 DB에 데이터 추가
    try:
        test_collection = get_chroma_collection()
        if test_collection.count() == 0:
            print("테스트를 위해 DB에 샘플 데이터를 추가합니다.")
            test_collection.add(
                documents=["This is a test document about cats.", "This is a test document about dogs."],
                metadatas=[{"source": "cat_test"}, {"source": "dog_test"}],
                ids=["cat_id1", "dog_id1"]
            )
    
        # 1. 기본 검색
        search_results = search_documents(query="animal", n_results=1, collection=test_collection)
        print("\n[기본 검색 결과]")
        if search_results and search_results['documents']:
             print(search_results['documents'][0])
        else:
            print("결과 없음")

        # 2. 필터 사용 검색
        filtered_search_results = search_documents(
            query="animal",
            n_results=1,
            where_filter={"source": "dog_test"},
            collection=test_collection
        )
        print("\n[필터 적용 검색 결과 ('source'='dog_test')]")
        if filtered_search_results and filtered_search_results['documents']:
            print(filtered_search_results['documents'][0])
        else:
            print("결과 없음")

    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")
