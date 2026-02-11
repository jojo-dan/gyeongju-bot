# RULES: Review Checklist

이 문서는 작업 완료 후 자가검수를 수행할 때 사용하는 체크리스트입니다.
`READY_FOR_REVIEW` 상태로 태스크를 이동하기 전에 반드시 확인하세요.

## Review Checklist

### 코드 품질 (Code Quality)
- [ ] Python type hints를 사용했는가?
- [ ] logging 모듈을 사용했는가? (print 사용 금지)
- [ ] import 에러가 없는가? (`python3 -c "import src.모듈명"` 확인)
- [ ] `python3 -m unittest discover tests/ -v` 가 통과하는가?
- [ ] 불필요한 print/debug 코드가 제거되었는가?
- [ ] docstring이 한국어로 작성되었는가?

### 보안 (Security)
- [ ] 모든 credential이 환경 변수(.env)로만 관리되고 있는가?
- [ ] API 키, 토큰 등이 코드에 하드코딩되어 있지 않은가?
- [ ] .env 파일이 .gitignore에 포함되어 있는가?
- [ ] 로그에 민감 정보(토큰, 키)가 노출되지 않는가?

### 네트워크 (Network)
- [ ] 모든 HTTP 요청(requests, API 호출)에 try/except가 적용되었는가?
- [ ] 모든 네트워크 호출에 timeout이 설정되었는가?
- [ ] 외부 서비스 장애 시 graceful fallback이 있는가?
- [ ] 재시도 로직이 필요한 곳에 구현되었는가?

### SSOT 충돌 검사
- [ ] CLAUDE.md의 규칙과 충돌하지 않는가?
- [ ] DECISIONS.md의 결정 사항과 일치하는가?
- [ ] 변경 사항이 DECISIONS.md에 기록되었는가? (필요한 경우)

### Git Workflow
- [ ] 브랜치명이 `work/T-###` 형식을 따르는가?
- [ ] 작업/커밋 전 현재 브랜치를 확인했는가?
- [ ] 티켓 상태가 `READY_FOR_REVIEW`인가?
- [ ] Review Pack이 작성되었는가?

### 티켓 상태 변경 규칙
- [ ] **상태 변경은 티켓 파일(`tickets/T-###.md`)에서만 수행하는가?**
- [ ] **TASKS.md는 인덱스(정본 아님)로만 사용하는가?**
- [ ] 티켓 파일의 `**Status**:` 필드를 먼저 업데이트했는가?

## Merge Gate (CODE/HYBRID)
- main 반영(merge) 이전에는 DONE으로 이동하지 않는다.
- Closeout PR에는 문서/상태/Evidence만 포함한다 (기능 코드 변경 금지).
