from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

def load_pdf_as_documents(file_path: str) -> List[Document]:
    """
    PDF 파일을 로드하여 LangChain Document 객체의 리스트로 반환합니다.
    각 Document는 PDF의 한 페이지를 나타냅니다.

    Args:
        file_path (str): 로드할 PDF 파일의 경로

    Returns:
        List[Document]: 각 페이지가 담긴 LangChain Document 객체의 리스트
    """
    try:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        return documents
    except Exception as e:
        print(f"PDF를 LangChain Document로 로드하는 중 오류가 발생했습니다: {e}")
        return []
