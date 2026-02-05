from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os
import time
from dotenv import load_dotenv

class QueryExpander:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             raise ValueError("GOOGLE_API_KEY가 환경 변수에 설정되지 않았습니다.")
             
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, google_api_key=api_key)
        
        # 프롬프트 정의: 대화 내역과 질문을 분석하여 독립적인 검색 쿼리 생성
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 산업용 장비 및 기술 매뉴얼 검색 최적화 전문가입니다.\n" 
                       "사용자의 대화 내역과 현재 질문을 분석하여, 검색 엔진이 정확한 정보를 찾을 수 있도록 독립적인(standalone) 검색 키워드를 생성하세요.\n\n"
                       "지침:\n"
                       "1. 현재 질문이 '그건 왜 그래?', '더 자세히 설명해줘'와 같이 앞선 대화에 의존적인 경우, 대화 내역을 바탕으로 지시대명사(그것, 저것 등)가 무엇을 의미하는지 파악하여 검색어로 변환하세요.\n"
                       "2. 한국어 기술 용어의 매칭을 위해 '조치 방법', '해결 방법' 등 동의어를 포함하세요.\n"
                       "3. 에러 코드나 파라미터 번호가 포함된 경우 반드시 포함하세요.\n"
                       "4. 불필요한 수식어를 빼고 명사 위주의 검색 최적화 쿼리를 만드세요.\n\n" 
                       "예시:\n" 
                       "대화 내역: User: E1236 알람이 뭐야? Assistant: ...입니다.\n"
                       "현재 질문: 그거 어떻게 조치해?\n"
                       "확장 쿼리: E1236 알람 조치 방법 처치 해결 방법"),
            ("human", "대화 내역: {history}\n\n현재 질문: {query}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.cache = {}

    def expand(self, query: str, history: str = "") -> str:
        """
        사용자 쿼리를 대화 내역을 바탕으로 확장하여 반환합니다.
        """
        cache_key = f"{history[:100]}_{query}" # 간단한 캐시 키
        if cache_key in self.cache:
            return self.cache[cache_key]

        expansion_start_time = time.time()
        expanded_query = self.chain.invoke({"query": query, "history": history})
        
        expansion_time = time.time() - expansion_start_time
        print(f"Query expansion with history took: {expansion_time:.4f}s")

        self.cache[cache_key] = expanded_query
        return expanded_query
