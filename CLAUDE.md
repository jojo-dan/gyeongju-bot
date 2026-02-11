# CLAUDE.md -- Gyeongju Bot

## 프로젝트 요약
경주 가족여행(2026.02.19~24) 일정을 관리하는 텔레그램 봇 + 웹앱.
Python 3.10+, Anthropic API + Tool Use 기반.

## 작업 시작 시 필수 읽기 (순서대로)
1. `CLAUDE.md` (이 파일)
2. `AGENTS.md` (에이전트 역할/권한)
3. `tickets/README.md` (티켓 운영 매뉴얼)
4. `TASKS.md` (현재 작업 보드)
5. `RULES.md` (자가검수 체크리스트)
6. `DECISIONS.md` (결정 로그)

## 기본 원칙
- **No-Write by default**: 오너가 GO를 주기 전에는 파일을 수정하지 않는다.
- **Plan Gate**: 코드 변경 전, 변경 파일 목록 / 검증 방법 / 리스크를 먼저 제시한다.
- **SSOT 우선**: 티켓 상태 변경은 tickets/T-###.md에서만 수행한다. TASKS.md는 인덱스(정본 아님).
- **append-only**: 티켓/기록은 완료 후에도 삭제/축약하지 않는다. 추가만 한다.
- **AI는 DONE 불가**: DONE은 오너만 확정. AI는 READY_FOR_REVIEW까지만 이동 가능.

## SSOT 규칙
- 티켓 정본: `tickets/T-###.md` -- 상태(Status) 변경은 여기서만
- 스토리 정본: `stories/S-###.md`
- 인덱스(정본 아님): `TASKS.md`, `STORIES.md`
- 지속 규범 변경: `DECISIONS.md`에 기록
- 상태 변경 순서: SSOT 파일 먼저 -> 인덱스는 동기화 대상

## Two-Stage Approval (CODE/HYBRID 필수)
- Code PR(`work/T-###`) -> 오너 verify -> Closeout PR(`closeout/T-###`) -> 오너 merge = DONE
- Closeout PR에는 문서/상태/Evidence만 포함 (기능 코드 변경 금지)
- Merge Gate: main 반영(merge) 전에는 DONE 처리/요청 금지

## Review Pack + Evidence (READY_FOR_REVIEW 필수)
Review Pack 최소 항목:
- Scope (변경 범위 요약)
- Changed files (수정 파일 목록)
- How to verify (검증 절차)
- Self-check results (RULES.md 기준)
- Risks & rollback

Evidence: 오너가 1분 내 검증 가능한 증거 (PR 링크, 실행 로그, 스크린샷 등)

## 에이전트 역할

| 역할 | 담당 | 권한 |
|---|---|---|
| Owner (조조) | 우선순위 결정, 최종 승인 | GO/NO-GO, PR merge, DONE 확정 |
| Team Lead | 전체 조율, 계획 수립, 티켓 관리 | 티켓 생성, 상태 이동(DONE 제외) |
| Dev | 기능 구현, 버그 수정 | 코드 변경, PR 생성 |
| QA | 코드 리뷰, 테스트, 품질 검수 | Review Pack 검증 |

## 오너 키워드
- `PLAN`: 구현 없이 계획/옵션/리스크만 제시
- `GO`: 제시한 Plan 기준으로 구현 진행
- `NO-GO`: 작업 중단, 대안 제시

## 커밋 컨벤션
- `feat:` 새 기능
- `fix:` 버그 수정
- `docs:` 문서 변경
- `refactor:` 리팩토링
- `chore:` 빌드/설정 변경

## 브랜치 규칙
- `main`: 안정 브랜치
- `work/T-###`: 티켓 작업 브랜치 (티켓 1개 = 브랜치 1개)
- `closeout/T-###`: 서류 마감용 (문서/상태만)

## 파일/폴더 생성 규칙
- `src/`: 소스코드 (봇, 핸들러, 클라이언트 등)
- `docs/`: 구현 세부사항, 데이터 구조, 디자인 시스템 등 문서
- `scripts/`: 유틸리티 스크립트
- `tests/`: 테스트 코드
- `tickets/`: 티켓 정본 (SSOT)
- `stories/`: 스토리 정본 (SSOT)

## 폴더 삭제 규칙
- 폴더 단위 삭제(rm -rf)는 실행 전 오너에게 "어떤 폴더를, 왜 삭제하는지" 보고 후 승인 받는다
- 예외: __pycache__/, .venv/, dist/, build/ 등 재생성 가능한 빌드 산출물은 자유롭게 삭제 가능

## 기술 스택
- Python 3.10+ / python-telegram-bot v20+ (async)
- Anthropic API (Tool Use) -- 여행 데이터 CRUD
- jsonbin.io -- 여행 데이터 저장소
- Vercel -- 웹앱 호스팅 (serverless API)
- python-dotenv / logging

## 코딩 규칙
- 한국어 주석/docstring, 영어 코드 (변수명/함수명)
- snake_case (함수, 변수), UPPER_SNAKE_CASE (상수)
- 네트워크 호출은 반드시 try/except + 타임아웃
- 모든 credential은 환경 변수로 관리 (.env), 하드코딩 금지
- 로깅은 logging 모듈 사용 (print 금지), 기본 레벨 INFO
- 타입 힌트 사용 권장
