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

### D-20260211-003: 카카오 SDK 제거
- **Decision**: 카카오 Maps SDK `<script>` 태그를 webapp/index.html에서 제거한다.
- **Rationale**: T-001에서 "Places API용으로 유지"했으나, T-003에서 좌표를 JSON에 사전 저장하는 방식을 채택하면서 런타임 API 호출이 불필요해졌다. SDK 로드에 따른 불필요한 네트워크 요청과 번들 크기를 줄인다.
- **Impact**: webapp/index.html에서 카카오 SDK 참조 삭제. S-001.md AC 3번 업데이트 필요.
- **Rollback**: `<script src="//dapi.kakao.com/v2/maps/sdk.js?appkey=...&libraries=services">` 태그 복원.

### D-20260211-002: 좌표 데이터 사전 저장 방식 채택
- **Decision**: 런타임 카카오 Places API 검색 대신, 여행 JSON의 option 스키마에 lat/lng 필드를 추가하고 빌드타임에 좌표를 사전 수집한다.
- **Rationale**: 장소가 고정적(~30개)이므로 런타임 API 호출 0회, 검색어 불일치 리스크 제거, 완전 클라이언트 사이드 거리 계산 가능.
- **Impact**: option 스키마에 lat/lng 필드 추가, collect_coords.py 스크립트 신규 생성, tool_definitions.py 업데이트.
- **Rollback**: option에서 lat/lng 필드 제거, collect_coords.py 삭제.

### D-20260211-001: 프로젝트 구조 개편 -- 거버넌스 문서 체계 도입
- **Decision**: Python 소스를 `src/`로 배치하고, agent-team-dashboard 수준의 거버넌스 문서 체계(AGENTS.md, RULES.md, DECISIONS.md, tickets/, stories/)를 도입한다.
- **Rationale**: 코드와 문서의 체계적 관리를 위해 검증된 SSOT/티켓 운영 모델을 적용한다. agent-team-dashboard에서 확립한 운영 체계를 Python 프로젝트 맥락으로 재사용한다.
- **Impact**: 폴더 구조 변경(src/ 기반), 거버넌스 문서 3종 신규 생성, CLAUDE.md 업데이트. VPS에서 systemd 서비스 파일의 ExecStart 경로 수정이 필요할 수 있다.
- **Rollback**: `git revert`로 문서/구조 변경 복원 가능. VPS에서 `ExecStart=/usr/bin/python3 bot.py` 경로를 원래대로 복원한다.
