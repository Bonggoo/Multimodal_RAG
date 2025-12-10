from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from src.storage.vector_db import get_vector_store

def get_retriever(
    collection_name: str = "manual_rag",
    db_path: str = "chroma_db",
    search_kwargs: Dict[str, Any] = {"k": 5}
) -> BaseRetriever:
    """
    LangChain Chroma 벡터 스토어로부터 검색기(retriever)를 초기화하고 반환합니다.

    Args:
        collection_name (str): 사용할 컬렉션의 이름.
        db_path (str): 데이터베이스 파일 경로.
        search_kwargs (Dict[str, Any]): 검색에 전달할 추가 인자 (예: k=Top-K).

    Returns:
        BaseRetriever: 초기화된 LangChain 검색기 객체.
    """
    vector_store = get_vector_store(collection_name=collection_name, db_path=db_path)
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    return retriever
