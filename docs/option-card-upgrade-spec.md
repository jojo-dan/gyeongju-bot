# 일정 상세 식당 옵션 카드 업그레이드 기획서

> 상태: **DRAFT** — 오너 승인 대기
> 대상: `webapp/index.html`
> 참조: `webapp/guide.html` 식당 카드 디자인

---

## 1. 배경

index.html(일정 상세 보기)의 식당/카페 선택지(options)가 현재 이름+메뉴+뱃지만 표시한다.
guide.html에는 별점, 가격, 영업시간, 메뉴 상세, 지도 링크 등 풍부한 정보가 있는데,
같은 데이터 소스(`travelData.days[].items[].options[]`)를 쓰면서 index.html에서는 안 보인다.

**목표**: index.html의 식당 옵션을 guide.html 수준의 카드로 업그레이드하여,
일정 보면서 바로 상세 정보를 확인할 수 있게 한다.

---

## 2. 현재 vs 목표

### 현재 (index.html)

```html
<div class="option-item chosen">
  <span class="option-name">온목당</span>
  <span class="option-menu">— 곰탕, 냉수육</span>
  <span class="chosen-tag">확정</span>
  <div class="option-badges">
    <span class="badge badge-dad-good">아빠 OK</span>
    <span class="badge badge-hiro-good">히로 OK</span>
  </div>
</div>
```

표시 필드: name, menu, chosen 여부, dad/hiro badges, distance(조건부)

### 목표 (guide.html 스타일 아코디언)

```
┌──────────────────────────────────┐
│ 온목당              4.5  확정  ▸  │  ← summary (접힌 상태)
│ 곰탕, 냉수육 · 영업중 · 1.2km    │
├──────────────────────────────────┤
│ 곰탕               12,000원      │  ← body (펼친 상태)
│ 냉수육              25,000원     │
│ 가격대    12,000~25,000원        │
│ 영업시간  11:00-21:00            │
│ 위치      경주시 ...             │
│ [아빠 OK] [히로 OK]              │
│ 지도에서 보기 →                   │
└──────────────────────────────────┘
```

표시 필드: name, rating, menu, openStatus, distance, menuDetail[], priceRange, hours, loc, badges, mapUrl

---

## 3. 데이터 필드 매핑

options 배열의 각 항목에 이미 존재하는 enriched 필드:

| 필드 | 예시 | 용도 |
|---|---|---|
| `name` | "온목당" | 식당 이름 |
| `menu` | "곰탕, 냉수육" | 메뉴 간략 설명 |
| `rating` | 4.5 | 별점 (Google) |
| `ratingSource` | "Google" | 평점 출처 |
| `menuDetail[]` | `[{item:"곰탕",price:12000}]` | 메뉴 상세 + 가격 |
| `hours` | "11:00-21:00" | 영업시간 |
| `loc` | "경주시 황남동 ..." | 위치/주소 |
| `mapUrl` | "https://map.naver.com/..." | 지도 링크 |
| `dad` / `dadNote` | "good" / "" | 아빠 적합도 |
| `hiro` / `hiroNote` | "good" / "이유식 가능" | 히로 적합도 |
| `lat` / `lng` | 35.83 / 129.22 | GPS 좌표 (거리 계산용) |
| `priceRange` | "10,000~25,000원" | 가격대 (일부 옵션) |
| `category` | "Korean" | 카테고리 |

> 모든 옵션이 enriched는 아님. rating/menuDetail 등이 없는 옵션은 폴백 처리 필요.

---

## 4. HTML 구조 변경

### 변경 전: `<div class="option-item">`

### 변경 후: `<details class="option-card">`

