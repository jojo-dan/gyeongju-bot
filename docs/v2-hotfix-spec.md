# V2 핫픽스 기획서 — UI 피드백 5건

> 작성일: 2026-02-14
> 상태: **검토 요청 (오너)**
> 목표: 이번 턴에서 UI·구조 수정 완벽 마무리

---

## 전체 요약

| # | 이슈 | 페이지 | 난이도 | 변경 범위 |
|---|------|--------|--------|-----------|
| 1 | day-tabs와 콘텐츠 너비 불일치 | index.html | 낮음 | CSS 1줄 |
| 2 | 복합 장소 세분화 | index.html + guide.html | **높음** | JS 데이터 + 렌더링 |
| 3 | 서브탭/정렬바 너비 통일 | guide.html | 낮음 | CSS 1줄 |
| 4 | 카페 한 줄 설명 누락 | index.html | 낮음 | JS 1줄 |
| 5 | 포저 능력 설명 | 양쪽 HTML | 중간 | 채팅 웰컴 UI |

---

## Issue 1: day-tabs와 콘텐츠 너비 불일치

### 원인
이전 핫픽스에서 플로팅 버튼 겹침 해결을 위해 `.day-tabs`에 `padding-right: 110px`을 적용. 이로 인해 탭 유효 너비가 314px로 줄어들어 아래 콘텐츠(408px)와 정렬 불일치 발생.

### 해결
`padding-right: 110px` 대신 `overflow-x: auto`로 변경. 탭이 많으면 스크롤, 버튼 겹침은 `scroll-padding`으로 해결.

```css
/* 변경 전 */
.day-tabs {
  padding: 0 110px 0 16px;
}

/* 변경 후 */
.day-tabs {
  padding: 0 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.day-tabs::-webkit-scrollbar { display: none; }
```

현재 6개 탭이 440px 안에 충분히 들어가므로 스크롤이 발생하지 않고, 너비가 `.device`와 일치함.

---

## Issue 2: 복합 장소 세분화 (핵심 변경)

### 현재 문제
"대릉원(천마총), 첨성대"처럼 여러 장소가 하나의 item.title에 문자열로 결합되어 있음.
- 가이드 페이지: 통합 카드 1개로만 표시
- 일정 상세: 통합 place-detail 1개로만 표시

### 유저 요구
- **가이드**: 개별 장소가 각각 별도 카드로 보임
- **일정 상세**: 부모 카드("대릉원(천마총), 첨성대") 아래에 세부 장소 카드가 1개씩 나열

### 설계: `subPlaces` 배열 패턴

jsonbin 데이터 변경 없이 **프론트엔드에서 하드코딩**하는 방식 채택 (guide 데이터와 동일한 패턴).

#### 데이터 구조

`patchGuideData()` 함수에서 복합 장소를 감지하면 `subPlaces` 배열을 주입:

```javascript
// 복합 장소: "대릉원(천마총), 첨성대" → 2개 subPlace
{
  title: "대릉원(천마총), 첨성대",  // 기존 그대로
  guide: { ... },  // 기존 통합 guide (호환성 유지)
  subPlaces: [  // ← 새로 주입
    {
      name: "대릉원(천마총)",
      subtitle: "신라 왕릉 23기 거대 고분군 · 유모차 산책 코스",
      guide: {
        mustDo: ["천마총 내부 관람 (15분)", "고분 사이 산책 · 목련 포토존"],
        babyTips: { stroller: "전 구간 유모차 가능, 비탈 없음", ... },
        practicalInfo: { fee: "대릉원 무료 / 천마총 3,000원", hours: "09:00~22:00", ... }
      }
    },
    {
      name: "첨성대",
      subtitle: "동양 최고(最古) 천문대 · 국보 제31호",
      guide: {
        mustDo: ["1,300년 원형 유지 천문관측대 감상"],
        practicalInfo: { fee: "무료", hours: "상시 개방 (외부 관람)", ... }
      }
    }
  ]
}
```

#### 대상 복합 장소 (3건)

| item.title | subPlaces |
|---|---|
| 대릉원(천마총), 첨성대 | 대릉원(천마총), 첨성대 |
| 교촌마을 산책 | 교촌 한옥마을, 최씨고택/교촌법주, 경주빵 카페거리 |
| 동궁과 월지 야경 | 동궁과 월지(안압지) |

