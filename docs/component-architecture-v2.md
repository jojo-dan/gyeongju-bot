# Component Architecture v2 — 경주봇 웹앱 리뉴얼

> 2026-02-15 작성. 새 에디토리얼 디자인 적용을 위한 컴포넌트 아키텍처 설계.

---

## 1. 기술 스택 결정

### 빌드 도구: 빌드리스 유지 (권장)

| 항목 | 결정 | 근거 |
|---|---|---|
| 빌드 도구 | **없음 (현행 유지)** | Vercel 정적 배포 호환, 빠른 개발, 50~60대 부모님 대상 → 복잡도 최소화 |
| JS 모듈 | **`<script>` 인라인 유지** | ES module import는 CORS/Vercel 설정 이슈 가능성. 단일 파일이 배포·디버깅에 유리 |
| CSS 관리 | **CSS 변수 + 인라인 `<style>`** | 현행 다크모드·폰트사이즈 메커니즘 그대로 활용 |
| 폰트 | **Noto Serif KR + Noto Sans KR + Noto Sans Mono** | 새 디자인 .pen 명세 기준. 기존 Spectral/KoPub Batang/DM Mono에서 교체 |

**왜 빌드리스인가:**
- 여행일(2/19)까지 4일. Vite 도입 시 설정·배포 파이프라인 변경 리스크 불필요
- 현재 1,662줄 단일 파일이 잘 동작 중. 리뉴얼 후에도 2,000줄 이내 예상
- Vercel에서 `webapp/index.html` 정적 서빙 — 변경 불필요

### CSS 전략

```
기존 CSS 변수 시스템 유지 + 새 디자인 토큰 반영
├── :root { 새 색상/타이포/간격 토큰 }
├── [data-theme="dark"] { 다크모드 오버라이드 }
├── [data-fontsize="small|large"] { 폰트 크기 조절 }
└── 컴포넌트별 CSS 블록 (BEM-lite 네이밍)
```

### JS 패턴

```
현재: renderXxx() 함수가 HTML 문자열 반환 → innerHTML 주입
유지: 동일 패턴. 함수명과 구조만 새 컴포넌트 체계에 맞게 리팩토링
```

프레임워크 없이 Vanilla JS 함수형 렌더 패턴을 유지한다.
각 컴포넌트 = 순수 함수 `(data) => htmlString`.

---

## 2. 컴포넌트 트리

```
App
├── ThemeToggle (고정, 우상단)
├── FontSizeToggle (고정, 우상단)
├── AppHeader
│   ├── title: "경주 가족여행"
│   ├── subtitle: 날짜 범위 / D-day
│   └── updateTime
│
├── SectionNav (sticky 4탭: 일정/장소/식당/숙소)
│
├── [tab=schedule]
│   ├── DayTabs (일차별 서브탭)
│   ├── DayHeroCard
│   │   ├── ContextHeader (시간대 dot + "일정" 라벨 | 진행률 indicator)
│   │   ├── SectionTitle (day 제목, Noto Serif KR 24px)
│   │   └── ProgressMeter (진행 바 + 틱)
│   └── ScheduleItemList
│       └── ScheduleItemCard (반복)
│           ├── ContextHeader (status dot + 시간 | 카테고리 뱃지)
│           ├── ItemTitle (제목, visited/skipped 상태)
│           ├── ItemDistance (위치 기반, 조건부)
│           ├── ReviewText (조건부)
│           ├── PlaceDetailAccordion (cat=activity, 조건부)
│           │   ├── PlaceHeader (이름 + 시간 + chevron)
│           │   ├── TagRow (유모차, 수유실 등)
│           │   ├── InfoTable (실용 정보)
│           │   └── MapLink
│           └── OptionList (cat=meal/cafe, 조건부)
│               └── RestaurantCard (축소형) 또는 SimpleOption
│                   ├── CardHeader (이름 + 점수 + 영업뱃지)
│                   ├── SubText (메뉴 요약)
│                   └── Chevron "상세보기"
│
├── [tab=places]
│   ├── SectionHero ("장소 가이드")
│   └── PlaceCardList
│       └── PlaceCard (반복, 아코디언)
│           ├── CardHeader (이름 + 방문뱃지 + chevron)
│           ├── SubText
│           ├── MustDoList
│           ├── BabyTipSection
│           ├── InfoTable
│           └── MapLink
│
├── [tab=restaurants]
│   ├── RestSubTabs (전체/식당/카페)
│   ├── SortBar (별점순/거리순)
│   ├── SectionHero ("식당 가이드")
│   └── RestaurantCardList
│       └── RestaurantCard (확장형, 아코디언)
│           ├── ContextHeader (조건부: 시간대 dot | 카테고리 뱃지)
│           ├── SectionTitle (이름, 20px bold)
│           ├── ScoreBadge (점수 16px + 영업뱃지)
│           ├── SubText (메뉴 요약)
│           ├── [open 시 확장]
│           │   ├── MenuTable (메뉴 3행: 이름 + 가격)
│           │   ├── InfoTable (영업시간, 위치, 가격대)
│           │   ├── TagRow (아빠OK, 히로OK 등)
│           │   └── MapLink
│           └── [closed 시]
│               └── Chevron "상세보기"
│
└── [tab=stay]
    ├── SectionHero ("숙소 안내")
    └── StayCardList
        ├── StayOverviewCard (기본정보 + 링크)
        ├── RoomInfoCard (객실 그리드)
        ├── KidsFacilityCard
        ├── PoolBBQCard
        ├── AmenityCard (카테고리별 태그)
        └── RulesCard
```

