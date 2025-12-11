import os
import pickle
from pathlib import Path
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

BM25_INDEX_PATH = Path("data/bm25_index.pkl")

def get_retriever(
    collection_name: str = "manual_rag",
    db_path: str = "chroma_db",
    search_kwargs: Dict[str, Any] = {"k": 20},
    ensemble_weights: List[float] = [0.5, 0.5],
    force_update: bool = False
) -> BaseRetriever:
    """
    LangChain Chroma 벡터 스토어와 BM25를 결합한 EnsembleRetriever를 반환합니다.
    BM25 인덱스는 로컬 파일에 캐싱하여 성능을 최적화합니다.

    Args:
        collection_name (str): 사용할 컬렉션의 이름.
        db_path (str): 데이터베이스 파일 경로.
        search_kwargs (Dict[str, Any]): 검색에 전달할 추가 인자 (예: k=Top-K).
        ensemble_weights (List[float]): [BM25 가중치, Vector 가중치]. 기본값은 [0.5, 0.5].
        force_update (bool): True일 경우 BM25 인덱스를 강제로 재생성하고 저장합니다.

    Returns:
        BaseRetriever: 초기화된 LangChain 검색기 객체 (EnsembleRetriever).
    """
    vector_store = get_vector_store(collection_name=collection_name, db_path=db_path)
    
    # Vector Retriever 초기화
    vector_retriever = vector_store.as_retriever(
        search_kwargs=search_kwargs
    )

    bm25_retriever = None

    # 1. 캐시된 BM25 인덱스 로드 시도
    if not force_update and BM25_INDEX_PATH.exists():
        try:
            with open(BM25_INDEX_PATH, "rb") as f:
                bm25_retriever = pickle.load(f)
            # k 값 업데이트 (저장된 k 값과 다를 수 있으므로)
            bm25_retriever.k = search_kwargs.get("k", 20)
        except Exception as e:
            print(f"BM25 인덱스 로드 실패 (재생성 진행): {e}")

    # 2. 인덱스가 없거나 강제 업데이트인 경우 재생성
    if bm25_retriever is None:
        # 모든 문서 가져오기
        collection_data = vector_store.get()
        texts = collection_data.get("documents", [])
        metadatas = collection_data.get("metadatas", [])
        
        # 문서가 없으면 Vector Retriever만 반환
        if not texts:
            return vector_retriever

        # LangChain Document 객체 리스트로 변환
        documents = []
        for text, metadata in zip(texts, metadatas):
            documents.append(Document(page_content=text, metadata=metadata))

        # BM25 Retriever 초기화
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = search_kwargs.get("k", 20)
        
        # 인덱스 저장
        try:
            BM25_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(BM25_INDEX_PATH, "wb") as f:
                pickle.dump(bm25_retriever, f)
            print(f"BM25 인덱스가 '{BM25_INDEX_PATH}'에 저장되었습니다.")
        except Exception as e:
            print(f"BM25 인덱스 저장 실패: {e}")

    # Ensemble Retriever 생성
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=ensemble_weights
    )

    return ensemble_retriever
