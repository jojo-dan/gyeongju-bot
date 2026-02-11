# DECISIONS: Decision Log

이 문서는 프로젝트 진행 과정에서 발생한 주요 기술적/정책적 결정 사항을 기록합니다.
모든 결정은 협의 후 이 로그에 기록되어야 하며, 이는 프로젝트의 Single Source of Truth(SSOT) 역할을 합니다.

## Decision Template
- **D-YYYYMMDD-XXX: 제목**
    - **Decision**: 결정된 내용 요약
    - **Rationale**: 결정의 이유 및 배경
    - **Impact**: 이 결정이 미치는 영향
    - **Rollback**: 결정 번복 시 필요한 조치

---

## Log

### D-20260211-001: 프로젝트 구조 개편 -- 거버넌스 문서 체계 도입
- **Decision**: Python 소스를 `src/`로 배치하고, agent-team-dashboard 수준의 거버넌스 문서 체계(AGENTS.md, RULES.md, DECISIONS.md, tickets/, stories/)를 도입한다.
- **Rationale**: 코드와 문서의 체계적 관리를 위해 검증된 SSOT/티켓 운영 모델을 적용한다. agent-team-dashboard에서 확립한 운영 체계를 Python 프로젝트 맥락으로 재사용한다.
- **Impact**: 폴더 구조 변경(src/ 기반), 거버넌스 문서 3종 신규 생성, CLAUDE.md 업데이트. VPS에서 systemd 서비스 파일의 ExecStart 경로 수정이 필요할 수 있다.
- **Rollback**: `git revert`로 문서/구조 변경 복원 가능. VPS에서 `ExecStart=/usr/bin/python3 bot.py` 경로를 원래대로 복원한다.