"동궁과 월지 야경"은 단일 장소이므로 subPlaces 없이 title만 정리.

#### index.html 렌더링 변경

`renderPlaceDetail()` 수정:

```javascript
function renderPlaceDetail(item) {
  if (isStayItem(item)) return renderStayDetail();

  // subPlaces가 있으면 각각 개별 카드로 렌더링
  if (item.subPlaces && item.subPlaces.length) {
    var html = '';
    item.subPlaces.forEach(function(sp) {
      html += renderSubPlaceCard(sp);
    });
    return html;
  }

  // 기존 단일 장소 렌더링
  var g = item.guide;
  if (!g) return '';
  return renderSinglePlaceDetail(item.title, g);
}

function renderSubPlaceCard(sp) {
  // 개별 subPlace를 place-detail 아코디언으로 렌더링
  var html = '<details class="place-detail">';
  html += '<summary>';
  html += '<div class="place-detail-top">';
  html += '<span class="place-detail-icon">📍</span>';
  html += '<span class="place-detail-name">' + escapeHtml(sp.name) + '</span>';
  html += '<div class="option-chevron">...</div>';
  html += '</div>';
  if (sp.subtitle) html += '<div class="place-detail-sub">' + escapeHtml(sp.subtitle) + '</div>';
  // ... tags, body (mustDo, babyTips, practicalInfo) ...
  html += '</summary>';
  html += '<div class="place-detail-body">...</div>';
  html += '</details>';
  return html;
}
```

#### guide.html 렌더링 변경

`renderPlaces()` 수정: `subPlaces`가 있는 item은 subPlaces 각각을 별도 카드로 렌더링.

```javascript
places.forEach(function(item) {
  if (item.subPlaces && item.subPlaces.length) {
    // 복합 장소: 각 subPlace를 별도 카드로
    item.subPlaces.forEach(function(sp, j) {
      html += renderSinglePlaceCard(sp, i + j);
    });
  } else {
    html += renderSinglePlaceCard({ name: item.title, subtitle: item.guide.subtitle, guide: item.guide }, i);
  }
});
```

### 주의사항
- jsonbin 데이터는 변경하지 않음 (기존 봇·API 호환성 유지)
- `patchGuideData()`에서 title 매칭으로 subPlaces 주입
- subPlaces가 없는 일반 장소는 기존 동작 그대로

---

## Issue 3: 서브탭/정렬바 너비 통일

### 원인
`.rest-sub-tab`에 `flex: 1`이 없어서 콘텐츠 크기만큼만 차지. `.sort-btn`은 `flex: 1`로 전체 너비를 균등 분할.

### 해결
`.rest-sub-tab`에 `flex: 1` 추가:

```css
.rest-sub-tab {
  flex: 1;          /* ← 추가 */
  text-align: center;  /* ← 추가 (중앙 정렬) */
  /* 나머지 기존 스타일 유지 */
}
```

---

## Issue 4: 카페 한 줄 설명 누락

### 원인
카페 옵션 데이터는 `menu` 필드가 아닌 `desc` 필드에 설명이 저장됨.
`renderOptionCard()`에서 `opt.menu`만 체크하므로 카페 설명이 표시되지 않음.

### 해결
`renderOptionCard()`의 메타 행에서 `opt.desc`를 fallback으로 사용:

```javascript
// 변경 전
if (opt.menu) html += '<span class="option-menu-brief">' + escapeHtml(opt.menu) + '</span>';

// 변경 후
var brief = opt.menu || opt.desc || '';
if (brief) html += '<span class="option-menu-brief">' + escapeHtml(brief) + '</span>';
```

동일한 패턴을 `renderSimpleOption()`에도 적용.

---

## Issue 5: 포저 능력 설명

### 포저가 할 수 있는 것 (13개 도구 기반)

**읽기 (5개 도구)**
- 특정 일차 일정 조회 (`get_schedule`)
- 이름/키워드로 항목 검색 (`find_item`)
- 조건 필터 검색: 카테고리, 아빠 당뇨, 히로 알러지, 상태 (`search_items`)
- 항목 상세 조회 (`get_item_detail`)
- 여행 전체 통계 (`get_trip_summary`)

