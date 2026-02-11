# TASKS: Task Board

프로젝트의 모든 작업 상태를 관리하는 보드입니다.

## Core Rules
1. **AI는 태스크를 `DONE` 상태로 직접 옮길 수 없습니다.** `DONE`은 오너의 최종 승인 후에만 가능합니다.
2. `READY_FOR_REVIEW` 상태로 태스크를 이동할 때는 반드시 **Review Pack + Evidence**를 포함해야 합니다.
3. **실행자 표기**: 모든 티켓 제목 앞에 `(AI)` 또는 `(OWNER)`를 반드시 표기합니다.
4. **상태 변경은 tickets/T-###.md에서만 수행하며, TASKS.md는 링크/요약 인덱스다.**

## Task Format
- `T-XXX [S-XXX] (P0) (AI|OWNER) 태스크 제목 (deps: T-XXX)`

---

## Board

### TODO
- T-002 [S-001] (P1) (AI) 코드 구조 공동 검토 (deps: T-001)

### BACKLOG

### IN_PROGRESS

### READY_FOR_REVIEW
- [T-003](tickets/T-003.md) [S-001] (P1) (AI) 웹앱 사용자 위치 기반 거리 표시 (deps: T-001)

### CHANGES_REQUESTED

### DONE
- [T-001](tickets/T-001.md) [S-001] (P0) (AI) 웹앱 지도 뷰 + 관리 기능 제거 — PR #1 merged
