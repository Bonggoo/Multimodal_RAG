import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def format_docs(docs: List[Any]) -> str:
    """
    검색된 문서들을 단일 문자열 컨텍스트로 포맷합니다.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def get_image_paths(docs: List[Any]) -> List[str]:
    """
    검색된 문서들에서 고유한 이미지 경로를 추출합니다.
    """
    image_paths = set()
    for doc in docs:
        if doc.metadata.get('image_path'):
            image_paths.add(doc.metadata['image_path'])
    return sorted(list(image_paths))


def get_rag_chain(retriever: BaseRetriever) -> Any: # Returns a Runnable object
    """
    LangChain Expression Language (LCEL)을 사용하여 RAG 체인을 생성합니다.

    Args:
        retriever (BaseRetriever): 문서 검색을 위한 검색기 객체.

    Returns:
        Runnable: 구성된 RAG 체인.
    """
    
    # 프롬프트 템플릿
    template = """
    당신은 주어진 컨텍스트 정보를 바탕으로 사용자의 질문에 답변하는 유용한 AI 어시스턴트입니다.

    **컨텍스트:**
    {context}

    **질문:**
    {question}

    **답변:**
    """
    prompt = ChatPromptTemplate.from_template(template)

    # LLM 초기화
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # RAG 체인 구성
    rag_chain = (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def generate_answer_with_rag(query: str, retriever: BaseRetriever) -> Dict[str, Any]:
    """
    RAG 체인을 사용하여 사용자 질문에 답변을 생성하고,
    관련된 이미지 경로를 함께 반환합니다.

    Args:
        query (str): 사용자 질문.
        retriever (BaseRetriever): 문서 검색을 위한 검색기 객체.

    Returns:
        Dict[str, Any]: 생성된 답변과 이미지 경로 리스트를 포함하는 딕셔너리.
    """
    rag_chain = get_rag_chain(retriever)
    
    # 체인을 실행하기 전에 검색된 문서들을 직접 가져와 이미지 경로를 추출합니다.
    docs = retriever.invoke(query)
    image_paths = get_image_paths(docs)

    answer = rag_chain.invoke(query)
    
    return {"answer": answer, "image_paths": image_paths}
