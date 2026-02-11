# Architecture

## 아키텍처

```
jojo (텔레그램) → VPS 봇 (Python) → Anthropic API (Tool Use) → jsonbin.io PUT
                                                                    ↑
가족 웹앱 (HTML) ← jsonbin.io GET (30초 폴링) ←─────────────────────┘
```

## 핵심 데이터 흐름

1. jojo가 텔레그램에 메시지 전송
2. bot.py가 메시지 수신, 허용된 user ID 확인
3. jsonbin_client.py로 현재 JSON 데이터 GET
4. claude_api_handler.py가 Anthropic API(Tool Use) 호출
5. Tool Use 루프: 도구 실행 → 결과 반환 → 반복
6. 데이터 변경 시 jsonbin PUT, 조회 시 텍스트 응답

## 가족 정보

- 인원: 아버지(당뇨 관리), 어머니(운전 담당), jojo, 아내, 히로(27개월, 밀/계란 알러지)
- 숙소: 까사멜로우 (경주 북군동)
- 특별 일정: 2/22(일) 대구국제마라톤 풀코스 (jojo 참가)
- 여행 기간: 2026.02.19(목) ~ 02.24(화), 5박 6일

## 환경 변수 (.env)

```
TELEGRAM_BOT_TOKEN=        # @BotFather에서 발급
JSONBIN_BIN_ID=698aa0ec43b1c97be973168e
JSONBIN_API_KEY=           # jsonbin.io Master Key
ALLOWED_USER_IDS=          # 쉼표 구분, jojo의 Telegram user ID
ANTHROPIC_API_KEY=         # Anthropic API 키
```

## JSON 데이터 구조

```json
{
  "meta": { "lastUpdated": "...", "updateNote": "..." },
  "days": [
    {
      "date": "2026-02-19", "dow": "목", "dayNum": 1, "title": "출발 & 도착",
      "items": [
        {
          "id": "d1_dinner", "time": "18:00~", "cat": "meal", "title": "저녁 식사",
          "options": [{ "name": "반월성한우", "menu": "한우 구이", "dad": "good", "hiro": "caution", "hiroNote": "반찬 확인" }],
          "chosen": "", "status": "planned", "note": ""
        }
      ]
    }
  ],
  "reference": { "distances": [], "contacts": [], "shopping": [] }
}
```

- status 값: "planned" | "done" | "skipped"
- cat 값: "activity" | "meal" | "cafe"
- dad/hiro 값: "good" | "caution"

## 봇 명령어 예시

| 사용자 입력 | 동작 | JSON 변경 |
|---|---|---|
| "내일 점심 복길로 확정" | set_chosen | O |
| "대릉원 다녀왔어" | update_status = "done" | O |
| "오늘 일정 알려줘" | get_schedule | X (조회만) |

## 항목 ID 전체 목록

- Day 1: d1_move, d1_shop, d1_checkin, d1_dinner, d1_donggung
- Day 2: d2_daereungwon, d2_lunch, d2_gyochon, d2_cafe, d2_dinner, d2_donggung
- Day 3: d3_bulguksa, d3_lunch, d3_cafe, d3_dinner, d3_prep
- Day 4: d4_depart, d4_marathon, d4_family_wait, d4_dinner
- Day 5: d5_bomun, d5_lunch, d5_cafe, d5_donggungwon, d5_dinner
- Day 6: d6_checkout, d6_museum, d6_lunch, d6_return

## 소스 모듈 구조

```
src/
├── bot.py                 # 텔레그램 봇 엔트리포인트
├── claude_api_handler.py  # Anthropic API + Tool Use
├── claude_handler.py      # Claude CLI subprocess (레거시)
├── jsonbin_client.py      # jsonbin.io GET/PUT
├── prompts.py             # CLI 모드 프롬프트 템플릿
├── tool_definitions.py    # Tool Use 도구 정의 (13개)
└── tool_executor.py       # 도구 실행 로직
```
