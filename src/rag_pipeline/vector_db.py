import os
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.rag_pipeline.schema import PageContent
from src.config import settings

# Chroma 클라이언트 및 임베딩 함수를 전역으로 캐싱하여 중복 로드를 방지합니다.
_vector_store = None
_embedding_function = None

def get_embedding_function():
    """Google Generative AI 임베딩 함수를 반환합니다. (캐싱 사용)"""
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
        )
    return _embedding_function

def get_vector_store(
    collection_name: str = settings.COLLECTION_NAME, 
    db_path: str = settings.CHROMA_DB_DIR
) -> Chroma:
    """Chroma 벡터 스토어 클라이언트를 반환합니다. (캐싱 사용)"""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name=collection_name,
            persist_directory=db_path,
            embedding_function=get_embedding_function()
        )
    return _vector_store

def create_documents_from_page_content(page_content: PageContent, page_num: int, thumbnail_path: str) -> List[Document]:
    """
    파싱된 PageContent 객체를 기반으로 LangChain Document 객체 리스트를 생성합니다.
    의미 기반 청킹(semantic chunking) 로직과 메타데이터 보강이 포함되어 있습니다.
    """
    documents = []
    
    # 공통 메타데이터: keywords와 summary를 page_content에서 직접 가져옵니다.
    # ChromaDB 호환성을 위해 리스트는 문자열로 변환합니다.
    base_metadata = {
        "page": page_num,
        "image_path": thumbnail_path,
        "doc_name": os.path.basename(os.path.dirname(thumbnail_path)), # 올바른 문서 이름 추출
        "chapter_path": page_content.chapter_path,
        "keywords": ", ".join(page_content.keywords) if page_content.keywords else "",
        "summary": page_content.summary if page_content.summary else "",
    }

    # 1. 텍스트 콘텐츠 추가
    if page_content.text and len(page_content.text.strip()) > 10:
        documents.append(Document(
            page_content=page_content.text,
            metadata={**base_metadata, "chunk_type": "text"}
        ))

    # 2. 테이블(Tables) 처리
    for i, table_str in enumerate(page_content.tables):
        documents.append(Document(
            page_content=table_str,
            metadata={**base_metadata, "chunk_type": "table", "table_index": i}
        ))
            
    # 3. 이미지 설명 처리
    for i, image in enumerate(page_content.images):
        if image.description:
            documents.append(Document(
                page_content=image.description,
                metadata={
                    **base_metadata, 
                    "chunk_type": "image_description", 
                    "image_index": i,
                    "image_caption": image.caption
                }
            ))

    return documents


def add_page_content_to_vector_db(page_content: PageContent, page_num: int, thumbnail_path: str, vector_store: Chroma):
    """
    파싱된 PageContent를 Document 리스트로 변환하고, 각 Document에 고유 ID를 부여하여 벡터 스토어에 추가합니다.
    """
    documents = create_documents_from_page_content(page_content, page_num, thumbnail_path)
    
    if not documents:
        return

    # 문서 이름은 이미 메타데이터에 있으므로 첫 번째 문서에서 가져옵니다.
    doc_name = documents[0].metadata.get("doc_name", "unknown_doc")
    ids = [f"{doc_name}_p{page_num}_chunk_{i}" for i in range(len(documents))]

    # 각 문서의 메타데이터에 'doc_id' 추가
    for i, doc in enumerate(documents):
        doc.metadata["doc_id"] = ids[i]

    vector_store.add_documents(documents=documents, ids=ids)