---

## 3. 각 컴포넌트 상세

### 3.1 Atomic 컴포넌트 (재사용 단위)

#### `ContextHeader`
- **역할**: 시간대 dot + 라벨 | 카테고리 뱃지. 카드 상단 컨텍스트 표시
- **데이터**: `{ dotColor, label, badgeText, badgeType }`
- **CSS**: `.ctx-header` (flex, space-between, align-center)
- **렌더**: `renderContextHeader(data) => string`

```js
function renderContextHeader(data) {
  var html = '<div class="ctx-header">';
  html += '<div class="ctx-header__left">';
  if (data.dotColor) html += '<span class="ctx-header__dot" style="background:' + data.dotColor + '"></span>';
  if (data.label) html += '<span class="ctx-header__label">' + esc(data.label) + '</span>';
  html += '</div>';
  if (data.badgeText) html += '<span class="ctx-header__badge ctx-header__badge--' + data.badgeType + '">' + esc(data.badgeText) + '</span>';
  html += '</div>';
  return html;
}
```

#### `SectionTitle`
- **역할**: 섹션 제목 (Noto Serif KR 24px bold)
- **데이터**: `{ text, sub? }`
- **CSS**: `.sec-title` (font-family: var(--serif), 24px, 700)
- **렌더**: `renderSectionTitle(text, sub?) => string`

#### `MenuTable`
- **역할**: 메뉴 이름 + 가격 테이블 (최대 3행)
- **데이터**: `menuDetail[]` — `{ item, price }`
- **CSS**: `.menu-table`, `.menu-table__row`, `.menu-table__name` (Noto Serif KR 14px), `.menu-table__price` (Noto Sans Mono 13px)
- **스타일**: 행 간 `#EEEEEE` / 다크모드 `var(--border)` 구분선
- **렌더**: `renderMenuTable(menuDetail) => string`

