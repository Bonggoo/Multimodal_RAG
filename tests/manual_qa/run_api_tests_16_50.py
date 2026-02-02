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
        response = requests.post(f"{BASE_URL}/qa", headers=HEADERS, json=payload, timeout=120)
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

# 질문 리스트 16-50
questions = [
    "수동 펄스 발생기(MPG)를 연동하기 위한 하드웨어 연결 단자 정보는?",
    "M-코드(M-Code) 출력 기능을 활용한 외부 기기 동기화 방법은?",
    "가속도와 감속도를 서로 다르게 설정할 수 있는 파라미터가 있나요?",
    "백래시(Backlash) 보정 기능 설정 시 허용되는 수치 범위는?",
    "토크 제한(Torque Limit) 기능이 실제 서보 앰프에 전달되는 과정은?",
    "동기 제어(Synchronous Control) 모드에서 '가상 축'의 역할은 무엇인가요?",
    "위치결정 완료 신호(Xn1)가 켜지지 않을 때 가장 먼저 확인해야 할 비트 상태는?",
    "버퍼 메모리의 '고속 읽기/쓰기' 영역은 어디인가요?",
    "매뉴얼에서 설명하는 '정지 원인' 중 'Emg Stop'과 'Decel Stop'의 차이는?",
    "펌웨어 버전 확인 방법과 해당 버전별 추가 기능은 어디서 보나요?",
    "로보스타 N1 시스템에서 알람 0101번이 발생하는 주된 원인은?",
    "'서보 OFF' 상태에서 기구부가 흘러내릴 때 점검해야 할 알람 코드는?",
    "통신 에러(Communication Error) 발생 시 RS-232/485 배선 점검 포인트는?",
    "원점 복귀(Homing) 실패 시 표시되는 알람 코드와 해결책은?",
    "비상 정지(E-STOP) 입력이 해제되지 않을 때 전기적 체크 리스트는?",
    "'과부하(Overload)' 알람 발생 시 모터 용량 대비 실제 부하 확인 방법은?",
    "엔코더 배터리(Encoder Battery) 저전압 경고 알람 번호는 무엇인가요?",
    "배터리 교체 후 알람을 물리적으로 리셋하는 순서는?",
    "소프트웨어 리미트(Soft Limit) 초과 알람 시 수동 조작으로 복귀하는 법은?",
    "제어기 내부 냉각 팬(Fan) 이상 알람 시 조치 방법은?",
    "티칭 펜던트 화면이 들어오지 않을 때 확인해야 할 하드웨어 스위치는?",
    "알람 이력(Alarm History)에서 최근 발생한 5개의 코드를 보는 방법은?",
    "로봇 충돌 감지(Collision Detection) 감도를 설정하는 파라미터 이름은?",
    "모터 과열 알람 시 자연 냉각 권장 시간은 몇 분인가요?",
    "브레이크 해제(Brake Release) 시 안전을 위해 반드시 선행되어야 할 조치는?",
    "QD77MS 매뉴얼 807페이지의 표 내용을 바탕으로 에러 종류를 요약해줘.",
    "QD77MS 매뉴얼 808페이지에 있는 '조치 방법' 이미지를 설명해줘.",
    "로보스타 N1 매뉴얼에서 알람 코드 전체 리스트가 시작되는 페이지 번호는?",
    "QD77MS와 로보스타 N1의 에러 리셋 절차상 공통된 '안전 확인' 사항은?",
    "매뉴얼 내의 '배선도' 이미지 중 노이즈 필터 설치 사례를 찾아 설명해줘.",
    "특정 에러 코드의 '정의-원인-조치'를 표 형태로 정리해서 답변해줘.",
    "위치결정 모듈 설치 시 권장되는 접지(Grounding) 클래스는 무엇인가요?",
    "QD77MS의 버퍼 메모리 맵 중 '고급 제어용' 영역을 요약해줘.",
    "로보스타 N1의 기본 I/O 할당표 상의 입력 1번 접점 기능을 알려줘.",
    "매뉴얼 전체에서 '경고(WARNING)'와 '주의(CAUTION)' 문구를 추출해 요약해줘."
]

results = []
for i, quest in enumerate(questions, 16):
    res = ask_qa(quest, i)
    results.append(res)
    time.sleep(2) # 부하 조절

# 결과 저장
results_file = Path("test_results_api_16_50.md")
with open(results_file, "w", encoding="utf-8") as f:
    f.write("# 🌐 REST API 테스트 결과 (16-50번)\n\n")
    for r in results:
        f.write(f"## {r['id']}. {r['query']}\n\n")
        if r['status'] == "SUCCESS":
            f.write(f"**지연 시간:** {r['latency']}\n\n")
            f.write(f"### 답변:\n{r['answer']}\n\n")
            f.write(f"### 관련 이미지:\n")
            if r['images']:
                for img in r['images']:
                    f.write(f"- {img}\n")
            else:
                f.write("없음\n")
        else:
            f.write(f"### ❌ 오류:\n```\n{r['error']}\n```\n")
        f.write("\n---\n\n")

print(f"API Test Results saved to {results_file}")
