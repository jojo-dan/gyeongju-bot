# 경주 가족여행 텔레그램 봇

## 프로젝트 요약

가족 경주 여행(2026.02.19~24) 일정을 관리하는 텔레그램 봇 + 웹앱.
jojo가 텔레그램으로 자연어 메시지를 보내면, VPS의 봇이 Claude CLI(headless mode)로 요청을 처리하고 jsonbin.io의 여행 데이터를 업데이트한다. 가족이 보는 웹앱은 jsonbin.io에서 자동으로 최신 데이터를 가져온다.

## 아키텍처

```
jojo (텔레그램) → VPS 봇 (Python) → claude -p (subprocess) → jsonbin.io PUT
                                                                    ↑
가족 웹앱 (HTML) ← jsonbin.io GET (30초 폴링) ←─────────────────────┘
```

## 기술 스택

- **Python 3.10+**: 메인 언어
- **python-telegram-bot v20+**: 텔레그램 봇 (async)
- **subprocess**: Claude CLI 호출 (`claude -p "..." --output-format text`)
- **requests**: jsonbin.io HTTP 통신
- **python-dotenv**: 환경 변수 (.env)
- **logging**: 표준 로깅 (print 사용 금지)

## 프로젝트 구조

```
gyeongju-bot/
├── CLAUDE.md              # 이 파일
├── bot.py                 # 텔레그램 봇 메인 (엔트리포인트)
├── claude_handler.py      # Claude CLI subprocess 래퍼
├── jsonbin_client.py      # jsonbin.io GET/PUT 클라이언트
├── prompts.py             # Claude 시스템 프롬프트 템플릿
├── webapp/
│   └── index.html         # 가족용 모바일 웹앱 (단일 파일)
├── tests/
│   ├── test_claude_handler.py
│   ├── test_jsonbin_client.py
│   └── test_bot.py
├── requirements.txt
├── .env.example
├── gyeongju-bot.service   # systemd 서비스 파일
└── README.md
```

## 코딩 규칙

- 한국어 주석, 영어 코드 (변수명·함수명 영어)
- snake_case (함수, 변수), UPPER_SNAKE_CASE (상수)
- 네트워크 호출은 반드시 try/except + 타임아웃
- 모든 credential은 환경 변수로 관리 (.env)
- 코드에 API 키, 토큰 등 하드코딩 절대 금지
- 로깅은 logging 모듈 사용, 레벨: INFO 기본, 에러 시 ERROR
- 타입 힌트 사용 권장
- docstring 한국어로 작성

## 환경 변수 (.env)

```
TELEGRAM_BOT_TOKEN=        # @BotFather에서 발급
JSONBIN_BIN_ID=698aa0ec43b1c97be973168e
JSONBIN_API_KEY=           # jsonbin.io Master Key
ALLOWED_USER_IDS=          # 쉼표 구분, jojo의 Telegram user ID
```

## 핵심 데이터 흐름

1. jojo가 텔레그램에 메시지 전송 (예: "내일 점심 복길로 확정")
2. `bot.py`가 메시지 수신, 허용된 user ID인지 확인
3. `jsonbin_client.py`로 현재 JSON 데이터를 jsonbin.io에서 GET
4. `claude_handler.py`가 Claude CLI를 subprocess로 호출:
   - 시스템 프롬프트 (prompts.py) + 현재 JSON + 사용자 메시지
   - `claude -p "{전체 프롬프트}" --output-format text`
5. Claude 응답 파싱:
   - ```json 코드블록이 있으면 → JSON 변경 → jsonbin PUT → "✅ 업데이트 완료"
   - 코드블록 없으면 → 조회/추천 응답 → 그대로 텔레그램 전송
6. 에러 시 → "⚠️ 처리 중 문제가 발생했어요" + 로그 기록

## 가족 정보 (프롬프트에 포함할 컨텍스트)

- **인원**: 아버지(당뇨 관리중), 어머니(운전 담당), jojo, 아내, 히로(27개월 아기, 밀/계란 알러지)
- **숙소**: 까사멜로우 (경주 북군동)
- **특별 일정**: 2/22(일) 대구국제마라톤 풀코스 (jojo 참가)
- **여행 기간**: 2026.02.19(목) ~ 02.24(화), 5박 6일

## JSON 데이터 구조

```json
{
  "meta": {
    "lastUpdated": "2026-02-10T09:00:00+09:00",
    "updateNote": "초기 데이터"
  },
  "days": [
    {
      "date": "2026-02-19",
      "dow": "목",
      "dayNum": 1,
      "title": "출발 & 도착",
      "items": [
        {
          "id": "d1_dinner",
          "time": "18:00~",
          "cat": "meal",
          "title": "저녁 식사",
          "options": [
            {
              "name": "반월성한우",
              "menu": "한우 구이",
              "dad": "good",
              "hiro": "caution",
              "hiroNote": "반찬 확인"
            }
          ],
          "chosen": "",
          "status": "planned",
          "note": ""
        }
      ]
    }
  ],
  "reference": {
    "distances": [],
    "contacts": [],
    "shopping": []
  }
}
```

### status 값: "planned" | "done" | "skipped"
### cat 값: "activity" | "meal" | "cafe"
### dad/hiro 값: "good" | "caution"

## 봇 명령어 예시

| 사용자 입력 | 동작 | JSON 변경 |
|---|---|---|
| "내일 점심 복길로 확정" | d2_lunch.chosen = "복길" | ✅ |
| "대릉원 다녀왔어" | d2_daereungwon.status = "done" | ✅ |
| "교촌마을 패스" | d2_gyochon.status = "skipped" | ✅ |
| "불국사 주차 무료였어" | d3_bulguksa.note += "주차 무료" | ✅ |
| "오늘 일정 알려줘" | 해당 날짜 items 요약 | ❌ (조회만) |
| "아버지한테 괜찮은 저녁?" | dad:"good" 옵션 추천 | ❌ (조회만) |

## 항목 ID 전체 목록

Day 1: d1_move, d1_shop, d1_checkin, d1_dinner, d1_donggung
Day 2: d2_daereungwon, d2_lunch, d2_gyochon, d2_cafe, d2_dinner, d2_donggung
Day 3: d3_bulguksa, d3_lunch, d3_cafe, d3_dinner, d3_prep
Day 4: d4_depart, d4_marathon, d4_family_wait, d4_dinner
Day 5: d5_bomun, d5_lunch, d5_cafe, d5_donggungwon, d5_dinner
Day 6: d6_checkout, d6_museum, d6_lunch, d6_return
