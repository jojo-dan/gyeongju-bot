# AGENTS.md — Gyeongju Bot

> 팀 구성, 운영 규칙, SSOT 원칙 등 공통 규칙은 **워크스페이스 CLAUDE.md(`jojodan/CLAUDE.md`)의 "팀 운영 플레이북"에서 상속**된다.
> 이 파일은 **이 프로젝트에서의 역할별 기술 맥락**만 담는다.

## 0) Must-read (작업 시작 체크리스트)

1. `CLAUDE.md` (이 프로젝트 + 상위 워크스페이스 CLAUDE.md)
2. `AGENTS.md` (이 문서)
3. `tickets/README.md` (티켓 운영 매뉴얼)
4. `TASKS.md` (보드/인덱스)
5. `RULES.md` (자가검수 체크리스트)
6. `DECISIONS.md` (결정 로그)

## 1) 프로젝트별 역할 & 기술 맥락

| 역할 | 이름 | 이 프로젝트에서의 담당 |
|---|---|---|
| **Team Lead** | 를르슈 | Python 아키텍처, Anthropic API 설계, 전체 기술 조율 |
| **Project Manager** | 하이바라 | 티켓/문서 관리, Mermaid 다이어그램으로 시스템 설명 |
| **UX Designer** | 크라피카 | 웹앱(`webapp/`) 사용자 플로우, 시니어 UX 최적화 (큰 글씨, 고대비) |
| **UI Designer** | 히소카 | 웹앱 비주얼 디자인, 한국어 UI, `docs/UI_DESIGN_SYSTEM.md` 참조 |
| **Frontend Dev** | 스자쿠 | `webapp/` Vercel 웹앱 구현 (HTML/CSS/JS, 카카오맵 연동) |
| **Backend Dev** | 알폰스 | 봇 코어(`src/`), Anthropic API + Tool Use, jsonbin.io 연동, 텔레그램 핸들러 |
| **QA Engineer** | 코난 | `python3 -m unittest discover tests/ -v` + VPS 실동작 검증 (텔레그램 메시지 테스트) |
| **Rules Auditor** | 체펠리 | 운영 문서 감사, SSOT 정합성 검증 |
| **Researcher** | 유키 | python-telegram-bot/Anthropic API 최신 문서 조사, 구현 사례 분석 |

## 2) 프로젝트 특화 팀 운영

### 디자인 협업 (이 프로젝트)
- 디자인 시스템: `docs/UI_DESIGN_SYSTEM.md` 참조
- 시니어 UX 최적화가 핵심 (큰 글씨, 고대비, 한국어 UI)
- 카카오맵 연동 UI

### 백엔드 (알폰스) — 이 프로젝트의 주력 구현 에이전트
- 담당 범위: `src/` 내 Python 모듈 전체
- Anthropic API (Tool Use), python-telegram-bot (async), jsonbin.io 연동
- `claude-sonnet-4-5-20250929` 모델 사용

### 프론트엔드 (스자쿠)
- `webapp/` 내 Vercel 배포 웹앱 구현
- HTML/CSS/JS 기반, 카카오맵 연동

### QA (코난)
- 유닛 테스트: `python3 -m unittest discover tests/ -v`
- 실동작 검증: VPS에서 봇 재시작 후 텔레그램 메시지 테스트
- 모든 credential이 .env에만 있는지 확인
