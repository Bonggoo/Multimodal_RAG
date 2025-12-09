from typing import List, Dict, Any
from src.parsing.client import get_gemini_client

def generate_answer(query: str, search_results: Dict[str, List[Any]]) -> str:
    """
    검색된 문서(context)와 사용자 질문을 바탕으로 Gemini를 사용하여 답변을 생성합니다.
    관련된 이미지가 있는 경우, 답변에 이미지 경로를 포함합니다.

    Args:
        query (str): 사용자 질문.
        search_results (Dict[str, List[Any]]): `search_documents`로부터의 검색 결과.

    Returns:
        str: 생성된 답변.
    """
    if not search_results or not search_results.get('documents') or not search_results['documents'][0]:
        return "죄송합니다, 관련 정보를 찾을 수 없습니다."

    try:
        # 1. 컨텍스트와 이미지 경로 구성
        context_parts = []
        image_paths = set()
        
        # search_results['documents']는 이중 리스트 [[]] 형태일 수 있으므로 확인
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]

        for doc, meta in zip(documents, metadatas):
            context_parts.append(doc)
            if meta.get('image_path'):
                image_paths.add(meta['image_path'])
        
        context_str = "\n---\n".join(context_parts)

        # 2. LLM 프롬프트 구성
        prompt = f"""
        당신은 주어진 컨텍스트 정보를 바탕으로 사용자의 질문에 답변하는 유용한 AI 어시스턴트입니다.

        **컨텍스트:**
        {context_str}

        **질문:**
        {query}

        **답변:**
        """

        # 3. Gemini API 호출
        model = get_gemini_client()
        response = model.generate_content(prompt)
        
        answer = response.text

        # 4. 답변에 이미지 경로 추가
        if image_paths:
            answer += "\n\n**관련 이미지:**\n" + "\n".join(f"- {path}" for path in sorted(list(image_paths)))

        return answer

    except Exception as e:
        print(f"답변 생성 중 오류 발생: {e}")
        return "답변을 생성하는 중에 오류가 발생했습니다."
