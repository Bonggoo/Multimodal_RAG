import re 
import os
import time
from typing import List, Dict, Any, AsyncIterator

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

from src.rag_pipeline.query_expansion import QueryExpander
from src.config import settings

def format_docs(docs: List[Any]) -> str:
    """
    검색된 문서들을 단일 문자열 컨텍스트로 포맷합니다.
    각 문서의 내용 앞에 출처 이미지 경로를 명시합니다.
    """
    formatted_docs = []
    for doc in docs:
        image_path = doc.metadata.get('image_path', 'N/A')
        content = f"[Image Source: {image_path}]\n{doc.page_content}"
        formatted_docs.append(content)
    return "\n\n".join(formatted_docs)

def get_image_paths(docs: List[Any]) -> List[str]:
    """
    검색된 문서들에서 고유한 이미지 경로를 추출합니다.
    (Legacy: format_docs와 LLM 인용 방식으로 대체되면서 사용 빈도 줄어듦)
    """
    image_paths = set()
    for doc in docs:
        if doc.metadata.get('image_path'):
            image_paths.add(doc.metadata['image_path'])
    return sorted(list(image_paths))


def get_rag_chain(retriever: BaseRetriever) -> Any: # Returns a Runnable object
    """
    LangChain Expression Language (LCEL)을 사용하여 RAG 체인을 생성합니다.
    주의: 이 함수는 단순 체인 구성용이며, Query Expansion이 적용된 로직은 generate_answer_with_rag에서 처리합니다.

    Args:
        retriever (BaseRetriever): 문서 검색을 위한 검색기 객체.

    Returns:
        Runnable: 구성된 RAG 체인.
    """
    template = """
    당신은 주어진 컨텍스트 정보를 바탕으로 사용자의 질문에 답변하는 유용한 AI 어시스턴트입니다.
    
    **컨텍스트:**
    {context}

    **질문:**
    {question}

    **답변:**
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
    )
    
    rag_chain = (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

def generate_answer_with_rag(query: str, retriever: BaseRetriever, query_expander: QueryExpander) -> Dict[str, Any]:
    """
    RAG 체인을 사용하여 사용자 질문에 답변을 생성하고,
    답변에 실제 인용된 이미지 경로만 추출하여 반환합니다.

    Args:
        query (str): 사용자 질문.
        retriever (BaseRetriever): 문서 검색을 위한 검색기 객체.
        query_expander (QueryExpander): 쿼리 확장을 위한 객체.

    Returns:
        Dict[str, Any]: 생성된 답변, 인용된 이미지 경로 리스트, 확장된 쿼리.
    """
    # 1. 쿼리 확장 (Query Expansion)
    expanded_query = query_expander.expand(query)
    
    # 2. 확장된 쿼리로 문서 검색
    docs = retriever.invoke(expanded_query)
    context_text = format_docs(docs)

    # 3. 답변 생성 (원본 질문 + 검색된 컨텍스트)
    # 프롬프트: 답변 마지막에 인용된 이미지 소스를 리스트업 하도록 지시
    template = """
    당신은 주어진 컨텍스트 정보를 바탕으로 사용자의 질문에 답변하는 유용한 AI 어시스턴트입니다.
    답변은 한국어로 작성하며, 기술적인 내용은 정확하게 전달해야 합니다.
    컨텍스트에 없는 내용은 지어내지 말고 모른다고 답변하세요.

    각 컨텍스트 블록은 `[Image Source: ...]`로 시작합니다.
    답변을 작성할 때 참고한 컨텍스트가 있다면, 해당 컨텍스트의 `Image Source` 경로를 기억해두세요.
    
    답변의 맨 마지막에, 답변 작성에 실제로 참고한 모든 `Image Source` 경로를 다음 형식으로 나열해 주세요:
    [[Cited Images: 경로1, 경로2, ...]]

    만약 참고한 이미지가 없다면 `[[Cited Images: None]]`이라고 출력하세요.

    **컨텍스트:**
    {context}

    **질문:**
    {question}

    **답변:**
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
    )
    
    chain = prompt | llm | StrOutputParser()
    
    full_response = chain.invoke({"context": context_text, "question": query})
    
    # 4. 답변과 이미지 경로 분리 (Regex Parsing)
    # 예상 포맷: ... 답변 내용 ... [[Cited Images: path/to/img1.png, path/to/img2.png]]
    cited_images = []
    final_answer = full_response

    match = re.search(r"\[\[Cited Images: (.*?)\]\]", full_response, re.DOTALL)
    if match:
        images_str = match.group(1)
        if images_str.lower() != "none":
            # 쉼표로 구분된 경로 추출 및 공백 제거
            cited_images = [img.strip() for img in images_str.split(',')]
        
        # 답변 텍스트에서 메타데이터 태그 제거 (깔끔하게 보여주기 위해)
        final_answer = full_response.replace(match.group(0), "").strip()
    else:
        cited_images = []

    return {
        "answer": final_answer, 
        "image_paths": cited_images, 
        "expanded_query": expanded_query
    }

