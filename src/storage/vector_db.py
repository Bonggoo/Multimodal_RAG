import os
from dotenv import load_dotenv
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.parsing.schema import PageContent # Corrected import path

# 상수 정의
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "manual_rag"

def get_vector_store(
    collection_name: str = COLLECTION_NAME,
    db_path: str = CHROMA_DB_PATH
) -> Chroma:
    """
    LangChain Chroma 벡터 스토어를 초기화하고 반환합니다.
    Google Generative AI 임베딩 함수를 사용합니다.

    Args:
        collection_name (str): 가져올 컬렉션의 이름.
        db_path (str): 데이터베이스 파일 경로.

    Returns:
        Chroma: 초기화된 LangChain Chroma 벡터 스토어 객체.

    Raises:
        ValueError: GOOGLE_API_KEY가 없는 경우.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY가 환경 변수에 설정되지 않았습니다. .env 파일을 확인하세요.")

    # Google Generative AI 임베딩 함수 초기화
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)

    # Chroma 벡터 스토어 초기화 (없으면 생성)
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=db_path
    )
    return vector_store


def add_page_content_to_vector_db(
    page_content: PageContent,
    page_number: int,
    image_path: str,
    vector_db: Chroma
):
    """
    파싱된 페이지 콘텐츠를 LangChain Document 객체로 변환하여 Chroma 벡터 스토어에 적재합니다.

    텍스트, 테이블, 이미지 설명을 각각 별도의 Document로 저장합니다.
    Keywords와 Summary를 메타데이터에 포함합니다.

    Args:
        page_content (PageContent): 파싱된 페이지 콘텐츠 Pydantic 모델.
        page_number (int): 현재 페이지 번호.
        image_path (str): 해당 페이지의 썸네일 이미지 경로.
        vector_db (Chroma): 데이터를 적재할 LangChain Chroma 벡터 스토어.
    """
    documents_to_add: List[Document] = []
    
    # 키워드 리스트를 콤마로 구분된 문자열로 변환
    keywords_str = ", ".join(page_content.keywords) if page_content.keywords else ""

    base_metadata = {
        "page_number": page_number,
        "chapter_path": page_content.chapter_path,
        "image_path": image_path,
        "keywords": keywords_str,
        "summary": page_content.summary or ""
    }

    # 1. 텍스트 콘텐츠 추가
    if page_content.text:
        text_metadata = {**base_metadata, "content_type": "text"}
        documents_to_add.append(
            Document(page_content=page_content.text, metadata=text_metadata)
        )

    # 2. 테이블 콘텐츠 추가
    for i, table in enumerate(page_content.tables):
        table_metadata = {**base_metadata, "content_type": "table", "table_index": i}
        documents_to_add.append(
            Document(page_content=table, metadata=table_metadata)
        )

    # 3. 이미지 설명 콘텐츠 추가
    for i, image in enumerate(page_content.images):
        image_metadata = {
            **base_metadata,
            "content_type": "image_description",
            "image_index": i,
            "image_caption": image.caption
        }
        documents_to_add.append(
            Document(page_content=image.description, metadata=image_metadata)
        )

    # 4. 벡터 스토어에 데이터 적재
    if documents_to_add:
        vector_db.add_documents(documents_to_add)



if __name__ == '__main__':
    try:
        # ChromaDB 컬렉션 가져오기 테스트
        manual_rag_collection = get_chroma_collection()
        print(f"성공적으로 '{manual_rag_collection.name}' 컬렉션을 가져왔습니다.")
        print(f"현재 컬렉션에 {manual_rag_collection.count()}개의 아이템이 있습니다.")
        # 새로운 아이템 추가 예시
        # manual_rag_collection.add(
        #     documents=["This is a test document", "This is another test document"],
        #     metadatas=[{"source": "test"}, {"source": "test"}],
        #     ids=["id1", "id2"]
        # )
        # print(f"테스트 아이템 추가 후: {manual_rag_collection.count()}개")

    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"ChromaDB 초기화 중 오류 발생: {e}")
