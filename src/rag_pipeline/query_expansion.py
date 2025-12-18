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
        
        # 프롬프트 정의: 질문을 분석하여 검색에 최적화된 키워드 나열
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 기술 매뉴얼(QD77MS 등) 검색 최적화 전문가입니다.\n" 
                       "사용자의 질문을 바탕으로, 검색 엔진(Vector DB + BM25)이 최적의 결과를 찾을 수 있도록 쿼리를 확장하세요.\n" 
                       "질문의 핵심 키워드, 동의어, 관련 기술 용어, 영어 약어 등을 포함하여 공백으로 구분된 하나의 문자열로 출력하세요.\n" 
                       "불필요한 설명 없이 확장된 쿼리 문자열만 출력합니다.\n\n" 
                       "예시:\n" 
                       "질문: 원점 복귀 방식 종류\n" 
                       "확장 쿼리: 원점 복귀 방식 OPR method 기계 원점 복귀 근점 도그식 카운트식 데이터 세트식 스토퍼식\n"),
            ("human", "{query}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.cache = {}

    def expand(self, query: str) -> str:
        """
        사용자 쿼리를 확장하여 반환합니다. (캐싱 적용)
        """
        # 1. 캐시 확인
        if query in self.cache:
            print(f"Query expansion cache hit for: '{query}'")
            return self.cache[query]

        # 2. 캐시 미스 시, LLM 호출
        print(f"Query expansion cache miss for: '{query}'. Calling LLM...")
        expansion_start_time = time.time()
        
        expanded_query = self.chain.invoke({"query": query})
        
        expansion_time = time.time() - expansion_start_time
        print(f"LLM call for query expansion took: {expansion_time:.4f}s")

        # 3. 결과 캐싱
        self.cache[query] = expanded_query
        
        return expanded_query
