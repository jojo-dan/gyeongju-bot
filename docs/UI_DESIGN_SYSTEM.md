# UI/UX Design System — "경주의 시간"

> 2026-02-13 현행화. 이전 디자인(Hardware Skeuomorphism)은 전면 교체됨.

---

## 디자인 컨셉

**"경주의 시간"** — 프리미엄 트래블 저널 스타일.
고급 여행 잡지의 에디토리얼 톤을 모바일 웹앱에 구현한다.
따뜻하고 절제된 세리프 타이포그래피, 자연 색조, 섬세한 질감이 핵심.

---

## 타이포그래피

| 변수 | 폰트 | 용도 |
|---|---|---|
| `--serif` | Spectral, KoPub Batang, Georgia, serif | 제목, 카드 이름, 헤더 |
| `--system` (index) / `--body` (guide) | Spectral, KoPub Batang, Georgia, serif | 본문, 설명, 메모 |
| `--mono` | DM Mono, SF Mono, monospace | 라벨, 시간, 태그, 버튼, 상태 표시 |

### 폰트 로드

```html
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/earlyaccess/kopubbatang.css" rel="stylesheet">
```

### 굵기 가이드

- **Spectral**: 300(placeholder), 400(body), 500(label), 600(subtitle), 700(heading)
- **KoPub Batang**: 300(light), 400(regular), 700(bold) — 한글 세리프
- **DM Mono**: 400(label), 500(active label)

---

## 색상 팔레트

### Light Mode (기본)

| 변수 | 값 | 용도 |
|---|---|---|
| `--bg` | #FAF7F2 | 페이지 배경 (따뜻한 크림) |
| `--bg-warm` | #F3EDE4 | 카드 내부, 옵션 배경 |
| `--housing` / `--card` | #FFFFFF | 카드 배경 |
| `--display` / `--hero` | #3D2E1F | 디스플레이 카드, active 탭 (다크 브라운) |
| `--display-text` / `--hero-text` | #FAF7F2 | 디스플레이 위 텍스트 |
| `--accent` | #C45D3E | 테라코타 — 강조, 액센트 |
| `--accent-soft` | #E8896E | 밝은 테라코타 — 보조 강조 |
| `--accent-bg` | rgba(196,93,62,0.08) | 테라코타 배경 |
| `--sage` | #7B8F6B | 세이지 그린 — 확정/OK 상태 |
| `--sage-bg` | rgba(123,143,107,0.1) | 세이지 배경 |
| `--blue` | #4A6FA5 | 블루 — 정보/아이 관련 (guide) |
| `--text` | #2C2218 | 기본 텍스트 |
| `--text-mid` | #5C4F42 | 보조 텍스트 |
| `--text-light` | #8C7E72 | 경량 텍스트 |
| `--text-muted` | #A89E94 | 비활성 텍스트 |
| `--border` | rgba(60,46,31,0.1) | 기본 보더 |
| `--border-strong` | rgba(60,46,31,0.18) | 강조 보더 |

### Dark Mode

| 변수 | 값 | 비고 |
|---|---|---|
| `--bg` | #1A1714 | 따뜻한 다크 |
| `--bg-warm` | #242019 | |
| `--housing` / `--card` | #2C261F | |
| `--display` / `--hero` | #2C261F | |
| `--display-text` | #E8E0D6 | |
| `--accent` | #E8896E | 밝은 테라코타 (가독성) |
| `--accent-soft` | #C45D3E | |
| `--sage` | #9AB089 | 밝은 세이지 |
| `--text` | #E8E0D6 | |
| `--text-mid` | #B5AA9E | |
| `--text-light` | #8C7E72 | |
| `--text-muted` | #6B5F54 | |
| `--border` | rgba(250,247,242,0.08) | |
| `--border-strong` | rgba(250,247,242,0.15) | |

### 다크모드 적용 방식

```css
/* 수동 토글 */
[data-theme="dark"] { ... }

/* 시스템 자동 감지 */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { ... }
}
```

- localStorage `gj_theme` 키로 사용자 선택 지속
- 해/달 SVG 아이콘 토글 버튼 (우상단 고정)

---

## 레이아웃

| 값 | 용도 |
|---|---|
| `max-width: 440px` | 컨텐츠 최대 폭 |
| `padding: 0 16px` | 좌우 여백 |
| `--radius-device` / `--r-card`: 20px | 카드 라운드 |
| `--radius-display`: 14px | 내부 디스플레이 라운드 |
| `--radius-btn` / `--r-btn`: 12px | 버튼, 칩, 태그 라운드 |
| `--r-tag`: 6px | 작은 태그 라운드 (guide) |

---

## 컴포넌트 패턴

### 1. 디스플레이 카드 (index.html)
다크 브라운 배경 + 세리프 타이틀 + 장식 원형 오버레이.
day 진행률 미터 포함.

### 2. 아코디언 카드 (guide.html)
`<details>` 기반. 20px radius, summary에 이름/메타, body에 상세.
chevron SVG가 open 시 90도 회전.

### 3. 아이템 카드 (index.html)
흰 배경 카드 안에 일정 항목. 상태 dot, 시간, 카테고리 라벨, 세리프 타이틀.
내부에 옵션 리스트 포함.

### 4. Section Nav (guide.html)
sticky 가로 탭. DM Mono 대문자. active = hero 색 fill.

### 5. Day Tabs (index.html)
sticky 가로 탭, 개별 pill 형태. active = display 색 fill + 그림자.

### 6. 필터 칩 (계획)
DM Mono 11px 대문자, 12px radius, 아웃라인. active = display 색 fill.

### 7. 뱃지
`badge-dad-good`: sage 계열, `badge-dad-caution`: accent 계열
`badge-hiro-good`: blue 계열, `badge-hiro-caution`: accent 계열

### 8. 테마 토글
원형 36x36 fixed 버튼, 우상단. 해/달 SVG 아이콘.

---

## 질감 & 장식

- **Grain 텍스처**: `body::before` pseudo-element, SVG noise filter, `opacity:0.03`, `z-index:9999`
- **장식 원형**: 섹션 헤더에 반투명 원형 (accent 계열), `pointer-events:none`
- **Accent 라인**: 헤더 하단 40px x 2px 테라코타 라인 (`::after`)

---

## 애니메이션

- **Fade-up**: `opacity:0 → 1`, `translateY(12px → 0)`, stagger 40ms/item
- **Transition curve**: `cubic-bezier(0.4, 0, 0.2, 1)` 통일
- **Chevron 회전**: `transform: rotate(90deg)`, 0.2s
- **버튼 터치**: `transform: scale(0.9)` / `scale(0.97)`

---

## 파일 구조

| 파일 | 역할 |
|---|---|
| `webapp/index.html` | 일정 상세 (day tabs + item cards) |
| `webapp/guide.html` | 종합 가이드 (4개 섹션: 일정/장소/식당/숙소) |
| `webapp/guide-preview.html` | 디자인 프리뷰 (레거시, 정리 대상) |

---

## 변경 이력

| 날짜 | 변경 |
|---|---|
| 2026-02-13 | 전면 리디자인: "경주의 시간" 적용. Cormorant Garamond + Noto Serif KR → Spectral + KoPub바탕. 다크모드 추가. |
| 이전 | Hardware Skeuomorphism (Braun/Dieter Rams 스타일) — 폐기 |
