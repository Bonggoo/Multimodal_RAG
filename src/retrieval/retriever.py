from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from src.storage.vector_db import get_vector_store

try:
    from langchain.retrievers import EnsembleRetriever
except ImportError:
    try:
        from langchain_classic.retrievers import EnsembleRetriever
    except ImportError:
         # Fallback or re-raise if strictly needed, or try another location
         raise ImportError("EnsembleRetriever could not be imported from langchain.retrievers or langchain_classic.retrievers")

def get_retriever(
    collection_name: str = "manual_rag",
    db_path: str = "chroma_db",
    search_kwargs: Dict[str, Any] = {"k": 20},
    ensemble_weights: List[float] = [0.5, 0.5]
) -> BaseRetriever:
    """
    LangChain Chroma 벡터 스토어와 BM25를 결합한 EnsembleRetriever를 반환합니다.

    Args:
        collection_name (str): 사용할 컬렉션의 이름.
        db_path (str): 데이터베이스 파일 경로.
        search_kwargs (Dict[str, Any]): 검색에 전달할 추가 인자 (예: k=Top-K).
        ensemble_weights (List[float]): [BM25 가중치, Vector 가중치]. 기본값은 [0.5, 0.5].

    Returns:
        BaseRetriever: 초기화된 LangChain 검색기 객체 (EnsembleRetriever).
    """
    vector_store = get_vector_store(collection_name=collection_name, db_path=db_path)
    
    # Vector Retriever 초기화
    vector_retriever = vector_store.as_retriever(
        search_kwargs=search_kwargs
    )

    # 모든 문서 가져오기 (BM25 구성을 위해)
    # get() 메서드는 dict를 반환함: {'ids': [], 'embeddings': [], 'metadatas': [], 'documents': []}
    collection_data = vector_store.get()
    
    texts = collection_data.get("documents", [])
    metadatas = collection_data.get("metadatas", [])
    
    # 문서가 없으면 Vector Retriever만 반환 (BM25 초기화 실패 방지)
    if not texts:
        return vector_retriever

    # LangChain Document 객체 리스트로 변환
    documents = []
    for text, metadata in zip(texts, metadatas):
        documents.append(Document(page_content=text, metadata=metadata))

    # BM25 Retriever 초기화
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = search_kwargs.get("k", 20)  # Vector search와 동일한 k 설정

    # Ensemble Retriever 생성
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=ensemble_weights
    )

    return ensemble_retriever
