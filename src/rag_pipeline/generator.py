import re 
import os
import time
from typing import List, Dict, Any, AsyncIterator, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

from src.rag_pipeline.query_expansion import QueryExpander
from src.config import settings
from src.rag_pipeline.vector_db import get_vector_store
from src.api.schemas import QAFilters, UserProfile

def extract_page_number(query: str) -> Optional[int]:
    """
    쿼리에서 'XXX페이지' 또는 'p.XXX', 'page XXX' 형식의 페이지 번호를 추출합니다.
    """
    patterns = [
        r'(\d+)\s*페이지',
        r'(\d+)\s*page',
        r'p\.\s*(\d+)',
        r'page\s*(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            try:
                page_num = int(match.group(1))
                # 일반적인 매뉴얼 페이지 범위를 고려 (예: 1~2000)
                if 1 <= page_num <= 3000:
                    return page_num
            except (ValueError, TypeError):
                continue
    return None

def format_docs(docs: List[Any]) -> str:
    """
    검색된 문서들을 단일 문자열 컨텍스트로 포맷합니다.
    각 문서의 내용 앞에 출처(문서명, 페이지, 이미지 경로)를 명시합니다.
    """
    formatted_docs = []
    for doc in docs:
        image_path = doc.metadata.get('image_path', 'N/A')
        doc_name = doc.metadata.get('doc_name', 'N/A')
        page_num = doc.metadata.get('page', 'N/A')
        content = f"[Document: {doc_name}, Page: {page_num}, Image Source: {image_path}]\n{doc.page_content}"
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

def generate_answer_with_rag(query: str, retriever: BaseRetriever, query_expander: QueryExpander, filters: QAFilters = None, history: List[Dict[str, str]] = None, user_profile: UserProfile = None) -> Dict[str, Any]:
    """
    RAG 체인을 사용하여 사용자 질문에 답변을 생성하고,
    답변에 실제 인용된 이미지 경로만 추출하여 반환합니다.

    Args:
        query (str): 사용자 질문.
        retriever (BaseRetriever): 문서 검색을 위한 검색기 객체.
        query_expander (QueryExpander): 쿼리 확장을 위한 객체.
        history (List[Dict[str, str]]): 이전 대화 내역.
        user_profile (UserProfile): 사용자 개인화 프로필 정보.

    Returns:
        Dict[str, Any]: 생성된 답변, 인용된 이미지 경로 리스트, 확장된 쿼리.
    """
    # 1. 쿼리 확장 (Query Expansion)
    expanded_query = query_expander.expand(query)
    
    # 2. 다중 쿼리 기반 문서 검색 (정제된 쿼리 + 확장 쿼리)
    # 정제 로직: 고유 코드(예: E1236)가 있으면 해당 코드에 집중하도록 쿼리 생성
    codes = re.findall(r'[A-Z]\d{3,4}', query.upper())
    refined_query = " ".join(codes) if codes else query
    
    vector_store = get_vector_store()
    
    # 3. 스마트 라우팅: 페이지 번호 추출 및 필터 구성
    page_filter = extract_page_number(query)
    
    search_filter = {}
    if filters and filters.doc_name:
        search_filter["doc_name"] = filters.doc_name
    
    if page_filter:
        print(f"Smart Routing: Detected page filter {page_filter}")
        # ChromaDB $and 조건 구성 (문서명 필터가 있는 경우)
        if "doc_name" in search_filter:
            search_filter = {"$and": [
                {"doc_name": {"$eq": search_filter["doc_name"]}},
                {"page": {"$eq": page_filter}}
            ]}
        else:
            search_filter = {"page": {"$eq": page_filter}}
    
    # 4. 필터가 적용된 검색 수행
    if search_filter:
        print(f"Applying search filters: {search_filter}")
        # 필터가 걸린 경우 k를 조절하거나 해당 페이지의 모든 청크를 가져오도록 함
        filtered_retriever = vector_store.as_retriever(
            search_kwargs={'filter': search_filter, 'k': 50 if page_filter else 100}
        )
        docs_orig = filtered_retriever.invoke(refined_query)
        docs_exp = filtered_retriever.invoke(expanded_query)
        docs_raw = filtered_retriever.invoke(query) if refined_query != query else []
    else:
        docs_orig = retriever.invoke(refined_query)
        docs_exp = retriever.invoke(expanded_query)
        docs_raw = retriever.invoke(query) if refined_query != query else []
    
    # 모든 결과 병합 및 중복 제거
    all_docs = docs_orig + docs_exp + docs_raw
    seen_contents = set()
    docs = []
    for doc in all_docs:
        if doc.page_content not in seen_contents:
            docs.append(doc)
            seen_contents.add(doc.page_content)
    
    # [추가] 상위 5개 페이지에 대해 자동으로 다음 페이지 컨텍스트 추가 (가로 펼침 표/연속 정보 대응)
    extended_docs = []
    processed_pages = set()
    
    # 상위 결과들 우선 유지
    for doc in docs[:10]:
        extended_docs.append(doc)
        doc_name = doc.metadata.get("doc_name")
        page_num = doc.metadata.get("page")
        if doc_name and page_num:
            processed_pages.add(f"{doc_name}_{page_num}")
            
            # 다음 페이지 후보군 탐색 (간단한 필터링 사용)
            next_page_num = page_num + 1
            if f"{doc_name}_{next_page_num}" not in processed_pages:
                try:
                    # 벡터 스토어에서 해당 페이지 직접 조회
                    next_page_docs = vector_store.get(
                        where={"$and": [{"doc_name": {"$eq": doc_name}}, {"page": {"$eq": int(next_page_num)}}]}
                    )
                    if next_page_docs and next_page_docs.get("documents"):
                        from langchain_core.documents import Document
                        for i, content in enumerate(next_page_docs["documents"]):
                            # Document 객체 재구성
                            new_doc = Document(
                                page_content=content,
                                metadata=next_page_docs["metadatas"][i]
                            )
                            if new_doc.page_content not in seen_contents:
                                extended_docs.append(new_doc)
                                seen_contents.add(new_doc.page_content)
                        processed_pages.add(f"{doc_name}_{next_page_num}")
                except Exception as e:
                    print(f"Error fetching next page context: {e}")

    # 나머지 중복되지 않은 문서들 추가
    for doc in docs[10:]:
        if doc.page_content not in seen_contents:
            extended_docs.append(doc)
            seen_contents.add(doc.page_content)
    
    docs = extended_docs
    
    # 최대 검색 결과 수 제한 (속도와 정확도의 균형을 위해 100개로 설정)
    docs = docs[:100]
    context_text = format_docs(docs)

    # 3. 답변 생성 (원본 질문 + 검색된 컨텍스트 + 대화 내역 + 사용자 프로필)
    # 프롬프트: 답변 마지막에 인용된 이미지 소스를 리스트업 하도록 지시
    history_text = ""
    if history:
        history_text = "\n".join([f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in history])

    profile_text = "제공된 프로필 정보가 없습니다."
    if user_profile:
        parts = []
        if user_profile.name: parts.append(f"이름: {user_profile.name}")
        if user_profile.role: parts.append(f"역할/직업: {user_profile.role}")
        if user_profile.interests: parts.append(f"관심분야: {', '.join(user_profile.interests)}")
        if user_profile.custom_instructions: parts.append(f"추가 요청사항: {user_profile.custom_instructions}")
        profile_text = "\n".join(parts)

    template = """
    당신은 사용자의 목표를 돕는 강력한 개인화 AI 비서입니다.
    현재 대화 중인 사용자에 대한 정보는 다음과 같습니다. 

    **사용자 프로필:**
    {user_profile}

    **작동 지침:**
    1. **자연스러운 대화**: 답변마다 유저의 이름을 부르거나 똑같은 인삿말을 반복하지 마세요. 이미 인사를 나눴다면 본론부터 답하세요.
    2. **암묵적 개인화**: 프로필 정보는 답변의 스타일을 결정하는 참고용으로만 사용하고 직접 언급하지 마세요.
    3. **정확한 정보 제공**: 제공된 컨텍스트를 최우선으로 참고하여 핵심 내용을 답변하세요.
    4. **문맥 유지**: 이전 대화 내역에 맞춰 자연스럽게 대화를 이어가세요.
    5. **출처 명시**: 문서 기반 답변 시 마지막에 [[Cited Images: 경로]]를 반드시 포함하세요.

    **이전 대화 내역:**
    {chat_history}

    **컨텍스트 (참고 문서):**
    {context}

    **현재 질문:**
    {question}

    **답변:**
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
    )
    
    chain = prompt | llm | StrOutputParser()
    
    full_response = chain.invoke({
        "context": context_text, 
        "question": query,
        "chat_history": history_text,
        "user_profile": profile_text
    })
    
    # 4. 답변과 이미지 경로 분리 (Regex Parsing)
    # 예상 포맷: ... 답변 내용 ... [[Cited Images: path/to/img1.png, path/to/img2.png]]
    cited_images = []
    final_answer = full_response

    match = re.search(r"\[\[Cited Images: (.*?)\]\]", full_response, re.DOTALL)
    if match:
        images_str = match.group(1)
        if images_str.lower() != "none":
            # 쉼표로 구분된 경로 추출, 공백 제거 및 중복 제거
            raw_images = [img.strip() for img in images_str.split(',')]
            cited_images = sorted(list(set(img for img in raw_images if img)))
        
        # 답변 텍스트에서 메타데이터 태그 제거 (깔끔하게 보여주기 위해)
        final_answer = full_response.replace(match.group(0), "").strip()
    else:
        cited_images = []

    return {
        "answer": final_answer, 
        "image_paths": cited_images, 
        "expanded_query": expanded_query
    }

async def generate_answer_with_rag_streaming(query: str, retriever: BaseRetriever, query_expander: QueryExpander, filters: QAFilters = None, history: List[Dict[str, str]] = None, user_profile: UserProfile = None) -> AsyncIterator[Dict[str, Any]]:
    """
    RAG 체인을 사용하여 사용자 질문에 대한 답변을 스트리밍하고,
    마지막에 인용된 이미지 경로를 반환합니다. (성능 로깅 포함)
    """
    print("\n--- RAG Streaming Pipeline Benchmark ---")
    total_start_time = time.time()

    # 1. 쿼리 확장 (Query Expansion)
    expansion_start_time = time.time()
    
    # 대화 내역 포맷팅 (쿼리 확장용)
    history_context = ""
    if history:
        history_context = "\n".join([f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in history[-3:]]) # 최근 3개만 참고
        
    expanded_query = query_expander.expand(query, history_context)
    expansion_time = time.time() - expansion_start_time
    print(f"[1] Query Expansion Time: {expansion_time:.4f}s")

    # 2. 다중 쿼리 기반 문서 검색 (정제된 쿼리 + 확장 쿼리)
    retrieval_start_time = time.time()
    codes = re.findall(r'[A-Z]\d{3,4}', query.upper())
    refined_query = " ".join(codes) if codes else query

    vector_store = get_vector_store()

    # 스마트 라우팅: 페이지 번호 추출 및 필터 구성
    page_filter = extract_page_number(query)
    
    search_filter = {}
    if filters and filters.doc_name:
        search_filter["doc_name"] = filters.doc_name
    
    if page_filter:
        print(f"Smart Routing (Streaming): Detected page filter {page_filter}")
        if "doc_name" in search_filter:
            search_filter = {"$and": [
                {"doc_name": {"$eq": search_filter["doc_name"]}},
                {"page": {"$eq": page_filter}}
            ]}
        else:
            search_filter = {"page": {"$eq": page_filter}}

    if search_filter:
        print(f"Applying search filters (Streaming): {search_filter}")
        filtered_retriever = vector_store.as_retriever(
            search_kwargs={'filter': search_filter, 'k': 50 if page_filter else 100}
        )
        docs_orig = filtered_retriever.invoke(refined_query)
        docs_exp = filtered_retriever.invoke(expanded_query)
        docs_raw = filtered_retriever.invoke(query) if refined_query != query else []
    else:
        docs_orig = retriever.invoke(refined_query)
        docs_exp = retriever.invoke(expanded_query)
        docs_raw = retriever.invoke(query) if refined_query != query else []
    
    # 결과 병합 및 중복 제거
    all_docs = docs_orig + docs_exp + docs_raw
    seen_contents = set()
    docs = []
    for doc in all_docs:
        if doc.page_content not in seen_contents:
            docs.append(doc)
            seen_contents.add(doc.page_content)
    
    # [추가] 상위 5개 페이지에 대해 자동으로 다음 페이지 컨텍스트 추가 (가로 펼침 표/연속 정보 대응)
    extended_docs = []
    processed_pages = set()
    
    # 상위 결과들 우선 유지
    for doc in docs[:10]:
        extended_docs.append(doc)
        doc_name = doc.metadata.get("doc_name")
        page_num = doc.metadata.get("page")
        if doc_name and page_num:
            processed_pages.add(f"{doc_name}_{page_num}")
            
            # 다음 페이지 후보군 탐색
            next_page_num = page_num + 1
            if f"{doc_name}_{next_page_num}" not in processed_pages:
                try:
                    # 벡터 스토어에서 해당 페이지 직접 조회
                    next_page_docs = vector_store.get(
                        where={"$and": [{"doc_name": {"$eq": doc_name}}, {"page": {"$eq": int(next_page_num)}}]}
                    )
                    if next_page_docs and next_page_docs.get("documents"):
                        from langchain_core.documents import Document
                        for i, content in enumerate(next_page_docs["documents"]):
                            new_doc = Document(
                                page_content=content,
                                metadata=next_page_docs["metadatas"][i]
                            )
                            if new_doc.page_content not in seen_contents:
                                extended_docs.append(new_doc)
                                seen_contents.add(new_doc.page_content)
                        processed_pages.add(f"{doc_name}_{next_page_num}")
                except Exception as e:
                    print(f"Error fetching next page context: {e}")

    # 나머지 중복되지 않은 문서들 추가
    for doc in docs[10:]:
        if doc.page_content not in seen_contents:
            extended_docs.append(doc)
            seen_contents.add(doc.page_content)
    
    docs = extended_docs[:100] # 최대 검색 결과 수 제한 (속도와 정확도의 균형을 위해 100개로 설정)
    retrieval_time = time.time() - retrieval_start_time
    print(f"[2] Retrieval Time (including extensions): {retrieval_time:.4f}s")

    # 3. 컨텍스트 포맷팅
    format_start_time = time.time()
    context_text = format_docs(docs)
    format_time = time.time() - format_start_time
    print(f"[3] Context Formatting Time: {format_time:.4f}s")
    
    # 4. 답변 생성 (LLM 스트리밍)
    history_text = ""
    if history:
        # Gemini 2.0의 강력한 컨텍스트 윈도우를 활용하여 전체 내역 전달
        history_text = "\n".join([f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in history])

    profile_text = "제공된 프로필 정보가 없습니다."
    if user_profile:
        parts = []
        if user_profile.name: parts.append(f"이름: {user_profile.name}")
        if user_profile.role: parts.append(f"역할/직업: {user_profile.role}")
        if user_profile.interests: parts.append(f"관심분야: {', '.join(user_profile.interests)}")
        if user_profile.custom_instructions: parts.append(f"추가 요청사항: {user_profile.custom_instructions}")
        profile_text = "\n".join(parts)

    template = """
    당신은 사용자의 목표를 돕는 강력한 개인화 AI 비서입니다.
    현재 대화 중인 사용자에 대한 정보는 다음과 같습니다. 

    **사용자 프로필:**
    {user_profile}

    **작동 지침:**
    1. **자연스러운 대화**: 답변마다 유저의 이름을 부르거나 똑같은 인삿말을 반복하지 마세요. 이미 인사를 나눴다면 본론부터 답하세요.
    2. **암묵적 개인화**: 프로필 정보는 답변의 스타일을 결정하는 참고용으로만 사용하고 직접 언급하지 마세요. (예: 개발자에게는 기술적으로 설명하되 그 이유를 설명 문구에 넣지 마세요.)
    3. **정확한 정보 제공**: 제공된 컨텍스트를 최우선으로 참고하여 핵심 내용을 답변하세요.
    4. **문맥 유지**: 이전 대화 내역에 맞춰 자연스럽게 대화를 이어가세요.
    5. **출처 명시**: 문서 기반 답변 시 마지막에 [[Cited Images: 경로]]를 반드시 포함하세요.

    **이전 대화 내역:**
    {chat_history}

    **컨텍스트 (참고 문서):**
    {context}

    **현재 질문:**
    {question}

    **답변:**
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
    )
    
    chain = prompt | llm | StrOutputParser()
    
    full_response = ""
    llm_start_time = time.time()
    # astream을 사용하여 비동기 스트리밍
    async for chunk in chain.astream({
        "context": context_text, 
        "question": query,
        "chat_history": history_text,
        "user_profile": profile_text
    }):
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
            # 쉼표로 구분된 경로 추출, 공백 제거 및 중복 제거
            raw_images = [img.strip() for img in images_str.split(',')]
            cited_images = sorted(list(set(img for img in raw_images if img)))
        
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

def generate_session_title(query: str, answer: str) -> str:
    """
    사용자의 첫 번째 질문과 AI의 답변을 기반으로 짧고 명확한 채팅 제목을 생성합니다.
    """
    print(f"[Titling] Generating title for query: {query[:50]}...")
    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0.7,
            google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
        )
        
        prompt = (
            "당신은 채팅방 주제 요약 전문가입니다. "
            "사용자의 질문과 AI의 답변을 보고, 이 대화의 주제를 가장 잘 나타내는 짧은 제목(10자 이내)을 하나만 지어주세요. "
            "추가 설명이나 따옴표, 마침표 없이 제목만 출력하세요.\n\n"
            f"유저 질문: {query}\n"
            f"AI 답변: {answer[:200]}...\n\n"
            "채팅방 제목:"
        )
        
        response = llm.invoke(prompt)
        title = response.content.strip()
        
        # 특수문자 및 불필요한 장식 제거
        title = re.sub(r'["\'“”.,!]', '', title)
        title = title.replace("채팅방 제목:", "").strip()
        
        print(f"[Titling] Generated title: {title}")
        return title if title else "새로운 채팅"
    except Exception as e:
        print(f"[Titling] Error generating session title: {e}")
        return "새로운 채팅"