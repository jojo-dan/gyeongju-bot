# PROJECT_SPEC.md — 모듈별 상세 요구사항

---

## 모듈 1: bot.py (텔레그램 봇 메인)

### 역할
텔레그램 메시지 수신 → 처리 → 응답의 오케스트레이터.

### 요구사항

- python-telegram-bot v20+ (async 기반) 사용
- Application 빌더 패턴으로 봇 초기화
- MessageHandler로 텍스트 메시지 수신
- 허용된 user ID만 처리 (ALLOWED_USER_IDS), 나머지는 무시 (로그만 남김)
- 메시지 처리 흐름:
  1. jsonbin에서 현재 데이터 GET
  2. claude_handler에 (현재 JSON + 사용자 메시지) 전달
  3. 응답 파싱: JSON 변경이면 jsonbin PUT + 확인 메시지, 아니면 그대로 전달
  4. 텔레그램으로 응답 전송
- 에러 핸들링: 사용자에게 친절한 에러 메시지, 상세 로그 기록
- /start 명령어: 간단한 인사 + 사용법 안내
- /today 명령어: 오늘 날짜 기준 일정 요약 (숏컷)
- 긴 메시지는 4096자 제한에 맞게 분할 전송

### 코드 구조 예시

```python
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from claude_handler import process_message
from jsonbin_client import JsonBinClient

load_dotenv()
logger = logging.getLogger(__name__)

ALLOWED_USER_IDS = [int(uid.strip()) for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid.strip()]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """메인 메시지 핸들러"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USER_IDS:
        logger.warning(f"허용되지 않은 사용자: {user_id}")
        return
    
    # ... 처리 로직

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    # 핸들러 등록
    app.run_polling()

if __name__ == "__main__":
    main()
```

---

## 모듈 2: claude_handler.py (Claude CLI 래퍼)

### 역할
Claude CLI를 subprocess로 호출하고, 응답을 파싱하여 JSON 변경/텍스트 응답을 구분.

### 요구사항

- `claude -p "{prompt}" --output-format text` 형태로 호출
- 타임아웃: 120초 (Claude가 오래 걸릴 수 있음)
- 프롬프트 구성: prompts.py의 템플릿 + 현재 JSON + 사용자 메시지
- 응답 파싱 로직:
  - ```json ... ``` 코드블록이 있으면 → JSON 변경으로 판단, JSON 추출
  - 코드블록 없으면 → 텍스트 응답 (조회/추천/대화)
- 인증 만료 감지: stderr에 "authentication", "OAuth", "expired" 키워드 → 알림 트리거
- 재시도: 1회 (네트워크 일시 장애 대비)
- 프롬프트 내 JSON은 크기 제한 고려 (너무 크면 요약)

### 반환 타입

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClaudeResponse:
    success: bool
    response_type: str          # "update" | "text" | "error"
    text_response: str          # 텔레그램에 보낼 메시지
    updated_json: Optional[dict] # response_type이 "update"일 때만
    error_message: Optional[str] # response_type이 "error"일 때만
```

### 인증 만료 감지

```python
AUTH_ERROR_KEYWORDS = ["authentication", "oauth", "expired", "401", "login"]

def _is_auth_error(stderr: str) -> bool:
    return any(kw in stderr.lower() for kw in AUTH_ERROR_KEYWORDS)
```

---

## 모듈 3: jsonbin_client.py (jsonbin.io 클라이언트)

### 역할
jsonbin.io API와의 모든 HTTP 통신을 담당.

### 요구사항

- GET: 최신 데이터 읽기 (`/v3/b/{BIN_ID}/latest`)
- PUT: 데이터 업데이트 (`/v3/b/{BIN_ID}`)
- 헤더: `X-Master-Key`, `Content-Type: application/json`
- 타임아웃: 15초
- 에러 핸들링: HTTP 상태 코드별 적절한 예외 처리
- 로컬 캐시: 마지막으로 성공한 GET 결과를 메모리에 보관 (jsonbin 장애 시 폴백)
- PUT 전 검증: meta.lastUpdated가 현재 시각(KST)으로 업데이트되었는지 확인

### 코드 구조

```python
class JsonBinClient:
    def __init__(self, bin_id: str, api_key: str):
        self.bin_id = bin_id
        self.api_key = api_key
        self.base_url = "https://api.jsonbin.io/v3/b"
        self._cache = None  # 마지막 성공 데이터
    
    def get_data(self) -> dict:
        """현재 여행 데이터를 가져온다"""
        ...
    
    def put_data(self, data: dict) -> bool:
        """여행 데이터를 업데이트한다"""
        ...
    
    def get_cached(self) -> Optional[dict]:
        """캐시된 데이터 반환 (jsonbin 장애 시)"""
        return self._cache