#### `InfoTable`
- **역할**: 라벨-값 수직 테이블 (영업시간, 위치, 전화 등)
- **데이터**: `entries[]` — `{ label, value }`
- **CSS**: `.info-table`, `.info-table__row`, `.info-table__label` (#999, 12px), `.info-table__value` (#111, 12px)
- **스타일**: vertical gap 8px
- **렌더**: `renderInfoTable(entries) => string`

#### `TagRow`
- **역할**: 태그 칩 가로 행
- **데이터**: `tags[]` — `{ text, type? }` (type: 'default' | 'baby' | 'dad' | 'hiro')
- **CSS**: `.tag-row` (flex, wrap, gap 6px), `.tag-row__chip` (padding 4px 10px, border #E5E5E5, text #555555)
- **렌더**: `renderTagRow(tags) => string`

#### `Badge`
- **역할**: 상태 뱃지 (영업중, 영업종료, 아빠OK 등)
- **데이터**: `{ text, type }` (type: 'open' | 'closed' | 'dad-good' | 'dad-caution' | 'hiro-good' | 'hiro-caution')
- **CSS**: `.badge--open` (border #1A8754), `.badge--closed`, `.badge--dad-good` (sage), `.badge--hiro-good` (blue)
- **렌더**: `renderBadge(text, type) => string`

#### `MapLink`
- **역할**: 지도 링크 (lucide map-pin 아이콘 + 텍스트)
- **데이터**: `{ url, text? }`
- **CSS**: `.map-link` (color #0066CC, flex, align-center, gap 4px)
- **렌더**: `renderMapLink(url, text?) => string`

#### `Chevron`
- **역할**: 아코디언 열기/닫기 화살표
- **CSS**: `.chevron` (transition rotate 90deg on `[open]`)
- **렌더**: `renderChevron() => string`

---

### 3.2 Compound 컴포넌트

#### `RestaurantCard` (확장형 — restaurants 탭)
- **역할**: 식당 전체 정보 카드 (아코디언)
- **구성**: `<details class="rest-card">` 안에 atomic 조합
- **데이터**: restaurant 객체 `{ name, rating, hours, menu, menuDetail[], priceRange, loc, dad, hiro, mapUrl, distKm, type, meals[] }`
- **CSS**: `.rest-card`, `.rest-card__summary`, `.rest-card__body`
- **렌더**: `renderRestaurantCard(restaurant, options?) => string`
- **Summary (축소)**: 이름(20px) + 점수 + 영업뱃지 → 서브텍스트 → chevron
- **Body (확장)**: MenuTable + InfoTable + TagRow + MapLink

```
┌─────────────────────────────────────┐
│ ContextHeader (시간대 | 카테고리)      │ ← 조건부 (schedule 내 사용 시)
├─────────────────────────────────────┤
│ 반월성한우            4.5  [영업중]   │ ← summary
│ 한우 구이 · 순두부                    │
│                        ▸ 상세보기    │
├ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┤
│ 한우 등심 1인분            54,000원   │ ← MenuTable
│ ────────────────────────────────── │
│ 한우 안심 1인분            62,000원   │
│ ────────────────────────────────── │
│ 순두부찌개                  9,000원   │
├─────────────────────────────────────┤
│ 영업시간  11:00~21:00               │ ← InfoTable
│ 위치     황남동                      │
│ 가격대   1인 35,000~                │
├─────────────────────────────────────┤
│ [아빠 OK]  [히로 주의 · 반찬 확인]     │ ← TagRow (badges)
├─────────────────────────────────────┤
│ 📍 지도에서 보기                      │ ← MapLink
└─────────────────────────────────────┘
```

#### `RestaurantCard` (축소형 — schedule 내)
- **역할**: 일정 내 식당 옵션 (아코디언)
- **구성**: OptionCard와 동일 구조, RestaurantCard의 경량 버전
- **데이터**: option 객체 `{ name, rating, menu, hours, mapUrl, dad, hiro }`
- **CSS**: `.opt-card` (기존 `.option-card` 대체)
- **렌더**: `renderOptionCard(opt, item) => string`

#### `PlaceCard`
- **역할**: 장소 상세 카드 (아코디언)
- **구성**: CardHeader + SubText + MustDoList + BabyTipSection + InfoTable + MapLink
- **데이터**: place 객체 `{ name, subtitle, guide: { mustDo[], babyTips, practicalInfo } }`
- **CSS**: `.place-card`, `.place-card__summary`, `.place-card__body`
- **렌더**: `renderPlaceCard(place, index, days) => string`

#### `ScheduleItemCard`
- **역할**: 일정 항목 카드
- **구성**: ContextHeader + ItemTitle + Distance + ReviewText + PlaceDetailAccordion/OptionList
- **데이터**: item 객체 `{ id, time, cat, title, status, visited, options[], guide, note }`
- **CSS**: `.sched-item`, `.sched-item--visited`, `.sched-item--skipped`
- **렌더**: `renderScheduleItemCard(item) => string`

#### `DayHeroCard`
- **역할**: 일차별 디스플레이 카드 (다크 배경)
- **구성**: ContextHeader + SectionTitle + ProgressMeter
- **데이터**: day 객체 `{ dayNum, title, items[] }`
- **CSS**: `.day-hero` (기존 `.display-card` 대체)
- **렌더**: `renderDayHeroCard(day) => string`

#### `SectionHero`
- **역할**: 탭별 상단 히어로 블록
- **데이터**: `{ label, title, subtitle }`
- **CSS**: `.sec-hero` (기존 `.section-hero` 대체)
- **렌더**: `renderSectionHero(label, title, subtitle) => string`

#### `AltSection`
- **역할**: 대안 옵션 (제목 + dash + 설명 + 태그)
- **데이터**: `{ title, desc, tags[] }`
- **CSS**: `.alt-section`, `.alt-section__title`, `.alt-section__desc`
- **렌더**: `renderAltSection(data) => string`

---

### 3.3 Page-Level 컴포넌트

#### `ScheduleTab`
- **렌더**: `renderScheduleTab() => void` (innerHTML 주입)
- **구성**: DayHeroCard + ScheduleItemCard[]

#### `PlacesTab`
- **렌더**: `renderPlacesTab(days) => string`
- **구성**: SectionHero + PlaceCard[]

#### `RestaurantsTab`
- **렌더**: `renderRestaurantsTab(days) => string`
- **구성**: SectionHero + RestaurantCard[]

#### `StayTab`
- **렌더**: `renderStayTab() => string`
- **구성**: SectionHero + StayOverviewCard + RoomInfoCard + ...

---

## 4. 파일 구조 제안

### 권장: 단일 파일 유지

```
webapp/
├── index.html          ← 리뉴얼 대상 (전체 CSS + JS + HTML)
├── guide.html          ← 별도 페이지 (현행 유지, 추후 통합 고려)
├── guide-preview.html  ← 레거시 (삭제 대상)
└── og-image.png
```

**근거:**
- 빌드 도구 없이 분리하면 `<link>`, `<script src>` 추가 필요 → 로딩 순서 관리 복잡
- 1,662줄 → 리뉴얼 후 ~2,000줄 예상. 단일 파일로 충분히 관리 가능
- Ctrl+F로 전체 검색, 배포 단위 단순

### 파일 내부 구조 (코드 섹션 순서)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <!-- 메타, OG, 폰트 로드 -->
  <style>
    /* ═══ DESIGN TOKENS ═══ */
    /* :root 변수, 다크모드, 폰트사이즈 */

    /* ═══ RESET & BASE ═══ */
    /* 리셋, body, grain 텍스처 */

    /* ═══ LAYOUT ═══ */
    /* container, header, section-nav, sticky tabs */

    /* ═══ ATOMIC COMPONENTS ═══ */
    /* ctx-header, sec-title, menu-table, info-table,
       tag-row, badge, map-link, chevron */

    /* ═══ COMPOUND COMPONENTS ═══ */
    /* day-hero, sched-item, rest-card, opt-card,
       place-card, sec-hero, alt-section */

    /* ═══ PAGE COMPONENTS ═══ */
    /* stay-*, location-banner, toast, loading */

    /* ═══ UTILITIES ═══ */
    /* fade-up, visited, skipped, spinner */
  </style>
</head>
<body>
  <!-- 고정 UI: theme toggle, font size toggle -->
  <!-- AppHeader -->
  <!-- SectionNav -->
  <!-- DayTabs -->
  <!-- RestSubTabs -->
  <!-- ContentArea -->
  <!-- Toast -->

  <script>
    // ═══ THEME & FONT SIZE ═══
    // ═══ UTILS (esc, format, distance) ═══
    // ═══ STATIC DATA (STAY_DATA, PLACE_COORDS) ═══
    // ═══ ATOMIC RENDERERS ═══
    // ═══ COMPOUND RENDERERS ═══
    // ═══ PAGE RENDERERS ═══
    // ═══ TAB NAVIGATION ═══
    // ═══ DATA FETCH & INIT ═══
    // ═══ LOCATION ═══
  </script>
</body>
</html>
```

---

## 5. 기존 함수 매핑

| 기존 함수 | 새 함수 | 변경 사항 |
|---|---|---|
| `renderDayContent()` | `renderScheduleTab()` | DayHeroCard + ScheduleItemCard 조합으로 분해 |
| `renderItemCard(item)` | `renderScheduleItemCard(item)` | ContextHeader + ItemTitle 등 atomic 조합 |
| `renderPlaceDetail(item)` | `renderPlaceDetailAccordion(item)` | PlaceCard atomic 재사용 |
| `renderSinglePlaceCardInline(n,s,g)` | `renderPlaceCardInline(place)` | InfoTable + TagRow atomic 재사용 |
| `renderStayDetailInline()` | `renderStayCardInline()` | InfoTable atomic 재사용 |
| `renderOptionCard(opt,item)` | `renderOptionCard(opt,item)` | MenuTable + InfoTable + Badge atomic 조합 |
| `renderSimpleOption(opt,item)` | `renderSimpleOption(opt,item)` | 변경 최소 |
| `renderPlaces(days)` | `renderPlacesTab(days)` | SectionHero + PlaceCard 조합 |
| `renderGuidePlace(sp,idx,days)` | `renderPlaceCard(place,idx,days)` | atomic 조합으로 리팩토링 |
| `renderRestaurants(days)` | `renderRestaurantsTab(days)` | SectionHero + RestaurantCard 조합 |
| `renderRestCards(list,days)` | `renderRestaurantCardList(list,days)` | RestaurantCard(확장형) 사용 |
| `renderStay()` | `renderStayTab()` | SectionHero + 서브카드 조합 |
| `buildBadges(opt)` | `renderBadges(opt)` | Badge atomic 재사용 |
| `extractRestaurants(days)` | `extractRestaurants(days)` | 로직 변경 없음 |
| `sortRestaurants(list)` | `sortRestaurants(list)` | 로직 변경 없음 |
| `patchGuideData(days)` | `patchGuideData(days)` | 로직 변경 없음 |

### 신규 함수

| 함수 | 역할 |
|---|---|
| `renderContextHeader(data)` | 시간대 dot + 라벨 + 뱃지 |
| `renderSectionTitle(text, sub)` | 세리프 섹션 제목 |
| `renderMenuTable(menuDetail)` | 메뉴 테이블 |
| `renderInfoTable(entries)` | 라벨-값 정보 테이블 |
| `renderTagRow(tags)` | 태그 칩 행 |
| `renderBadge(text, type)` | 단일 뱃지 |
| `renderMapLink(url, text)` | 지도 링크 |
| `renderChevron()` | 아코디언 화살표 |
| `renderDayHeroCard(day)` | 일차 디스플레이 카드 |
| `renderSectionHero(label, title, sub)` | 탭 히어로 블록 |
| `renderAltSection(data)` | 대안 옵션 섹션 |

---

## 6. 다크 모드 / 접근성 전략

### 다크 모드

**현행 메커니즘 100% 유지:**

```css
/* 수동 토글 */
[data-theme="dark"] { --bg: ...; --card: ...; ... }

/* 시스템 자동 감지 (명시적 light 제외) */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { ... }
}
```

- `localStorage('gj_theme')` 키로 사용자 선택 지속
- 해/달 SVG 아이콘 토글 (우상단 고정)
- 새 디자인 토큰은 light/dark 양쪽 모두 정의

### 폰트 크기

**현행 메커니즘 100% 유지:**

```css
:root[data-fontsize="small"]  { --base-font: 14px; --delta: -2px; }
:root                          { --base-font: 16px; --delta: 0px; }  /* 기본 */
:root[data-fontsize="large"]  { --base-font: 18px; --delta: 2px; }
```

- 모든 본문 크기에 `calc(Npx + var(--delta, 0px))` 패턴 적용
- 50~60대 부모님 대상 → `large`가 기본값 (`initFontSize` 기본값 유지)

### 접근성

| 항목 | 전략 |
|---|---|
| 터치 타겟 | 최소 44x44px (현행 유지, 새 컴포넌트에도 적용) |
| 색상 대비 | WCAG AA 기준. 새 디자인 토큰에서 #999 라벨은 다크모드 시 밝기 보정 |
| aria-label | 테마 토글, 폰트 크기 버튼에 유지. 아코디언은 `<details>` 네이티브 접근성 활용 |
| 스크롤 | `-webkit-overflow-scrolling: touch` 유지 (iOS 관성 스크롤) |
| 키보드 | `<details>` + `<summary>` = 네이티브 키보드 지원 |
| 모션 | `prefers-reduced-motion` 미디어 쿼리 추가 고려 (fade-up 비활성화) |

### 새 디자인에서 달라지는 색상 매핑

새 디자인 명세(.pen)는 `#FFFFFF` 배경, `#111111` 텍스트, `#999999` 라벨 등 중립 색상을 사용한다.
이를 기존 CSS 변수 시스템으로 매핑:

| .pen 명세 | CSS 변수 매핑 | 비고 |
|---|---|---|
| `#FFFFFF` (배경) | `var(--card)` | 다크모드 시 자동 전환 |
| `#111111` (본문) | `var(--text)` | 다크모드 시 자동 전환 |
| `#999999` (라벨) | `var(--text-light)` | |
| `#555555` (태그 텍스트) | `var(--text-mid)` | |
| `#EEEEEE` (구분선) | `var(--border)` | |
| `#E5E5E5` (태그 보더) | `var(--border-strong)` | |
| `#1A8754` (영업중 보더) | `var(--sage)` | |
| `#0066CC` (지도 링크) | `var(--blue)` 또는 신규 `--link` | |

---

## 7. CSS 클래스 네이밍 컨벤션

### BEM-lite 채택

기존 코드의 `-` 기반 네이밍을 유지하되, 블록/엘리먼트 구분을 명확히 한다.

```
.block-name              ← Block (컴포넌트)
.block-name__element     ← Element (내부 요소)
.block-name--modifier    ← Modifier (변형)
```

### 네이밍 규칙

| 카테고리 | 접두사 | 예시 |
|---|---|---|
| Atomic 컴포넌트 | 짧은 약어 | `.ctx-header`, `.sec-title`, `.menu-table`, `.info-table`, `.tag-row`, `.badge`, `.map-link` |
| Compound 컴포넌트 | 기능 기반 | `.day-hero`, `.sched-item`, `.rest-card`, `.opt-card`, `.place-card`, `.sec-hero`, `.alt-section` |
| Page 레이아웃 | 기능 기반 | `.app-header`, `.section-nav`, `.day-tabs`, `.container` |
| 상태 | `--` modifier | `.sched-item--visited`, `.sched-item--skipped`, `.badge--open`, `.badge--closed` |
| 유틸리티 | 직관적 | `.fade-up`, `.visited`, `.loading`, `.spinner` |

### 기존 → 새 클래스 매핑 (주요)

| 기존 클래스 | 새 클래스 | 비고 |
|---|---|---|
| `.display-card` | `.day-hero` | 일차 디스플레이 |
| `.display-screen` | `.day-hero__screen` | |
| `.display-label` | `.ctx-header__label` | atomic 재사용 |
| `.item-card` | `.sched-item` | 일정 항목 |
| `.item-top-row` | `.ctx-header` | atomic 재사용 |
| `.item-title` | `.sched-item__title` | |
| `.card` (details) | `.rest-card` / `.place-card` | 용도별 분리 |
| `.card-top` | `.rest-card__header` / `.place-card__header` | |
| `.card-name` | `.rest-card__name` / `.place-card__name` | |
| `.card-body` | `.rest-card__body` / `.place-card__body` | |
| `.option-card` | `.opt-card` | 일정 내 옵션 |
| `.option-body` | `.opt-card__body` | |
| `.rest-rating` | `.rest-card__score` | |
| `.rest-info` | `.info-table__row` | atomic 재사용 |
| `.open-tag` | `.badge--open` / `.badge--closed` | |
| `.badge-dad-good` | `.badge--dad-good` | BEM modifier |
| `.section-hero` | `.sec-hero` | |
| `.section-label` | `.sec-hero__label` | |
| `.section-title` | `.sec-hero__title` | |
| `.place-detail` | `.place-card--inline` | 인라인 장소 상세 |
| `.info-grid` | `.info-table` | 이름 통일 |

---

## 부록 A. 데이터 흐름

```
fetchData() → /api/data → travelData (전역)
     │
     ├── render()
     │   ├── updateHeader()
     │   └── renderContent(activeTab)
     │       ├── 'schedule' → renderScheduleTab()
     │       │                  ├── renderDayHeroCard(day)
     │       │                  └── day.items.map(renderScheduleItemCard)
     │       │                       ├── renderContextHeader()
     │       │                       ├── renderPlaceDetailAccordion() [activity]
     │       │                       └── renderOptionCard() [meal/cafe]
     │       │                            ├── renderMenuTable()
     │       │                            ├── renderInfoTable()
     │       │                            └── renderBadges()
     │       ├── 'places'   → renderPlacesTab(days)
     │       │                  └── places.map(renderPlaceCard)
     │       ├── 'restaurants' → renderRestaurantsTab(days)
     │       │                    └── allRestaurants.map(renderRestaurantCard)
     │       └── 'stay'     → renderStayTab()
     │
     └── patchGuideData(days) — 하드코딩 장소 데이터 병합
```

## 부록 B. 마이그레이션 가이드라인

### 단계별 적용 전략

1. **Phase 1: 디자인 토큰 교체** — CSS 변수만 업데이트 (폰트, 색상, 간격)
2. **Phase 2: Atomic 컴포넌트 추가** — 새 함수 추가, 기존 함수에서 호출
3. **Phase 3: Compound 리팩토링** — 기존 renderXxx()를 새 구조로 교체
4. **Phase 4: 정리** — 미사용 CSS/함수 제거, 클래스명 통일

### 주의사항

- Phase 1~2는 기존 코드와 공존 가능 (점진적 교체)
- `<details>` 아코디언 패턴은 변경하지 않음 (접근성 + 간결성)
- `travelData` 전역 변수 구조는 변경하지 않음 (API 호환성)
- `patchGuideData()` 하드코딩 데이터는 현행 유지 (여행일 전 변경 리스크 최소화)
