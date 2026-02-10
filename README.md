# 경주 가족여행 텔레그램 봇

가족 경주 여행(2026.02.19~24) 일정을 관리하는 텔레그램 봇 + 웹앱.

텔레그램으로 자연어 메시지를 보내면, Claude CLI가 여행 일정 JSON을 자동 업데이트하고,
가족 웹앱에서 실시간으로 확인할 수 있습니다.

## 아키텍처

```
jojo (텔레그램) → VPS 봇 (Python) → claude -p (subprocess) → jsonbin.io PUT
                                                                    ↑
가족 웹앱 (HTML) ← jsonbin.io GET (30초 폴링) ←─────────────────────┘
```

## 필요 조건

- Python 3.10+
- Claude CLI 설치 및 인증 완료 (`claude` 명령어 사용 가능)
- 텔레그램 봇 토큰 (@BotFather에서 발급)
- jsonbin.io 계정 및 API 키

## 설치 방법

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd gyeongju-bot
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열고 아래 값을 입력:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
JSONBIN_BIN_ID=698aa0ec43b1c97be973168e
JSONBIN_API_KEY=your_jsonbin_api_key_here
ALLOWED_USER_IDS=123456789
```

| 변수 | 설명 |
|---|---|
| `TELEGRAM_BOT_TOKEN` | @BotFather에서 발급받은 봇 토큰 |
| `JSONBIN_BIN_ID` | jsonbin.io Bin ID |
| `JSONBIN_API_KEY` | jsonbin.io Master Key |
| `ALLOWED_USER_IDS` | 허용할 텔레그램 사용자 ID (쉼표 구분) |

## 실행 방법

### 직접 실행

```bash
python3 bot.py
```

### 테스트 실행

```bash
python3 -m unittest discover tests -v
```

## systemd 서비스 등록 (VPS 배포)

### 1. 서비스 파일 복사

```bash
sudo cp gyeongju-bot.service /etc/systemd/system/
```

### 2. 서비스 활성화 및 시작

```bash
sudo systemctl daemon-reload
sudo systemctl enable gyeongju-bot
sudo systemctl start gyeongju-bot
```

### 3. 상태 확인

```bash
sudo systemctl status gyeongju-bot
```

### 4. 로그 확인

```bash
sudo journalctl -u gyeongju-bot -f
```

### 5. 재시작

```bash
sudo systemctl restart gyeongju-bot
```

## 웹앱 배포

`webapp/index.html`은 단일 HTML 파일로, 정적 호스팅 서비스에 업로드하면 됩니다.

### GitHub Pages

1. `webapp/index.html`을 repository의 `docs/index.html`로 복사
2. GitHub Settings > Pages > Source를 `docs/` 폴더로 설정

### Netlify / Vercel

1. `webapp/` 폴더를 배포 디렉토리로 지정
2. 빌드 명령 없이 정적 파일 배포

### 직접 호스팅

웹 서버(nginx, Apache 등)에서 `webapp/index.html`을 서빙:

```nginx
server {
    listen 80;
    server_name travel.example.com;
    root /home/ubuntu/gyeongju-bot/webapp;
    index index.html;
}
```

## 봇 사용법

| 메시지 예시 | 동작 |
|---|---|
| "내일 점심 복길로 확정" | 일정 업데이트 |
| "대릉원 다녀왔어" | 상태를 done으로 변경 |
| "교촌마을 패스" | 상태를 skipped로 변경 |
| "오늘 일정 알려줘" | 오늘 일정 조회 |
| "아버지한테 괜찮은 저녁?" | 맞춤 추천 |

### 명령어

- `/start` - 인사 및 사용법 안내
- `/today` - 오늘 일정 요약

## 프로젝트 구조

```
gyeongju-bot/
├── CLAUDE.md              # 프로젝트 컨텍스트
├── PROJECT_SPEC.md        # 모듈별 상세 요구사항
├── bot.py                 # 텔레그램 봇 메인 (엔트리포인트)
├── claude_handler.py      # Claude CLI subprocess 래퍼
├── jsonbin_client.py      # jsonbin.io GET/PUT 클라이언트
├── prompts.py             # Claude 시스템 프롬프트 템플릿
├── webapp/
│   └── index.html         # 가족용 모바일 웹앱
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_claude_handler.py
│   └── test_jsonbin_client.py
├── requirements.txt
├── .env.example
├── gyeongju-bot.service   # systemd 서비스 파일
└── README.md
```