```html
<details class="option-card [chosen]" [open]>
  <summary>
    <div class="option-top">
      <span class="option-name">온목당</span>
      <span class="option-rating">4.5</span>
      <span class="chosen-tag">확정</span>
      <div class="option-chevron">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </div>
    </div>
    <div class="option-meta">
      <span class="option-menu-brief">곰탕, 냉수육</span>
      <span class="open-tag open">영업중</span>
      <span class="option-dist">1.2km</span>
    </div>
  </summary>

  <div class="option-body">
    <!-- 메뉴 상세 (menuDetail이 있을 때) -->
    <div class="option-info">
      곰탕 <span>12,000원</span>
    </div>
    <div class="option-info">
      냉수육 <span>25,000원</span>
    </div>

    <!-- 가격대 -->
    <div class="option-info">
      <span class="option-info-label">가격대</span>10,000~25,000원
    </div>

    <!-- 영업시간 -->
    <div class="option-info">
      <span class="option-info-label">영업시간</span>11:00-21:00
    </div>

    <!-- 위치 -->
    <div class="option-info">
      <span class="option-info-label">위치</span>경주시 황남동...
    </div>

    <!-- 뱃지 -->
    <div class="option-badges">
      <span class="badge badge-dad-good">아빠 OK</span>
      <span class="badge badge-hiro-good">히로 OK</span>
    </div>

    <!-- 지도 링크 -->
    <a class="option-map-link" href="https://..." target="_blank">
      지도에서 보기
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
        <polyline points="15 3 21 3 21 9"/>
        <line x1="10" y1="14" x2="21" y2="3"/>
      </svg>
    </a>
  </div>
</details>
```

---

## 5. CSS 설계

### 새 클래스 (추가)

```css
/* ═══ OPTION CARD (Accordion) ═══ */
.option-card {
  border-radius: 14px;
  margin-bottom: 8px;
  background: var(--bg-warm);
  border: 1px solid transparent;
  overflow: hidden;
  transition: box-shadow 0.3s, border-color 0.3s;
}
.option-card[open] {
  border-color: var(--border);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.option-card.chosen {
  background: var(--sage-bg);
  border-color: rgba(123,143,107,0.25);
}

.option-card summary {
  padding: 12px 14px;
  cursor: pointer;
  list-style: none;
  -webkit-tap-highlight-color: transparent;
}
.option-card summary::-webkit-details-marker { display: none; }

/* 상단 행: 이름 + 별점 + 확정 + chevron */
.option-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.option-name {
  font-family: var(--serif);
  font-size: 16px;
  font-weight: 700;
  color: var(--item-text);
  flex: 1;
  min-width: 0;
}
.option-card.chosen .option-name {
  color: var(--sage);
}
.option-rating {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 500;
  color: var(--accent);
}
.chosen-tag {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--sage);
  letter-spacing: 0.3px;
}
.option-chevron {
  color: var(--text-muted);
  flex-shrink: 0;
  transition: transform 0.2s;
  display: flex;
}
.option-card[open] .option-chevron {
  transform: rotate(90deg);
}

/* 하단 메타: 메뉴 + 영업상태 + 거리 */
.option-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 13px;
  color: var(--item-text-dim);
}
.option-menu-brief {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.open-tag {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 6px;
  flex-shrink: 0;
}
.open-tag.open {
  background: var(--sage-bg);
  color: var(--sage);
}
.open-tag.closed {
  background: var(--accent-bg);
  color: var(--accent);
}
.option-dist {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* 펼침 영역 */
.option-body {
  padding: 0 14px 14px;
  border-top: 1px solid var(--border);
  margin-top: 0;
  padding-top: 12px;
}
.option-info {
  font-size: 13px;
  color: var(--item-text-mid);
  padding: 3px 0;
  display: flex;
  justify-content: space-between;
}
.option-info-label {
  font-weight: 600;
  color: var(--item-text-dim);
  margin-right: 8px;
  flex-shrink: 0;
}
.option-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 10px;
}
.option-map-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 500;
  color: var(--accent);
  text-decoration: none;
  margin-top: 10px;
  letter-spacing: 0.3px;
}
.option-map-link:active { opacity: 0.7; }
```

### 제거할 CSS

기존 `.option-item` 관련 클래스:
- `.option-item`, `.option-item.chosen`
- `.option-name` (새 버전으로 교체)
- `.option-menu`
- `.option-distance`, `.option-distance.nearby`