**쓰기 (7개 도구)**
- 일정 상태 변경: planned → done / skipped (`update_status`)
- 식당 확정 (`set_chosen`)
- 메모 추가/수정 (`update_note`)
- 옵션 정보 수정: 메뉴, 영업시간, 주소, 전화, 좌표 등 (`update_option`)
- 새 일정 추가 (`add_item`)
- 기존 항목에 옵션 추가 (`add_option`)
- 항목 다른 날로 이동 (`move_item`)

**삭제 (1개)**
- 항목 삭제 (`remove_item`)

### 포저가 할 수 없는 것
- 실시간 날씨/교통 정보 조회 (외부 API 없음)
- 예약 대행 (전화/웹 예약 불가)
- 사진 촬영/공유
- 실시간 위치 추적 (웹앱의 위치 기능과 별개)
- 다른 사람에게 메시지 전송 (텔레그램 봇은 허용된 유저만)
- 숙소/식당 직접 예약 또는 결제

### UI 반영: 채팅 웰컴 화면 개선

현재 웰컴 화면의 힌트 칩을 포저 능력 중심으로 재구성:

```html
<div class="chat-welcome">
  <div class="chat-welcome-icon">🧭</div>
  <div class="chat-welcome-title">포저 — AI 여행 보좌관</div>
  <div class="chat-welcome-desc">
    일정 확인 · 식당 추천 · 일정 변경까지<br>
    경주 여행의 모든 것을 도와드려요.
  </div>
  <div class="chat-welcome-section">이런 걸 물어보세요</div>
  <div class="chat-welcome-hints">
    <div class="chat-hint-chip" onclick="chatHint('내일 일정 알려줘')">일정 확인</div>
    <div class="chat-hint-chip" onclick="chatHint('아빠가 먹을 수 있는 식당 찾아줘')">식당 추천</div>
    <div class="chat-hint-chip" onclick="chatHint('저녁 식사를 온목당으로 확정해줘')">식당 확정</div>
    <div class="chat-hint-chip" onclick="chatHint('교촌마을 일정을 3일차로 옮겨줘')">일정 이동</div>
  </div>
  <div class="chat-welcome-caveat">
    ※ 실시간 날씨·교통, 예약 대행은 지원하지 않습니다.
  </div>
</div>
```

CSS 추가:
```css
.chat-welcome-section {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 20px;
  margin-bottom: 8px;
}
.chat-welcome-caveat {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 16px;
  line-height: 1.5;
}
```

---

## 구현 순서

```
Phase 1 (즉시 — CSS/JS 소수정)
  ├── [1] day-tabs 너비 수정 (CSS)
  ├── [3] 서브탭 flex:1 (CSS)
  └── [4] 카페 desc fallback (JS 1줄)

Phase 2 (복합 장소)
  ├── [2] patchGuideData()에 subPlaces 주입 (index.html)
  ├── [2] renderPlaceDetail() 분기 (index.html)
  ├── [2] renderPlaces() subPlaces 분기 (guide.html)
  └── [2] subPlaces 데이터 작성 (3개 복합 장소)

Phase 3 (채팅 웰컴)
  └── [5] 채팅 웰컴 화면 업데이트 (양쪽 HTML)
```

---

## 변경 파일 요약

| 파일 | Issue | 변경 |
|---|---|---|
| `webapp/index.html` | 1, 2, 4, 5 | day-tabs CSS, subPlaces 렌더링, 카페 desc, 챗 웰컴 |
| `webapp/guide.html` | 2, 3, 5 | subPlaces 렌더링, card-sub padding, 서브탭 flex, 챗 웰컴 |

---

## 리스크

| 리스크 | 대응 |
|---|---|
| subPlaces 데이터가 실제 일정 데이터와 불일치 | title 매칭 기반이므로 일정 데이터 변경 시에도 동작. 매칭 실패 시 기존 통합 guide 표시 |
| 가이드 장소 수 증가로 스크롤 길어짐 | 카드가 접혀있으므로 시각적 부담 적음 |
| 포저 능력 설명이 부정확할 가능성 | tool_definitions.py 기준으로 정확하게 기술 |
