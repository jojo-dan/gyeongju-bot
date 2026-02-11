# tickets/README.md -- Ticket 운영 매뉴얼 (SSOT)

이 프로젝트는 **Repo 안의 문서가 곧 운영 시스템(SSOT)** 입니다.
티켓은 "할 일 메모"가 아니라 **작업 기록 + 검수 패키지 + 종료 증빙**입니다.

---

## 1) SSOT 구조 (무엇이 정본인가)

- **정본(SSOT):** `tickets/T-###.md`
  - 티켓의 상태(Status), 본문, Plan, Evidence, Review Pack이 모두 여기에 있습니다.
  - **상태 변경은 티켓 파일에서만** 합니다.

- **인덱스/보드:** `TASKS.md`
  - 전체 티켓 링크와 요약(Status/work_type/deps)만 보여주는 "보드"입니다.
  - 정본이 아니며, 티켓 파일 변경 후 필요 시 동기화됩니다.

---

## 2) 티켓 라이프사이클 (상태 정의)

- `TODO`: 아직 시작 안 함
- `BACKLOG`: 우선순위 낮음/추후 진행
- `IN_PROGRESS`: AI가 작업 중
- `READY_FOR_REVIEW`: AI 작업 완료, 오너 검수 대기 (Review Pack + Evidence 포함 필수)
- `CHANGES_REQUESTED`: 오너가 수정 요청함 (AI가 다시 작업)
- `DONE`: **오너만** 최종 확정(서명)한 상태

> 규칙: AI는 `DONE`으로 직접 이동할 수 없습니다. `DONE`은 오너의 최종 승인/머지로만 성립합니다.

---

## 3) work_type 정의 (CODE / EXTERNAL / HYBRID)

- `CODE`: 코드 변경이 포함된 작업 (Python 스크립트, 설정 파일, 워크플로우 등)
- `EXTERNAL`: 코드 변경 없이 외부 콘솔/설정에서 수행하는 작업
- `HYBRID`: 코드 변경 + 외부 작업이 함께 필요한 작업

---

## 4) DONE 규칙(done_rule) & Merge Gate (Two-Stage Approval)

### 핵심 원칙
- CODE/HYBRID는 "코드가 main에 합쳐졌다"는 사실만으로 DONE이 아닙니다.
- **오너가 실제 동작/결과를 확인한 뒤**, "서류 마감(Closeout PR)"까지 끝나야 DONE입니다.

### Two-Stage Approval (2단계 PR)

1) **Code PR (AI)**: 브랜치 `work/T-###`, 기능/코드 변경 반영
2) **Owner verify (오너)**: PR merge 후 실제 동작 확인
3) **Closeout PR (AI)**: 브랜치 `closeout/T-###`, 문서/상태/Evidence만 포함
4) **DONE 확정 (오너)**: Closeout PR merge = DONE

### work_type별 DONE 규칙 요약
- `CODE`: Code PR merge + Closeout PR merge(오너) = DONE
- `HYBRID`: Code PR merge + 오너 verify + Closeout PR merge = DONE
- `EXTERNAL`: 오너 verify 후 DONE (Closeout PR은 선택)

---

## 5) Evidence 규칙

`READY_FOR_REVIEW`로 올릴 때 Evidence는 **필수**입니다.
오너가 "코드 실행 없이" 판단할 수 있도록 최소 증거를 남깁니다.

### Evidence 최소 템플릿
- `CODE/HYBRID`: PR 링크, 실행 로그/스크린샷, 오너 3-step verify
- `EXTERNAL`: 확인 URL, 스크린샷/로그, 기대 결과 1줄

---

## 6) 티켓 파일은 append-only (기록 보존)

- 티켓은 작업 기록이므로 **완료 시에도 삭제/축약하지 않습니다.**
- Plan/Evidence/Review Pack 섹션은 보존(append-only)합니다.

---

끝.
