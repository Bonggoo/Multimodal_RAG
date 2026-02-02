import subprocess
import json
import os
from pathlib import Path

def run_qa(query):
    print(f"Testing Question: {query}")
    try:
        result = subprocess.run(
            ["poetry", "run", "python", "main.py", "qa", query],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

questions = [
    "QD77MS 모듈의 주요 특징과 제어 축 수는 얼마인가요?",
    "서보 앰프와의 SSCNET III/H 통신 방식의 장점은 무엇인가요?",
    "에러 코드 104번의 정의와 구체적인 해결 방법 3가지를 알려줘.",
    "위치결정 데이터(Positioning Data) 구성 요소 중 '제어 방식'의 종류는?",
    "OPR(원점 복귀) 방식 중 '데이터 세트식'은 어떤 경우에 사용하나요?"
]

results_file = Path("test_results_1_5.md")
with open(results_file, "w", encoding="utf-8") as f:
    f.write("# 🧪 테스트 결과 (1-5번)\n\n")
    for i, q in enumerate(questions, 1):
        output = run_qa(q)
        f.write(f"## {i}. {q}\n\n")
        f.write("### 결과:\n")
        f.write(f"```\n{output}\n```\n\n")
        f.write("---\n\n")

print(f"Results saved to {results_file}")
