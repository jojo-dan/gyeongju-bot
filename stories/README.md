# stories/README.md -- Story 운영 매뉴얼 (SSOT)

이 프로젝트는 **Repo 안의 문서가 곧 운영 시스템(SSOT)** 입니다.
스토리는 "요구사항 메모"가 아니라 **사용자 스토리 + 비즈니스 요구사항 + 진척 관리**입니다.

---

## 1) SSOT 구조

- **정본(SSOT):** `stories/S-###.md`
  - 상태 변경은 스토리 파일에서만 합니다.

- **인덱스/보드:** `STORIES.md`
  - 정본이 아니며, 스토리 파일 변경 후 동기화됩니다.

---

## 2) 스토리 라이프사이클

- `BACKLOG`: 아직 시작하지 않음
- `IN_PROGRESS`: 진행 중
- `BLOCKED`: 차단됨
- `READY_FOR_REVIEW`: 검토 대기
- `DONE`: **오너만** 최종 확정

---

## 3) 스토리 파일 포맷

- **Status**: 스토리 상태
- **Linked tickets**: 연결된 티켓 목록
- **Title**: 스토리 제목
- **Story**: 사용자 스토리 설명
- **Acceptance Criteria**: 완료 조건
- **Non-goals**: 이번 스토리에서 다루지 않는 범위

---

## 4) 스토리 파일은 append-only (기록 보존)

- 완료 시에도 삭제/축약하지 않습니다.
- 추가 수정은 `## Update YYYY-MM-DD` 섹션을 추가합니다.

---

끝.
