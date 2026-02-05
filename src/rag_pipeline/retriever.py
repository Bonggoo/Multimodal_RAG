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
_okt = None

def get_okt():
    global _okt
    if _okt is None:
        try:
            from konlpy.tag import Okt
            import jpype
            if not jpype.isJVMStarted():
                # 이미 실행 중인 JVM이 없을 때만 시작 (기본 경로 사용)
                jpype.startJVM(convertStrings=True)
            elif jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()
            
            _okt = Okt()
            print("konlpy.tag.Okt 지연 로드 성공.")
        except Exception as e:
            print(f"Okt 로드 중 오류 발생: {e}. 기본 토크나이징을 사용합니다.")
            return None
    return _okt

def korean_tokenizer(text: str) -> List[str]:
    """Okt를 사용한 전역 한국어 토크나이저 (지연 로드 방식)"""
    okt = get_okt()
    if okt:
        try:
            return okt.morphs(text)
        except Exception as e:
            print(f"Okt 토크나이징 오류: {e}")
            return text.split()
    return text.split()

BM25_PREPROCESS_FUNC = korean_tokenizer
# --- 끝 ---

BM25_INDEX_PATH = Path(settings.BM25_INDEX_PATH)

def get_retriever(
    uid: str = "default",
    collection_name: str = settings.COLLECTION_NAME,
    search_kwargs: Dict[str, Any] = {"k": 40},
    ensemble_weights: List[float] = [0.5, 0.5],
    force_update: bool = False
) -> BaseRetriever:
    """
    유저 UID별 EnsembleRetriever를 반환합니다.
    BM25 인덱스는 {CHROMA_DB_DIR}/{uid}/bm25_index.pkl 에 저장됩니다.
    """
    # 유저별 전용 경로 설정
    db_path = os.path.join(settings.CHROMA_DB_DIR, uid)
    bm25_path = Path(db_path) / "bm25_index.pkl"
    
    vector_store = get_vector_store(uid=uid, collection_name=collection_name, db_path=db_path)
    
    # Vector Retriever 초기화
    vector_retriever = vector_store.as_retriever(
        search_kwargs=search_kwargs
    )

    bm25_retriever = None

    # 1. 캐시된 BM25 인덱스 로드 시도 (force_update가 아닐 때)
    if not force_update and bm25_path.exists():
        try:
            with open(bm25_path, "rb") as f:
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
        if bm25_path.exists():
            try:
                with open(bm25_path, "rb") as f:
                    cached_retriever = pickle.load(f)
                
                # 'doc_id'가 메타데이터에 있는지 확인하고 ID 집합 생성
                cached_ids = {doc.metadata['doc_id'] for doc in cached_retriever.docs if 'doc_id' in doc.metadata}
                current_ids = set(ids)
                
                if cached_ids == current_ids:
                    print(f"BM25 인덱스가 이미 최신 상태입니다. ({len(current_ids)}개 문서) 생성을 건너뜜 (UID: {uid})")
                    bm25_retriever = cached_retriever
                    bm25_retriever.k = search_kwargs.get("k", 20)
                else:
                    print(f"문서 변경이 감지되어 BM25 인덱스를 재생성합니다. (UID: {uid})")
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
            bm25_path.parent.mkdir(parents=True, exist_ok=True)
            with open(bm25_path, "wb") as f:
                pickle.dump(bm25_retriever, f)
            print(f"BM25 인덱스가 '{bm25_path}'에 저장되었습니다.")
        except Exception as e:
            print(f"BM25 인덱스 저장 실패: {e}")

    # Ensemble Retriever 생성
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=ensemble_weights
    )

    return ensemble_retriever