---

## 6. JS 변경

### 6-1. `parseOpenClosed()` 함수 포팅

guide.html에서 가져와야 할 함수:

```javascript
function parseOpenClosed(hours) {
  if (!hours) return null;
  // "11:00-21:00" 형식 파싱
  // 현재 시간(KST)과 비교하여 { status: 'open'|'closed', text: '영업중'|'영업종료' } 반환
  // guide.html의 기존 구현 참조
}
```

### 6-2. `renderItemCard()` 내 옵션 렌더링 교체

현재 코드 (index.html ~830-860줄):
```javascript
// 기존: option-item div 생성
html += `<div class="option-item${isChosen ? ' chosen' : ''}">`;
html += `<span class="option-name">${opt.name}</span>`;
// ...
```

변경:
```javascript
// 새: option-card details 생성
function renderOptionCard(opt, item) {
  const isChosen = item.chosen && item.chosen === opt.name;
  const hasRichData = opt.rating || opt.menuDetail || opt.hours || opt.mapUrl;

  // enriched 데이터가 없으면 폴백 (단순 표시)
  if (!hasRichData) {
    return renderSimpleOption(opt, item);
  }

  let html = `<details class="option-card${isChosen ? ' chosen' : ''}"${isChosen ? ' open' : ''}>`;
  html += '<summary>';

  // 상단: 이름 + 별점 + 확정 + chevron
  html += '<div class="option-top">';
  html += `<span class="option-name">${escapeHtml(opt.name)}</span>`;
  if (opt.rating) html += `<span class="option-rating">${opt.rating}</span>`;
  if (isChosen) html += '<span class="chosen-tag">확정</span>';
  html += '<div class="option-chevron"><svg ...></svg></div>';
  html += '</div>';

  // 메타: 메뉴 + 영업상태 + 거리
  html += '<div class="option-meta">';
  if (opt.menu) html += `<span class="option-menu-brief">${escapeHtml(opt.menu)}</span>`;
  if (opt.hours) {
    const oc = parseOpenClosed(opt.hours);
    if (oc) html += `<span class="open-tag ${oc.status}">${oc.text}</span>`;
  }
  if (userLat && opt.lat && opt.lng) {
    const km = haversineDistance(userLat, userLng, opt.lat, opt.lng);
    html += `<span class="option-dist">${km < 1 ? km.toFixed(1) : Math.round(km)}km</span>`;
  }
  html += '</div>';
  html += '</summary>';

  // 펼침 영역
  html += '<div class="option-body">';

  // 메뉴 상세
  if (opt.menuDetail && opt.menuDetail.length) {
    opt.menuDetail.forEach(m => {
      html += `<div class="option-info">${escapeHtml(m.item)}`;
      if (m.price) html += `<span>${Number(m.price).toLocaleString()}원</span>`;
      html += '</div>';
    });
  }

  // 가격대
  if (opt.priceRange) {
    html += `<div class="option-info"><span class="option-info-label">가격대</span>${escapeHtml(opt.priceRange)}</div>`;
  }

  // 영업시간
  if (opt.hours) {
    html += `<div class="option-info"><span class="option-info-label">영업시간</span>${escapeHtml(opt.hours)}</div>`;
  }

  // 위치
  if (opt.loc) {
    html += `<div class="option-info"><span class="option-info-label">위치</span>${escapeHtml(opt.loc)}</div>`;
  }

  // 뱃지
  const badges = [];
  if (opt.dad === 'good') badges.push('<span class="badge badge-dad-good">아빠 OK</span>');
  if (opt.dad === 'caution') badges.push(`<span class="badge badge-dad-caution">아빠 주의${opt.dadNote ? ' · '+escapeHtml(opt.dadNote) : ''}</span>`);
  if (opt.hiro === 'good') badges.push('<span class="badge badge-hiro-good">히로 OK</span>');
  if (opt.hiro === 'caution') badges.push(`<span class="badge badge-hiro-caution">히로 주의${opt.hiroNote ? ' · '+escapeHtml(opt.hiroNote) : ''}</span>`);
  if (badges.length) html += `<div class="option-badges">${badges.join('')}</div>`;

  // 지도 링크
  if (opt.mapUrl) {
    html += `<a class="option-map-link" href="${escapeAttr(opt.mapUrl)}" target="_blank">지도에서 보기 <svg ...></svg></a>`;
  }

  html += '</div></details>';
  return html;
}
```

