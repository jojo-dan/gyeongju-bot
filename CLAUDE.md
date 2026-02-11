# CLAUDE.md -- Gyeongju Bot

> 팀 운영 규칙(기본 원칙, SSOT, Plan Gate, Two-Stage Approval, 에이전트 팀 등)은
> **워크스페이스 CLAUDE.md(`jojodan/CLAUDE.md`)에서 상속**된다. 이 파일은 프로젝트 전용 규칙만 담는다.

## 프로젝트 요약
경주 가족여행(2026.02.19~24) 일정을 관리하는 텔레그램 봇 + 웹앱.
Python 3.10+, Anthropic API + Tool Use 기반.

## 작업 시작 시 필수 읽기 (순서대로)
1. `CLAUDE.md` (이 파일 + 상위 워크스페이스 CLAUDE.md)
2. `AGENTS.md` (프로젝트별 역할/기술 맥락)
3. `tickets/README.md` (티켓 운영 매뉴얼)
4. `TASKS.md` (현재 작업 보드)
5. `RULES.md` (자가검수 체크리스트)
6. `DECISIONS.md` (결정 로그)

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

## 파일/폴더 생성 규칙
- `src/`: 소스코드 (봇, 핸들러, 클라이언트 등)
- `docs/`: 구현 세부사항, 데이터 구조, 디자인 시스템 등 문서
- `scripts/`: 유틸리티 스크립트
- `tests/`: 테스트 코드
- `tickets/`: 티켓 정본 (SSOT)
- `stories/`: 스토리 정본 (SSOT)

## src/ 모듈 구조
| 모듈 | 역할 |
|---|---|
| `src/bot.py` | 텔레그램 봇 엔트리포인트 |
| `src/claude_api_handler.py` | Anthropic API + Tool Use 메시지 처리 |
| `src/claude_handler.py` | Claude CLI subprocess 처리 (레거시) |
| `src/jsonbin_client.py` | jsonbin.io HTTP 클라이언트 |
| `src/prompts.py` | 프롬프트 템플릿 (CLI 모드용) |
| `src/tool_definitions.py` | Tool Use 도구 정의 |
| `src/tool_executor.py` | 도구 실행 엔진 |

## 테스트 실행
```bash
python3 -m unittest discover tests/ -v
```
- 모든 코드 변경 후 테스트를 실행하여 통과 여부를 확인한다.
- 새 모듈 추가 시 `tests/test_{모듈명}.py`를 함께 작성한다.

## .env 관리
- credential은 `.env`로만 관리. 절대 커밋하지 않는다 (`.gitignore` 포함).
- VPS 배포 시 systemd `EnvironmentFile`로 로드.

## VPS 배포
- SSH: `root@76.13.176.32` (키: `~/.ssh/id_ed25519_openclaw`)
- 봇 경로: `/home/ubuntu/gyeongju-bot`
- 서비스: `systemctl restart gyeongju-bot`
- venv: `/home/ubuntu/gyeongju-bot/venv/bin/python3 src/bot.py`
