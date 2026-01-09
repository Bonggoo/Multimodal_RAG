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
            ("system", "당신은 산업용 장비 및 기술 매뉴얼 검색 최적화 전문가입니다.\n" 
                       "사용자의 질문을 분석하여, 검색 엔진(Vector DB + BM25)이 정확한 정보를 찾을 수 있도록 핵심 키워드를 추출하고 확장하세요.\n\n"
                       "지침:\n"
                       "1. 한국어 기술 용어의 매칭을 위해 '조치 방법', '처치 방법', '해결 방법' 등의 동의어를 적극 포함하세요.\n"
                       "2. 에러 코드나 파라미터 번호가 포함된 경우(예: 104, E1234), 해당 코드를 반드시 포함하고 관련 검색어를 생성하세요.\n"
                       "3. 질문의 의도를 파악하여 관련 기술 용어, 동의어, 영어 약어를 추가하세요.\n"
                       "4. 불필요한 수식어나 문장 성분은 제외하고 검색에 도움이 되는 명사 위주로 구성하세요.\n"
                       "5. 결과는 공백으로 구분된 단어들로만 구성된 하나의 문자열이어야 합니다.\n\n" 
                       "예시:\n" 
                       "질문: E1236 알람의 원인과 조치\n" 
                       "확장 쿼리: E1236 알람 에러 원인 조치 방법 ERROR Code Protocol type MISS\n"),
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
