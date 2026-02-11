# AGENTS.md (Start Here)

이 문서는 이 프로젝트에서 작업하는 모든 에이전트가
**작업 시작 시 반드시 먼저 읽는 문서**입니다.

## 0) Must-read (작업 시작 체크리스트)

작업을 시작하기 전에 아래 문서들을 **순서대로** 읽고 현재 운영 규칙을 확인합니다.

1. `AGENTS.md` (이 문서)
2. `CLAUDE.md` (프로젝트 규칙/설정)
3. `tickets/README.md` (티켓 운영 매뉴얼)
4. `TASKS.md` (보드/인덱스)
5. `RULES.md` (자가검수 체크리스트)
6. `DECISIONS.md` (결정 로그)

## 1) SSOT (정본) 규칙

- 티켓 SSOT: `tickets/T-###.md`
  - 상태(Status) 변경은 **티켓 파일에서 먼저** 한다.
  - `TASKS.md`는 인덱스(sync 대상). 정본이 아니다.
- 스토리 SSOT: `stories/S-###.md`
- 지속 규범 변경: `DECISIONS.md`에 기록.
- 상태 변경 순서: SSOT 파일 먼저 -> 인덱스는 동기화 대상.

## 2) Roles & Permissions

### 기본 원칙: No-Write by default
- 오너가 명시적으로 "GO"라고 말하기 전에는 **레포 파일을 수정하지 않는다.**
- 기본 동작은 **읽기/분석/계획(Plan)/옵션 제시/리스크 설명**.

### 역할 분담

| 역할 | 담당 | 기본 동작 |
|---|---|---|
| **Owner (조조)** | 우선순위/승인(GO/NO-GO), DONE 확정 | 전체 권한 |
| **Team Lead** | 계획 수립, 티켓 배분, 에이전트 조율 | 읽기 + 계획 -> GO 후 쓰기 |
| **Dev** | 기능 구현, 버그 수정, 테스트 작성 | 티켓 범위 내 쓰기 |
| **QA/Reviewer** | 리뷰, 테스트 실행, 규칙 준수 검증 | 읽기 + 코멘트 |

### Plan Gate (선계획-후구현)
코드 변경 전, 오너에게 반드시 공유:
1. 변경 파일 목록
2. 검증 방법
3. 리스크 & 롤백

### 오너 키워드
- `PLAN`: 구현 없이 계획만
- `GO`: 제시한 Plan대로 진행
- `NO-GO`: 중단, 대안 제시

## 3) Two-Stage Approval (CODE/HYBRID)

- CODE/HYBRID는 **Code PR merge만으로 DONE이 아닙니다.**
- 흐름: Code PR(`work/T-###`) -> (필요 시 verify/체크) -> Closeout PR(`closeout/T-###`) -> 오너가 Closeout PR merge = DONE 확정
- Closeout PR에는 문서/상태/Evidence만 포함한다 (기능 코드 변경 금지).

## 4) "대화에서 나온 결론" 기록 규칙

| 성격 | 기록 위치 |
|---|---|
| 이번 작업 단위 기록/증빙 | `tickets/T-###.md` |
| 앞으로 유지될 규칙/정의 변경 | `DECISIONS.md` |
| 제품 범위/우선순위 변경 | `stories/S-###.md` |

## 5) Python 프로젝트 특화

### 테스트 실행
```bash
python3 -m unittest discover tests/ -v
```
- 모든 코드 변경 후 테스트를 실행하여 통과 여부를 확인한다.
- 새 모듈 추가 시 `tests/test_{모듈명}.py`를 함께 작성한다.

### src/ 모듈 import 규칙
- 소스코드는 `src/`에 위치. 순환 import 금지, 의존 방향 단방향 유지.
- 모듈 구조: `src/bot.py`(메인), `src/claude_handler.py`(API), `src/jsonbin_client.py`(HTTP), `src/prompts.py`(템플릿)

### .env 관리
- credential은 `.env`로만 관리. 절대 커밋하지 않는다 (`.gitignore` 포함).
- VPS 배포 시 systemd `EnvironmentFile`로 로드.