### 6-3. 폴백: enriched 데이터 없는 옵션

```javascript
function renderSimpleOption(opt, item) {
  // 기존 option-item 스타일 유지 (간단 표시)
  const isChosen = item.chosen && item.chosen === opt.name;
  let html = `<div class="option-simple${isChosen ? ' chosen' : ''}">`;
  html += `<span class="option-name">${escapeHtml(opt.name)}</span>`;
  if (opt.menu) html += ` <span class="option-menu-brief" style="color:var(--item-text-dim);font-size:13px">— ${escapeHtml(opt.menu)}</span>`;
  if (isChosen) html += ' <span class="chosen-tag">확정</span>';
  // badges
  // ...
  html += '</div>';
  return html;
}
```

---

## 7. 엣지 케이스

| 케이스 | 처리 |
|---|---|
| enriched 데이터 없는 옵션 ("숙소에서 간단히" 등) | `renderSimpleOption()` 폴백, 아코디언 아님 |
| rating이 없는 옵션 | 별점 영역 숨김 |
| menuDetail이 없지만 menu는 있는 옵션 | menu만 meta에 표시, body에서 메뉴 상세 생략 |
| hours가 없는 옵션 | 영업상태 태그 숨김 |
| mapUrl이 없는 옵션 | 지도 링크 숨김 |
| 옵션이 1개뿐인 아이템 | 동일하게 아코디언 적용 (정보 확인용) |
| chosen 옵션 | 자동 `open`, sage 배경/테두리 강조 |
| 거리 정보 (위치 비활성) | distance 숨김 |
| `cat === 'activity'` 아이템의 옵션 | 식당이 아니므로 기존 처리 유지 (또는 별도 판단) |

---

## 8. 건드리지 않는 것

- item 카드 상위 구조 (display card, item-top-row, item-title 등)
- guide.html 코드 (별도 파일, 독립적)
- API 데이터 구조 (travelData 스키마 변경 없음)
- 거리/위치 관련 기존 로직 (haversineDistance, requestLocation 등)
- 다크모드 CSS 변수 (이미 적용됨, 새 클래스도 변수 사용)

---

## 9. 구현 순서

1. `parseOpenClosed()` 함수를 guide.html에서 index.html로 포팅
2. 새 CSS 추가 (`.option-card` 관련 전체)
3. 기존 `.option-item` CSS 정리/제거
4. `renderOptionCard()` + `renderSimpleOption()` 함수 작성
5. `renderItemCard()` 내 옵션 루프를 새 함수 호출로 교체
6. chosen 옵션 자동 open 동작 확인
7. 다크모드에서 카드 외관 확인
8. 각 day tab 순회하며 다양한 옵션 수 / enriched 여부 테스트

---

## 10. 변경 파일

| 파일 | 변경 |
|---|---|
| `webapp/index.html` | CSS 교체 (option-item → option-card), JS (renderOptionCard, parseOpenClosed 추가) |

---

## 11. 리스크

| 리스크 | 대응 |
|---|---|
| 중첩 `<details>` 터치 영역 | item 자체는 details가 아니므로 충돌 없음 |
| 카드 펼침 시 day 화면이 길어짐 | chosen만 auto-open, 나머지는 접힌 상태 |
| parseOpenClosed() KST 시간대 | `new Date()` 기본이 로컬 시간이므로 한국에서 사용 시 문제 없음 |
| 일부 옵션만 enriched | hasRichData 분기로 폴백 처리 |
