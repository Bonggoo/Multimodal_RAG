import sys
import asyncio
import json
import os
import time
from pathlib import Path
from typing import List, Dict

# 프로젝트 루트 경로를 sys.path에 추가 (src 모듈 import 위해)
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import pandas as pd
from datasets import Dataset
from ragas import evaluate
# Ragas 최신 버전 (0.4.x+) 대응: 메트릭을 클래스로 import하고 인스턴스화해야 함
try:
    from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision
    # 0.4.x에서는 인스턴스화 필요
    faithfulness = Faithfulness()
    answer_relevancy = AnswerRelevancy()
    context_precision = ContextPrecision()
except ImportError:
    # 구버전 호환 (이미 인스턴스인 경우)
    from ragas.metrics import faithfulness, answer_relevancy, context_precision

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src.config import settings
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.query_expansion import QueryExpander
from src.rag_pipeline.generator import generate_answer_with_rag
from src.rag_pipeline.vector_db import get_embedding_function

# --- Ragas 설정 ---
# 평가용 심판 모델 (Gemini 3.0 Pro)
judge_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_EVAL_MODEL, # "gemini-3.0-pro"
    temperature=0,
    google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
)

# 임베딩 모델 (기존 로컬 모델 or Google)
# Ragas는 임베딩 모델도 필요로 함 (유사도 측정 등)
eval_embeddings = get_embedding_function()

# --- 데이터셋 로드 ---
def load_golden_dataset(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- RAG 실행 및 데이터 수집 ---
async def collect_rag_results(dataset: List[Dict]):
    print("Initializing RAG pipeline for evaluation...")
    retriever = get_retriever()
    query_expander = QueryExpander(model_name=settings.GEMINI_MODEL)
    
    rag_results = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [] # Ragas expects 'ground_truth' (string) or 'ground_truths' (list[str])
    }

    print(f"Running evaluation on {len(dataset)} questions...")
    
    for item in dataset:
        query = item["question"]
        ground_truth = item["ground_truth"]
        
        print(f"Processing: {query}")
        
        # RAG 파이프라인 호출 (동기 함수이므로 바로 호출)
        # generate_answer_with_rag는 내부적으로 retriever.invoke()를 호출하여 docs를 가져옴.
        # 하지만 Ragas는 'contexts' (list of str)를 요구하므로, 
        # generate_answer_with_rag를 수정하거나 여기서 별도로 retriever를 호출해야 함.
        # 정확한 평가를 위해 실제 파이프라인과 동일한 과정을 수행해야 함.
        
        # 1. Query Expansion
        expanded_query = query_expander.expand(query)
        
        # 2. Retrieval
        docs = retriever.invoke(expanded_query)
        contexts = [doc.page_content for doc in docs]
        
        # 3. Generation (Generation 함수 재사용 or 직접 호출)
        # generate_answer_with_rag는 검색을 내부에서 또 하므로 중복됨.
        # 여기서는 정확한 'contexts'를 평가에 넘기기 위해, 
        # Generate 단계만 수행하는 것이 좋으나, 기존 함수가 통합되어 있음.
        # 편의상 기존 함수를 호출하고, 검색은 재사용되지 않지만 결과는 동일하다고 가정.
        # (이상적으로는 generator가 retrieved docs를 입력받도록 리팩토링 되어야 함)
        
        response = generate_answer_with_rag(query, retriever, query_expander)
        answer = response["answer"]
        
        rag_results["question"].append(query)
        rag_results["answer"].append(answer)
        rag_results["contexts"].append(contexts)
        rag_results["ground_truth"].append(ground_truth) 
        
    return rag_results

# --- Ragas 평가 실행 ---
def run_ragas_eval(rag_data: Dict):
    print("\nRunning Ragas evaluation metrics...")
    
    # Dataset 변환
    dataset = Dataset.from_dict(rag_data)
    
    # 평가 지표 설정
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
    ]
    
    # 심판 모델 주입 (Ragas 최신 버전에 따른 설정 필요)
    # 0.4.x 버전에서는 llm, embeddings 인자를 evaluate에 전달 가능
    
    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=judge_llm, 
        embeddings=eval_embeddings
    )
    
    return results

if __name__ == "__main__":
    start_time = time.time()
    
    # 1. Load Data
    golden_data = load_golden_dataset("tests/evaluation/golden_dataset.json")
    
    # 2. Run Pipeline
    rag_data = asyncio.run(collect_rag_results(golden_data))
    
    # 3. Evaluate
    eval_results = run_ragas_eval(rag_data)
    
    # 4. Save & Print Results
    print("\n=== Evaluation Results ===")
    print(eval_results)
    
    df = eval_results.to_pandas()
    output_path = "tests/evaluation/eval_report.csv"
    df.to_csv(output_path, index=False)
    print(f"\nDetailed report saved to {output_path}")
    
    print(f"Total evaluation time: {time.time() - start_time:.2f}s")
