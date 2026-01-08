import os
import pickle
from pathlib import Path
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from src.config import settings
from src.rag_pipeline.vector_db import get_vector_store

try:
    from langchain.retrievers import EnsembleRetriever  # type: ignore
except ImportError:
    try:
        from langchain_classic.retrievers import EnsembleRetriever
    except ImportError:
         # Fallback or re-raise if strictly needed, or try another location
         raise ImportError("EnsembleRetriever could not be imported from langchain.retrievers or langchain_classic.retrievers")

# --- BM25 한국어 토크나이저 설정 (전역) ---
# 이 함수는 pickle로 저장 및 로드해야 하므로, 전역 레벨에 정의되어야 합니다.
try:
    from konlpy.tag import Okt
    from tqdm import tqdm

    print("konlpy.tag.Okt 로드 성공. BM25에 한국어 토크나이저를 적용합니다.")
    okt_tokenizer = Okt()
    
    def korean_tokenizer(text: str) -> List[str]:
        """Okt를 사용한 전역 한국어 토크나이저"""
        return okt_tokenizer.morphs(text)
    
    BM25_PREPROCESS_FUNC = korean_tokenizer

except ImportError:
    print("WARNING: konlpy가 설치되지 않았습니다. 기본 토크나이저(공백 기준)로 BM25를 초기화합니다. 한국어 검색 성능이 저하될 수 있습니다.")
    from tqdm import tqdm # tqdm은 konlpy와 무관하게 사용 가능
    # 기본 토크나이저 함수
    def default_tokenizer(text: str) -> List[str]:
        return text.split()
    
    BM25_PREPROCESS_FUNC = default_tokenizer
# --- 끝 ---

BM25_INDEX_PATH = Path(settings.BM25_INDEX_PATH)

def get_retriever(
    collection_name: str = settings.COLLECTION_NAME,
    db_path: str = settings.CHROMA_DB_DIR,
    search_kwargs: Dict[str, Any] = {"k": 40},
    ensemble_weights: List[float] = [0.5, 0.5],
    force_update: bool = False
) -> BaseRetriever:
    """
    LangChain Chroma 벡터 스토어와 BM25를 결합한 EnsembleRetriever를 반환합니다.
    BM25 인덱스는 로컬 파일에 캐싱하며, 문서 ID 집합을 비교하여 불필요한 재생성을 방지합니다.
    """
    vector_store = get_vector_store(collection_name=collection_name, db_path=db_path)
    
    # Vector Retriever 초기화
    vector_retriever = vector_store.as_retriever(
        search_kwargs=search_kwargs
    )

    bm25_retriever = None

    # 1. 캐시된 BM25 인덱스 로드 시도 (force_update가 아닐 때)
    if not force_update and BM25_INDEX_PATH.exists():
        try:
            with open(BM25_INDEX_PATH, "rb") as f:
                bm25_retriever = pickle.load(f)
            bm25_retriever.k = search_kwargs.get("k", 20)
        except Exception as e:
            print(f"BM25 인덱스 로드 실패 (재생성 진행): {e}")

    # 2. 인덱스가 없거나 강제 업데이트인 경우 재생성 로직
    if bm25_retriever is None:
        print("BM25 인덱스 재/생성 절차를 시작합니다.")
        
        # 모든 문서 가져오기 (Source of Truth)
        collection_data = vector_store.get(include=["metadatas", "documents"])
        ids = collection_data.get("ids", [])
        texts = collection_data.get("documents", [])
        metadatas = collection_data.get("metadatas", [])
        
        # 문서가 없으면 Vector Retriever만 반환
        if not texts:
            return vector_retriever

        # (최적화) 기존 인덱스가 있고, 문서 ID 집합이 동일하면 재생성 스킵
        if BM25_INDEX_PATH.exists():
            try:
                with open(BM25_INDEX_PATH, "rb") as f:
                    cached_retriever = pickle.load(f)
                
                # 'doc_id'가 메타데이터에 있는지 확인하고 ID 집합 생성
                cached_ids = {doc.metadata['doc_id'] for doc in cached_retriever.docs if 'doc_id' in doc.metadata}
                current_ids = set(ids)
                
                if cached_ids == current_ids:
                    print(f"BM25 인덱스가 이미 최신 상태입니다. ({len(current_ids)}개 문서) 생성을 건너뜁니다.")
                    bm25_retriever = cached_retriever
                    bm25_retriever.k = search_kwargs.get("k", 20)
                else:
                    print("문서 변경이 감지되어 BM25 인덱스를 재생성합니다.")
            except Exception as e:
                print(f"캐시된 BM25 인덱스 비교 중 오류 발생 (재생성 진행): {e}")

    # 3. 최종적으로 BM25 리트리버가 없으면 생성
    if bm25_retriever is None:
        # LangChain Document 객체 리스트로 변환 (doc_id를 메타데이터에 포함)
        documents = [
            Document(page_content=texts[i], metadata={**metadatas[i], "doc_id": ids[i]}) 
            for i in range(len(ids))
        ]

        print(f"BM25 인덱스 생성을 시작합니다 ({len(documents)}개 문서)...")
        
        # BM25 Retriever 초기화 (전역 토크나이저 사용)
        bm25_retriever = BM25Retriever.from_documents(
            documents=tqdm(documents, desc="BM25 인덱싱"),
            preprocess_func=BM25_PREPROCESS_FUNC
        )
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
