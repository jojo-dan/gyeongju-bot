# Git Workflow

## 브랜치 구조

- `main`: 안정 브랜치 (Production)
- `work/T-###`: 티켓 작업 브랜치 (티켓 1개 = 브랜치 1개)
- `closeout/T-###`: Closeout PR 전용 (문서/상태/Evidence만)

## 브랜치 생성 원칙

- 작업 시작은 최신 `origin/main`에서 분기
- 티켓 1개 = 브랜치 1개 (한 브랜치에서 여러 티켓을 섞지 않음)

## PR 규칙

- 제목: `[T-###] 티켓 제목`
- 본문: 티켓 연결, 변경 요약

## 커밋 컨벤션

- `feat:` 새 기능
- `fix:` 버그 수정
- `docs:` 문서 변경
- `refactor:` 리팩토링
- `chore:` 빌드/설정 변경

## Two-Stage Approval

1. Code PR (`work/T-###`) -> 오너 merge
2. Closeout PR (`closeout/T-###`) -> 오너 merge = DONE
