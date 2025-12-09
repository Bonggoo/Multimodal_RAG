import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from typing import List
from src.parsing.parser import PageContent

# 상수 정의
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "manual_rag"

def get_google_embedding_function() -> embedding_functions.GoogleGenerativeAiEmbeddingFunction:
    """
    Google GenAI 임베딩 함수를 생성하고 반환합니다.
    
    .env 파일에서 GOOGLE_API_KEY를 로드하여 사용합니다.

    Returns:
        embedding_functions.GoogleGenerativeAiEmbeddingFunction: 설정된 임베딩 함수 객체.

    Raises:
        ValueError: GOOGLE_API_KEY가 없는 경우.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY가 환경 변수에 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    return embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)


def get_chroma_collection(
    collection_name: str = COLLECTION_NAME,
    db_path: str = CHROMA_DB_PATH
) -> chromadb.Collection:
    """
    Persistent ChromaDB 클라이언트를 초기화하고 특정 컬렉션을 가져오거나 생성합니다.

    Args:
        collection_name (str): 가져올 컬렉션의 이름.
        db_path (str): 데이터베이스 파일 경로.

    Returns:
        chromadb.Collection: ChromaDB 컬렉션 객체.
    """
    # 1. Persistent 클라이언트 생성
    persistent_client = chromadb.PersistentClient(path=db_path)
    
    # 2. Google GenAI 임베딩 함수 가져오기
    google_ef = get_google_embedding_function()
    
    # 3. 컬렉션 가져오기 또는 생성하기
    # 임베딩 함수는 컬렉션 생성 시에만 필요합니다.
    collection = persistent_client.get_or_create_collection(
        name=collection_name,
        embedding_function=google_ef
    )
    
    return collection

def add_page_content_to_db(
    page_content: PageContent,
    page_number: int,
    image_path: str,
    collection: chromadb.Collection
):
    """
    파싱된 페이지 콘텐츠를 ChromaDB에 적재합니다.

    텍스트, 테이블, 이미지 설명을 각각 별도의 Document로 저장합니다.

    Args:
        page_content (PageContent): 파싱된 페이지 콘텐츠 Pydantic 모델.
        page_number (int): 현재 페이지 번호.
        image_path (str): 해당 페이지의 썸네일 이미지 경로.
        collection (chromadb.Collection): 데이터를 적재할 ChromaDB 컬렉션.
    """
    documents: List[str] = []
    metadatas: List[dict] = []
    ids: List[str] = []
    
    # 1. 텍스트 콘텐츠 추가
    if page_content.text:
        documents.append(page_content.text)
        metadatas.append({
            "page_number": page_number,
            "content_type": "text",
            "chapter_path": page_content.chapter_path,
            "image_path": image_path,
        })
        ids.append(f"p{page_number}_text_0")

    # 2. 테이블 콘텐츠 추가
    for i, table in enumerate(page_content.tables):
        documents.append(table)
        metadatas.append({
            "page_number": page_number,
            "content_type": "table",
            "chapter_path": page_content.chapter_path,
            "image_path": image_path,
        })
        ids.append(f"p{page_number}_table_{i}")

    # 3. 이미지 설명 콘텐츠 추가
    for i, image in enumerate(page_content.images):
        documents.append(image.description)
        metadatas.append({
            "page_number": page_number,
            "content_type": "image_description",
            "chapter_path": page_content.chapter_path,
            "image_path": image_path,
            "image_caption": image.caption
        })
        ids.append(f"p{page_number}_image_{i}")

    # 4. DB에 데이터 적재
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

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