async def generate_answer_with_rag_streaming(query: str, retriever: BaseRetriever, query_expander: QueryExpander) -> AsyncIterator[Dict[str, Any]]:
    """
    RAG 체인을 사용하여 사용자 질문에 대한 답변을 스트리밍하고,
    마지막에 인용된 이미지 경로를 반환합니다. (성능 로깅 포함)
    """
    print("\n--- RAG Streaming Pipeline Benchmark ---")
    total_start_time = time.time()

    # 1. 쿼리 확장 (Query Expansion)
    expansion_start_time = time.time()
    expanded_query = query_expander.expand(query)
    expansion_time = time.time() - expansion_start_time
    print(f"[1] Query Expansion Time: {expansion_time:.4f}s")

    # 2. 확장된 쿼리로 문서 검색
    retrieval_start_time = time.time()
    docs = retriever.invoke(expanded_query)
    retrieval_time = time.time() - retrieval_start_time
    print(f"[2] Document Retrieval Time: {retrieval_time:.4f}s")

    # 3. 컨텍스트 포맷팅
    format_start_time = time.time()
    context_text = format_docs(docs)
    format_time = time.time() - format_start_time
    print(f"[3] Context Formatting Time: {format_time:.4f}s")
    
    # 4. 답변 생성 (LLM 스트리밍)
    template = """
    당신은 주어진 컨텍스트 정보를 바탕으로 사용자의 질문에 답변하는 유용한 AI 어시스턴트입니다.
    답변은 한국어로 작성하며, 기술적인 내용은 정확하게 전달해야 합니다.
    컨텍스트에 없는 내용은 지어내지 말고 모른다고 답변하세요.

    각 컨텍스트 블록은 `[Image Source: ...]`로 시작합니다.
    답변을 작성할 때 참고한 컨텍스트가 있다면, 해당 컨텍스트의 `Image Source` 경로를 기억해두세요.
    
    답변의 맨 마지막에, 답변 작성에 실제로 참고한 모든 `Image Source` 경로를 다음 형식으로 나열해 주세요:
    [[Cited Images: 경로1, 경로2, ...]]

    만약 참고한 이미지가 없다면 `[[Cited Images: None]]`이라고 출력하세요.

    **컨텍스트:**
    {context}

    **질문:**
    {question}

    **답변:**
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
    )
    
    chain = prompt | llm | StrOutputParser()
    
    full_response = ""
    llm_start_time = time.time()
    # astream을 사용하여 비동기 스트리밍
    async for chunk in chain.astream({"context": context_text, "question": query}):
        full_response += chunk
        yield {"type": "token", "payload": chunk}
    llm_time = time.time() - llm_start_time
    print(f"[4] LLM Stream Generation Time: {llm_time:.4f}s")


    # 5. 답변과 이미지 경로 분리 (Regex Parsing)
    parsing_start_time = time.time()
    cited_images = []
    final_answer = full_response

    match = re.search(r"\[\[Cited Images: (.*?)\]\]", full_response, re.DOTALL)
    if match:
        images_str = match.group(1)
        if images_str.lower() != "none":
            cited_images = [img.strip() for img in images_str.split(',')]
        
        final_answer = full_response.replace(match.group(0), "").strip()
    parsing_time = time.time() - parsing_start_time
    print(f"[5] Metadata Parsing Time: {parsing_time:.4f}s")
    
    # 메타데이터를 마지막에 전송
    yield {
        "type": "metadata",
        "payload": {
            "image_paths": cited_images,
            "expanded_query": expanded_query,
            "final_answer": final_answer,
        },
    }
    yield {"type": "end", "payload": "Stream ended"}
    
    total_time = time.time() - total_start_time
    print(f"--- Total RAG Pipeline Time: {total_time:.4f}s ---")