import requests
import json
import time
from pathlib import Path

# 설정
BASE_URL = "http://localhost:8000"
API_KEY = "12345"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def ask_qa(query, question_id):
    print(f"[{question_id}] Testing via API: {query}")
    payload = {"query": query}
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/qa", headers=HEADERS, json=payload, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            return {
                "id": question_id,
                "query": query,
                "answer": result.get("answer"),
                "images": result.get("retrieved_images", []),
                "latency": f"{end_time - start_time:.2f}s",
                "status": "SUCCESS"
            }
        else:
            return {
                "id": question_id,
                "query": query,
                "error": f"HTTP {response.status_code}: {response.text}",
                "status": "FAILED"
            }
    except Exception as e:
        return {
            "id": question_id,
            "query": query,
            "error": str(e),
            "status": "ERROR"
        }

# 질문 리스트
questions = [
    "JOG 운전 시 속도 제한 수치를 설정하는 파라미터는 무엇인가요?",
    "가감속 시간 설정 시 '지수 함수' 방식이 지원되나요?",
    "하드웨어 리미트 스위치(FLS, RLS) 배선 시 B접점(N.C)을 권장하는 이유는?",
    "위치결정 제어 중 'ABS(절대값)'와 'INC(증분값)' 시스템의 결정적인 차이는?",
    "티칭(Teaching) 기능을 사용하여 목표 위치를 저장하는 절차는?",
    "2축 직선 보간 제어 시 합성 속도 계산 방식은?",
    "인터럽트 위치결정 제어 기동 시 필요한 외부 입력 신호는?",
    "파라미터 초기화(Flash ROM) 시 주의사항은 무엇인가요?",
    "에러 리셋(Error Reset)을 수행하는 버퍼 메모리 주소를 알려줘.",
    "현재 피드 값(Current Feed Value)을 모니터링하기 위한 주소는?"
]

results = []
for i, quest in enumerate(questions, 6): # 6번부터 시작
    res = ask_qa(quest, i)
    results.append(res)
    time.sleep(1) # 부하 조절

# 결과 저장
results_file = Path("test_results_api_6_15.md")
with open(results_file, "w", encoding="utf-8") as f:
    f.write("# 🌐 REST API 테스트 결과 (6-15번)\n\n")
    for r in results:
        f.write(f"## {r['id']}. {r['query']}\n\n")
        if r['status'] == "SUCCESS":
            f.write(f"**지연 시간:** {r['latency']}\n\n")
            f.write(f"### 답변:\n{r['answer']}\n\n")
            f.write(f"### 관련 이미지:\n")
            for img in r['images']:
                f.write(f"- {img}\n")
        else:
            f.write(f"### ❌ 오류:\n```\n{r['error']}\n```\n")
        f.write("\n---\n\n")

print(f"API Test Results saved to {results_file}")
