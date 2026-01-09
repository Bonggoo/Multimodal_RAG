# 💎 GEMINI.md: Vibe Coding & Engineering Principles (Updated)

## 0. 최우선 원칙 (Global Priority)
*   **언어**: **그 어떤 작업을 하더라도 모든 소통, 주석, 결과물은 한국어**가 필수입니다. (절대 예외 없음)

## 1. 핵심 루틴 (Workflow)
*   **할 일 관리**: 작업 시작 전 `task.md` 업데이트 후 단계별 진행. 응답 마지막에 진행률 표시.
*   **Git (gh CLI)**: 모든 변경은 `gh` CLI로 기능 단위 커밋/PR 생성. (Conventional Commits 준수)
*   **문서화**: Mermaid 사용 시 구문 오류에 극도로 주의하며, 복잡한 설계는 SVG 파일로 생성하여 에러를 방지함.

## 2. 엔지니어링 및 품질 (Engineering & Quality)
*   **Simple is Best (직관적 유지보수)**: 작동하는 가장 단순한 코드를 우선하며, Bonggoo님이 직관적으로 이해하고 관리하기 쉬운 수준을 유지함. (보안 및 에러 대응은 철저히 함)
*   **SOLID & Clean Architecture**: 단일 책임(SRP)과 핵심 로직-세부 구현 분리를 통해 "확장 가능하고 고치기 쉬운 코드" 지향.
*   **Interface First & Type Safety**: 외부 도구는 추상화 계층을 거쳐 사용하고, Pydantic/Type Hints로 데이터 흐름을 명시함.
*   **최신성 유지 (Planning)**: 계획 단계에서 항상 모델(Gemini 3.0+ 등) 및 라이브러리의 최신 문법을 검색하여 반영함.

## 3. 실시간 정보 및 검색 전략 (Search Strategy)
*   **Search Strategy**: 기술 탐구 및 최신 정보(소프트웨어 버전, 모델 출시 등) 확인은 **Google 검색**을 필수적으로 수행함.

## 4. 검증 및 문서화 (Validation & Sync)
*   **검증 필수**: 기능 완료 후 반드시 동작 여부를 확인(테스트 실행)하고 결과를 사용자에게 공유함.
*   **문서 동기화**: 코드 변경 시 관련 문서(README, API 가이드 등)를 즉시 최신화하여 관리 편의성을 높임.
*   **Task 관리**: `task.md` 업데이트 시, 새로운 task는 항상 **최신 날짜와 함께 상단에 추가**하여 현재 진행 상황을 즉시 확인할 수 있도록 함.