```

---

## 모듈 4: prompts.py (프롬프트 템플릿)

### 역할
Claude CLI에 전달할 시스템 프롬프트를 구성.

### 핵심 프롬프트

```python
SYSTEM_PROMPT_TEMPLATE = """너는 경주 가족여행 일정 관리 봇이야. 아래 JSON이 현재 여행 일정 데이터야.

[가족 정보]
- 인원: 아버지(당뇨 관리), 어머니(운전 담당), jojo, 아내, 히로(27개월, 밀/계란 알러지)
- 숙소: 까사멜로우(경북 경주시 북군4길 75)
- 특별 일정: 2/22(일) 대구마라톤 (jojo)
- 오늘 날짜: {today}
- 여행 {day_status}

[규칙]
1. 사용자 메시지를 분석해서 JSON에서 변경할 부분이 있는지 판단해.
2. 변경이 필요하면, 수정된 전체 JSON을 ```json 코드블록 안에 출력해.
3. 변경이 없고 조회/추천/대화만이면, 한국어로 간결하게 답변해. JSON은 출력하지 마.
4. 변경 시 반드시 meta.lastUpdated를 현재 시각(KST, ISO8601)으로, meta.updateNote를 변경 요약으로 업데이트해.
5. 식당 추천 시 아버지 당뇨(dad 필드)와 히로 알러지(hiro 필드)를 반드시 고려해.
6. 응답은 한국어로, 간결하고 친근하게.

[현재 데이터]
{json_data}

[사용자 메시지]
{user_message}"""


def build_prompt(json_data: dict, user_message: str) -> str:
    """최종 프롬프트 생성"""
    import json
    from datetime import datetime, timezone, timedelta
    
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst).strftime("%Y-%m-%d (%a)")
    
    # 여행 상태 판단
    trip_start = datetime(2026, 2, 19, tzinfo=kst)
    trip_end = datetime(2026, 2, 24, 23, 59, tzinfo=kst)
    now = datetime.now(kst)
    
    if now < trip_start:
        day_status = f"시작 전 (D-{(trip_start - now).days})"
    elif now > trip_end:
        day_status = "종료됨"
    else:
        day_num = (now - trip_start).days + 1
        day_status = f"Day {day_num} 진행 중"
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        today=today,
        day_status=day_status,
        json_data=json.dumps(json_data, ensure_ascii=False, indent=2),
        user_message=user_message
    )
```

---

## 모듈 5: webapp/index.html (가족 웹앱)

### 역할
가족 전원이 모바일로 보는 여행 가이드. jsonbin에서 데이터를 자동으로 가져와서 표시.

### 요구사항

- **단일 HTML 파일** (외부 의존성 최소화, CDN만 허용)
- 모바일 최적화 (viewport, 큰 글씨, 터치 친화)
- 한국어 UI
- 30초마다 jsonbin.io에서 자동 새로고침
- 마지막 업데이트 시각 표시
- 관리자 모드: PIN 4545 입력 시 수동 편집 가능

### UI 구성

1. **상단**: 여행 제목 + 현재 Day 표시 + 마지막 업데이트 시각
2. **날짜 탭**: Day 1 ~ Day 6 탭으로 전환
3. **일정 카드**: 각 항목을 카드로 표시
   - 상태 아이콘: ⬜ planned, ✅ done, ⏭️ skipped
   - 식사/카페: 선택지 목록 + 확정된 곳 강조
   - 아버지/히로 주의사항 배지 (⚠️ caution 표시)
   - 메모 표시
4. **하단**: 관리자 PIN 입력 버튼

### 디자인

- 배경: 따뜻한 크림/베이지 톤
- 카드: 흰색 + 가벼운 그림자
- 상태별 색상: planned(회색), done(초록), skipped(빨강 줄긋기)
- 폰트: 시스템 폰트 + 한국어 가독성 우선
- 아이콘: 이모지 활용 (외부 아이콘 라이브러리 불필요)

---

## 모듈 6: 기타 파일

### requirements.txt
```
python-telegram-bot>=20.0
requests>=2.28.0
python-dotenv>=1.0.0
```

### .env.example
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
JSONBIN_BIN_ID=698aa0ec43b1c97be973168e
JSONBIN_API_KEY=your_jsonbin_api_key_here
ALLOWED_USER_IDS=123456789
```

### gyeongju-bot.service (systemd)
```ini
[Unit]
Description=Gyeongju Travel Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gyeongju-bot
ExecStart=/usr/bin/python3 bot.py
Restart=on-failure
RestartSec=10
EnvironmentFile=/home/ubuntu/gyeongju-bot/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
