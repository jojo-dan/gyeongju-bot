# V2 기능 개선 종합 기획서

> 상태: **DRAFT** — 오너 승인 대기
> 작성: 2026-02-14 (를르슈 + 크라피카 + 히소카 + 유키)
> 대상: `webapp/index.html`, `webapp/guide.html`, 여행 데이터(jsonbin)

---

## 요구사항 요약

| # | 기능 | 대상 | 우선순위 | 난이도 |
|---|---|---|---|---|
| 1 | 홈플러스 데이터 리서치 & 추가 | 데이터 + guide | P0 | 낮음 |
| 2 | 활동 아이템에 장소 상세 카드 | index.html | P0 | 중간 |
| 3 | 가이드 페이지 일정 탭 제거 | guide.html | P0 | 낮음 |
| 4 | 가이드 장소에 홈플러스·소아과 추가 | guide.html + 데이터 | P0 | 낮음 |
| 5 | 식당/카페 분리 표시 | guide.html | P1 | 낮음 |
| 6 | 텍스트 크기 조절 | 양쪽 | P1 | 낮음 |
| 7 | 웹앱 내 챗봇 대화 | 양쪽 + 백엔드 | P2 | 높음 |

---

## Feature 1: 홈플러스 경주점 데이터

### 리서치 결과

**결론: 정상 영업 중. 2024년 4월 '메가푸드마켓'으로 새단장 완료.**

| 항목 | 내용 |
|---|---|
| 정식 명칭 | 홈플러스 메가푸드마켓 경주점 |
| 주소 | 경상북도 경주시 공단로 97 (용강동 800-11) |
| 전화 | 054-770-8000 |
| 영업시간 | 09:00~22:00 |
| 정기휴무 | 매월 둘째·넷째 일요일 |
| 2월 휴무일 | 2/8(일), **2/22(일)** ← 여행 4일차 |
| 주차 | 1층 고객주차장 + 2층 옥상주차장 (유료, 구매시 무료) |
| 아기시설 | 수유실 있을 가능성 높으나 미확인 (전화확인 권장) |
| 기타 | 단층 매장, 전기차 충전소, 수퍼윙스(키즈카페) 1층 입점 |
| 지도 | https://map.naver.com/p/search/홈플러스%20경주점 |

**⚠️ 2/22(일)은 정기 휴무일!** 여행 4일차에 해당하므로 장보기 일정에 주의 필요.

### 여행 데이터에 추가할 guide 정보

```json
{
  "guide": {
    "subtitle": "경주 유일의 대형 할인점 · 2024 메가푸드마켓 리뉴얼",
    "mustDo": [
      "BBQ 식재료·간식·음료 장보기",
      "아기 간식·이유식 재료 확보"
    ],
    "babyTips": {
      "stroller": "단층 매장이라 유모차 이동 편리",
      "nursingRoom": "매장 내 수유실 (전화확인: 054-770-8000)",
      "restSpots": ["수퍼윙스 키즈카페 (1층)"]
    },
    "practicalInfo": {
      "hours": "09:00~22:00",
      "parking": "1층 고객주차장 + 2층 옥상주차장 (유료, 구매시 무료)",
      "phone": "054-770-8000",
      "closedDays": "매월 둘째·넷째 일요일 (2월: 8일, 22일)",
      "address": "경상북도 경주시 공단로 97",
      "fromAccommodation": "까사멜로우에서 차량 약 15분"
    }
  }
}
```

### 실행

- 텔레그램 봇 Tool Use(`update_option` 또는 직접 jsonbin 수정)로 홈플러스 장보기 아이템에 guide 데이터 추가
- 좌표: 위도 35.8372, 경도 129.2081 (추정 — 정확한 좌표는 네이버 지도에서 확인 필요)

---

## Feature 2: 활동 아이템 장소 상세 카드

### 현황

현재 `index.html`의 `renderItemCard()`는 활동(activity) 아이템에 대해:
- 상태 점 + 시간 + 카테고리 라벨 + 제목 + 거리 + 옵션 목록 + 메모

를 보여준다. **`item.guide` 데이터가 존재해도 렌더링하지 않는다.**

### 목표

활동 아이템 카드 내부에 **장소 상세 아코디언**을 추가하여, 해당 장소의 가이드 정보(영업시간, 입장료, 주차, 아기팁 등)를 접었다 펼쳐서 볼 수 있게 한다.

3가지 유형:
1. **일반 장소** (홈플러스, 동궁과월지 등): `item.guide` 데이터 렌더링
2. **숙소** (체크인&정착): `STAY_DATA` 또는 별도 숙소 데이터 렌더링
3. **guide 없는 활동**: 상세 카드 미표시 (현재와 동일)

### HTML 구조

```html
<div class="item-card">
  <div class="item-display">
    <!-- 기존: 상태, 시간, 카테고리, 제목, 거리 -->

    <!-- NEW: 장소 상세 아코디언 -->
    <details class="place-detail">
      <summary>
        <div class="place-detail-top">
          <span class="place-detail-icon">📍</span>
          <span class="place-detail-name">홈플러스 경주점</span>
          <span class="place-detail-hours">09:00~22:00</span>
          <div class="option-chevron">▶</div>
        </div>
        <div class="place-detail-tags">
          <span class="place-tag">주차 가능</span>
          <span class="place-tag baby">유모차 OK</span>
        </div>
      </summary>
      <div class="place-detail-body">
        <!-- 필수 체험 -->
        <div class="place-must-do">
          <div class="place-body-label">꼭 할 것</div>
          <ul>
            <li>BBQ 식재료·간식·음료 장보기</li>
          </ul>
        </div>
        <!-- 아기 팁 -->
        <div class="place-baby-tips">
          <div class="place-body-label">아기 동반 팁</div>
          <div class="place-info-row">유모차: 단층 매장이라 이동 편리</div>
          <div class="place-info-row">수유실: 매장 내 수유실</div>
        </div>
        <!-- 실용 정보 -->
        <div class="place-practical">
          <div class="place-info-row"><span class="place-info-label">주소</span> 경상북도 경주시 공단로 97</div>
          <div class="place-info-row"><span class="place-info-label">영업시간</span> 09:00~22:00</div>
          <div class="place-info-row"><span class="place-info-label">전화</span> 054-770-8000</div>
          <div class="place-info-row"><span class="place-info-label">주차</span> 1층 + 옥상 주차장</div>
          <div class="place-info-row"><span class="place-info-label">휴무</span> 매월 둘째·넷째 일요일</div>
        </div>
        <!-- 지도 링크 -->
        <a class="option-map-link" href="..." target="_blank">지도에서 보기 ↗</a>
      </div>
    </details>

    <!-- 기존: 옵션 목록, 메모 -->
  </div>
</div>
```

### 숙소 타입 (체크인&정착)

체크인&정착 아이템은 `item.guide` 대신 숙소 정보를 표시한다.
판별 조건: `item.id`에 'checkin' 또는 'stay' 포함, 또는 `item.title`에 '체크인' 포함.

```html
<details class="place-detail stay-detail">
  <summary>
    <div class="place-detail-top">
      <span class="place-detail-icon">🏠</span>
      <span class="place-detail-name">까사멜로우</span>
      <span class="place-detail-hours">체크인 15:30</span>
      <div class="option-chevron">▶</div>
    </div>
  </summary>
  <div class="place-detail-body">
    <div class="place-info-row"><span class="place-info-label">주소</span> 경상북도 경주시 북군4길 75</div>
    <div class="place-info-row"><span class="place-info-label">전화</span> 010-3583-6648</div>
    <div class="place-info-row"><span class="place-info-label">체크인/아웃</span> 15:30 / 11:00</div>
    <div class="place-info-row"><span class="place-info-label">주차</span> 건물 외부 전용 주차장</div>
    <!-- 키즈 시설 하이라이트 -->
    <div class="place-body-label">키즈 시설</div>
    <ul>
      <li>실내 키즈룸 (미끄럼틀, 놀이기구)</li>
      <li>야외 모래 놀이터</li>
      <li>온수 풀 (약 70cm, 사계절)</li>
    </ul>
    <!-- 아기 용품 -->
    <div class="place-body-label">아기 용품</div>
    <div class="place-info-row">젖병소독기, 유아 어메니티, 키즈가구</div>
    <a class="option-map-link" href="https://map.naver.com/p/search/까사멜로우 경주" target="_blank">지도에서 보기 ↗</a>
  </div>
</details>
```

### CSS

```css
/* ═══ PLACE DETAIL (Activity Item 내부) ═══ */
.place-detail {
  border-radius: 14px;
  margin: 10px 0 8px;
  background: var(--bg-warm);
  border: 1px solid transparent;
  overflow: hidden;
  transition: box-shadow 0.3s, border-color 0.3s;
}
.place-detail[open] {
  border-color: var(--border);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.place-detail summary {
  padding: 12px 14px;
  cursor: pointer;
  list-style: none;
  -webkit-tap-highlight-color: transparent;
}
.place-detail summary::-webkit-details-marker { display: none; }

.place-detail-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.place-detail-icon { font-size: 14px; }
.place-detail-name {
  font-family: var(--serif);
  font-size: 15px;
  font-weight: 600;
  color: var(--item-text);
  flex: 1;
}
.place-detail-hours {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--text-muted);
}
.place-detail-tags {
  display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap;
}
.place-tag {
  font-family: var(--mono);
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--border);
  color: var(--text-mid);
}
.place-tag.baby { background: var(--accent-bg); color: var(--accent); }

.place-detail-body {
  padding: 0 14px 14px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}
.place-body-label {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  letter-spacing: 0.3px;
  margin: 12px 0 6px;
  text-transform: uppercase;
}
.place-body-label:first-child { margin-top: 0; }
.place-info-row {
  font-size: 13px;
  color: var(--item-text-mid);
  padding: 3px 0;
}
.place-info-label {
  font-weight: 600;
  color: var(--item-text-dim);
  margin-right: 8px;
}
.place-must-do ul, .place-baby-tips ul {
  margin: 0; padding-left: 16px;
  font-size: 13px; color: var(--item-text-mid);
  line-height: 1.7;
}
```

### JS 구현: `renderPlaceDetail(item)` 함수

```javascript
function renderPlaceDetail(item) {
  // 숙소 타입 체크
  if (isStayItem(item)) return renderStayDetail();

  var g = item.guide;
  if (!g) return '';

  var html = '<details class="place-detail">';
  html += '<summary>';
  html += '<div class="place-detail-top">';
  html += '<span class="place-detail-icon">📍</span>';
  html += '<span class="place-detail-name">';
  // 장소명: guide.subtitle이 있으면 그걸 사용, 없으면 item.title
  html += escapeHtml(g.subtitle || item.title);
  html += '</span>';

  // 영업시간 태그
  if (g.practicalInfo && g.practicalInfo.hours) {
    html += '<span class="place-detail-hours">' + escapeHtml(g.practicalInfo.hours) + '</span>';
  }
  html += '<div class="option-chevron"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M9 18l6-6-6-6"/></svg></div>';
  html += '</div>'; // place-detail-top

  // summary 태그들
  var tags = [];
  if (g.practicalInfo && g.practicalInfo.parking) tags.push('주차 가능');
  if (g.babyTips && g.babyTips.stroller) tags.push({text: '유모차 OK', cls: 'baby'});
  if (g.babyTips && g.babyTips.nursingRoom) tags.push({text: '수유실', cls: 'baby'});
  if (tags.length) {
    html += '<div class="place-detail-tags">';
    tags.forEach(function(t) {
      if (typeof t === 'string') html += '<span class="place-tag">' + t + '</span>';
      else html += '<span class="place-tag ' + t.cls + '">' + t.text + '</span>';
    });
    html += '</div>';
  }
  html += '</summary>';

  // body
  html += '<div class="place-detail-body">';

  // 필수 체험
  if (g.mustDo && g.mustDo.length) {
    html += '<div class="place-body-label">꼭 할 것</div><ul>';
    g.mustDo.forEach(function(m) { html += '<li>' + escapeHtml(m) + '</li>'; });
    html += '</ul>';
  }

  // 아기 팁
  if (g.babyTips) {
    html += '<div class="place-body-label">아기 동반 팁</div>';
    var bt = g.babyTips;
    if (bt.stroller) html += '<div class="place-info-row"><span class="place-info-label">유모차</span>' + escapeHtml(bt.stroller) + '</div>';
    if (bt.nursingRoom) html += '<div class="place-info-row"><span class="place-info-label">수유실</span>' + escapeHtml(bt.nursingRoom) + '</div>';
    if (bt.restroom) html += '<div class="place-info-row"><span class="place-info-label">화장실</span>' + escapeHtml(bt.restroom) + '</div>';
    if (bt.restSpots && bt.restSpots.length) {
      html += '<div class="place-info-row"><span class="place-info-label">쉴 곳</span>' + bt.restSpots.map(escapeHtml).join(', ') + '</div>';
    }
    if (bt.recommendedRoute) html += '<div class="place-info-row"><span class="place-info-label">추천 동선</span>' + escapeHtml(bt.recommendedRoute) + '</div>';
  }

  // 실용 정보
  if (g.practicalInfo) {
    html += '<div class="place-body-label">실용 정보</div>';
    var pi = g.practicalInfo;
    if (pi.address) html += '<div class="place-info-row"><span class="place-info-label">주소</span>' + escapeHtml(pi.address) + '</div>';
    if (pi.hours) html += '<div class="place-info-row"><span class="place-info-label">영업시간</span>' + escapeHtml(pi.hours) + '</div>';
    if (pi.fee) html += '<div class="place-info-row"><span class="place-info-label">입장료</span>' + escapeHtml(pi.fee) + '</div>';
    if (pi.phone) html += '<div class="place-info-row"><span class="place-info-label">전화</span>' + escapeHtml(pi.phone) + '</div>';
    if (pi.parking) html += '<div class="place-info-row"><span class="place-info-label">주차</span>' + escapeHtml(pi.parking) + '</div>';
    if (pi.timeNeeded) html += '<div class="place-info-row"><span class="place-info-label">소요시간</span>' + escapeHtml(pi.timeNeeded) + '</div>';
    if (pi.closedDays) html += '<div class="place-info-row"><span class="place-info-label">휴무</span>' + escapeHtml(pi.closedDays) + '</div>';
    if (pi.fromAccommodation) html += '<div class="place-info-row"><span class="place-info-label">숙소에서</span>' + escapeHtml(pi.fromAccommodation) + '</div>';
  }

  // 지도 링크 (guide.practicalInfo.mapUrl 또는 첫 번째 옵션의 mapUrl)
  var mapUrl = (g.practicalInfo && g.practicalInfo.mapUrl) || '';
  if (!mapUrl && item.options && item.options[0] && item.options[0].mapUrl) mapUrl = item.options[0].mapUrl;
  if (mapUrl) {
    html += '<a class="option-map-link" href="' + escapeAttr(mapUrl) + '" target="_blank">지도에서 보기 <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></a>';
  }

  html += '</div></details>';
  return html;
}

function isStayItem(item) {
  return item.title && (item.title.indexOf('체크인') !== -1 || item.title.indexOf('정착') !== -1);
}

function renderStayDetail() {
  // STAY_DATA를 index.html에도 임베드하거나, API 응답에 포함
  // guide.html의 STAY_DATA와 동일한 구조 사용
  var s = STAY_DATA; // 전역 변수로 정의 필요
  if (!s) return '';

  var html = '<details class="place-detail stay-detail">';
  html += '<summary>';
  html += '<div class="place-detail-top">';
  html += '<span class="place-detail-icon">🏠</span>';
  html += '<span class="place-detail-name">' + escapeHtml(s.name) + '</span>';
  html += '<span class="place-detail-hours">체크인 ' + escapeHtml(s.checkin) + '</span>';
  html += '<div class="option-chevron"><svg ...>...</svg></div>';
  html += '</div></summary>';

  html += '<div class="place-detail-body">';
  html += '<div class="place-info-row"><span class="place-info-label">주소</span>' + escapeHtml(s.address) + '</div>';
  html += '<div class="place-info-row"><span class="place-info-label">전화</span>' + escapeHtml(s.phone) + '</div>';
  html += '<div class="place-info-row"><span class="place-info-label">체크인/아웃</span>' + s.checkin + ' / ' + s.checkout + '</div>';
  html += '<div class="place-info-row"><span class="place-info-label">주차</span>' + escapeHtml(s.parking) + '</div>';

  // 키즈 시설 하이라이트
  if (s.kids && s.kids.length) {
    html += '<div class="place-body-label">키즈 시설</div><ul>';
    s.kids.forEach(function(k) { html += '<li>' + escapeHtml(k) + '</li>'; });
    html += '</ul>';
  }

  // 아기 용품
  if (s.amenities && s.amenities.baby && s.amenities.baby.length) {
    html += '<div class="place-body-label">아기 용품</div>';
    html += '<div class="place-info-row">' + s.amenities.baby.map(escapeHtml).join(', ') + '</div>';
  }

  // 풀장
  if (s.pool) {
    html += '<div class="place-body-label">풀장</div>';
    html += '<div class="place-info-row">' + escapeHtml(s.pool.note) + '</div>';
  }

  if (s.mapUrl) {
    html += '<a class="option-map-link" href="' + escapeAttr(s.mapUrl) + '" target="_blank">지도에서 보기 ↗</a>';
  }

  html += '</div></details>';
  return html;
}
```

### renderItemCard() 수정

```javascript
// 제목 바로 아래, 거리 행 위에 삽입
html += `<div class="item-title${titleClass}">${item.title}</div>`;

// ★ NEW: 장소 상세 카드
if (item.cat === 'activity') {
  html += renderPlaceDetail(item);
}

// 기존 거리 행
if (userLat && item.options ...
```

### STAY_DATA 공유

현재 `STAY_DATA`는 guide.html에만 하드코딩되어 있다. index.html에서도 사용하려면:

**방안 A (추천)**: index.html에도 동일한 `STAY_DATA` 객체를 복사 (중복이지만 단순)
**방안 B**: 별도 JS 파일(`webapp/stay-data.js`)로 분리 후 양쪽에서 `<script src>` 참조
**방안 C**: API 응답에 숙소 데이터 포함 (백엔드 변경 필요)

→ 단기적으로는 **방안 A**, 장기적으로 방안 B로 전환.

---

## Feature 3: 가이드 페이지 일정 탭 제거

### 변경 내용

1. **section-nav에서 '일정' 버튼 제거**
```html
<!-- Before -->
<div class="section-nav">
  <button class="section-nav-btn active" onclick="scrollToSection('overview')">일정</button>
  <button class="section-nav-btn" onclick="scrollToSection('places')">장소</button>
  <button class="section-nav-btn" onclick="scrollToSection('restaurants')">식당</button>
  <button class="section-nav-btn" onclick="scrollToSection('stay')">숙소</button>
</div>

<!-- After -->
<div class="section-nav">
  <button class="section-nav-btn active" onclick="scrollToSection('places')">장소</button>
  <button class="section-nav-btn" onclick="scrollToSection('restaurants')">식당</button>
  <button class="section-nav-btn" onclick="scrollToSection('stay')">숙소</button>
</div>
```

2. **`renderOverview()` 함수 호출 제거** (render() 함수에서)
```javascript
// Before
html += renderOverview(days);
html += renderPlaces(days);

// After
html += renderPlaces(days);
```

3. **`renderOverview()` 함수 코드는 유지** (dead code지만 추후 필요할 수 있으므로 주석 처리)

4. **`scrollToSection()` 함수에서 'overview' 케이스 제거** 또는 무시

5. **필터의 section nav 자동 활성화 로직 수정** (`applyFilters` 함수의 sectionIdx 매핑 변경)

### 영향

- section nav가 3탭으로 줄어들어 모바일에서 더 넉넉한 공간
- 첫 번째 active 탭이 '장소'가 됨

---

## Feature 4: 가이드 장소에 홈플러스·소아과 추가

### 사랑의소아청소년과 리서치 결과

| 항목 | 내용 |
|---|---|
| 정식 명칭 | 사랑의 소아과의원 |
| 주소 | 경상북도 경주시 황성로 59, 2층 (황성동) |
| 전화 | 054-773-7740 |
| 진료과목 | 소아청소년과, 내과, 안과, 이비인후과, 피부과 |
| 영업시간 | 평일 09:00~18:00 (추정), 토 09:00~13:00 (추정) |
| 일요/공휴 | 휴진 |
| 비대면 진료 | 일부 플랫폼에서 가능 |
| 지도 | https://naver.me/GJrFT2S7 |
| 비고 | 소아청소년과 전문의 1명 상주 |

### 구현 방법

현재 guide.html의 `renderPlaces()`는 `item.cat === 'activity' && item.guide`인 항목만 수집한다.
홈플러스와 소아과는 아래 두 가지 방법으로 추가 가능:

**방안 A (추천): 여행 데이터에 직접 추가**

홈플러스는 이미 일정에 있으므로 guide 데이터만 추가하면 자동으로 장소 섹션에 노출된다.
소아과는 '비상 연락처/의료' 성격이므로 별도의 activity 아이템으로 추가하거나, guide.html에 하드코딩한다.

**방안 B: guide.html에 하드코딩 장소 추가**

`renderPlaces()` 내에 하드코딩된 추가 장소 배열을 합쳐서 렌더링:

```javascript
// 여행 데이터 외 추가 장소
var extraPlaces = [
  {
    title: '사랑의 소아과의원',
    guide: {
      subtitle: '아이 아플 때 대비 — 소아청소년과 전문의',
      mustDo: ['방문 전 반드시 전화 확인 (임시 휴진 가능)'],
      babyTips: {},
      practicalInfo: {
        address: '경상북도 경주시 황성로 59, 2층',
        phone: '054-773-7740',
        hours: '평일 09:00~18:00 (추정), 토 09:00~13:00',
        closedDays: '일요일·공휴일 휴진'
      }
    }
  }
];
```

→ 소아과는 **방안 B**로 하드코딩 (일정 아이템이 아니므로), 홈플러스는 **방안 A**로 guide 데이터 추가.

### 추가 아이디어 (크라피카 제안)

장소 섹션을 **관광지 / 편의시설** 두 그룹으로 분류:
- 관광지: 불국사, 석굴암, 동궁과월지, 대릉원 등
- 편의시설: 홈플러스, 소아과

이렇게 하면 성격이 다른 장소가 자연스럽게 구분된다.
구현: 장소 카드에 `data-place-type="tourist|facility"` 속성 추가 후 서브헤더로 그룹핑.

---

## Feature 5: 식당/카페 분리 표시

### 현황

`extractRestaurants()`가 `cat === 'meal'`과 `cat === 'cafe'` 항목을 하나의 리스트로 합쳐서 '식당·카페 가이드' 섹션에 표시한다.

### 설계

**방안 A: 서브 탭 추가 (추천)**

식당 섹션 내부에 서브 탭(전체/식당/카페)을 추가한다.

```html
<div class="rest-sub-tabs">
  <button class="rest-sub-tab active" onclick="filterRestType('all')">전체 (23)</button>
  <button class="rest-sub-tab" onclick="filterRestType('meal')">식당 (15)</button>
  <button class="rest-sub-tab" onclick="filterRestType('cafe')">카페 (8)</button>
</div>
```

```css
.rest-sub-tabs {
  display: flex;
  gap: 6px;
  padding: 0 16px 12px;
  max-width: 440px;
  margin: 0 auto;
}
.rest-sub-tab {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 10px;
  border: 1.5px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}
.rest-sub-tab.active {
  background: var(--hero);
  color: var(--hero-text);
  border-color: var(--hero);
}
```

**방안 B: 별도 섹션 분리**

'식당 가이드'와 '카페 가이드'를 완전히 별도 섹션으로 분리. section-nav에도 '카페' 탭 추가.
→ 탭이 4개→5개로 늘어남. 모바일에서 살짝 빡빡하지만 가능.

### 추천: 방안 A

- section nav는 3탭(장소/식당/숙소) 유지 → Feature 3에서 일정을 제거했으므로 깔끔
- 식당 섹션 내부에서 서브 탭으로 전체/식당/카페 전환
- 기존 필터 칩(카페, 한식 등)과 자연스럽게 병합 가능
- 정렬(별점순/거리순)은 서브 탭과 독립적으로 동작

### 구현

1. `extractRestaurants()`에서 각 항목에 `type: 'meal' | 'cafe'` 필드 추가 (이미 `cat` 필드 보존 중)
2. 식당 카드에 `data-type="meal|cafe"` 속성 추가
3. 서브 탭 HTML + CSS 추가
4. `filterRestType(type)` JS 함수: `data-type` 기준으로 show/hide
5. 탭 카운트 동적 계산

```javascript
var restTypeFilter = 'all';

function filterRestType(type) {
  restTypeFilter = type;
  document.querySelectorAll('.rest-sub-tab').forEach(function(t) {
    t.classList.toggle('active', t.getAttribute('data-type') === type);
  });
  document.querySelectorAll('.card[data-section="restaurants"]').forEach(function(card) {
    if (type === 'all' || card.getAttribute('data-type') === type) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
  // 기존 필터와 조합
  applyFilters();
}
```

---

## Feature 6: 텍스트 크기 조절

### UX 설계 (크라피카)

- 고정 버튼 그룹: 테마 토글 옆에 A-/A+ 버튼 추가
- 3단계: 작게(14px) / 기본(16px) / 크게(18px)
- 버튼 1개로 순환: 기본 → 크게 → 작게 → 기본 ...
- localStorage에 저장하여 페이지 재방문 시 유지

### UI 설계 (히소카)

테마 토글(우상단 right:16px)과 검색 트리거(right:60px) 사이에 텍스트 크기 버튼 배치하면 3개가 줄줄이 놓여 복잡해진다.

**대안: 테마 토글 버튼 장 누르기(long press)로 텍스트 크기 순환**
→ 발견성이 낮다. 탈락.

**대안: 검색 트리거 옆에 배치**

```
[🔍 right:104px] [가 right:60px] [☀ right:16px]
```

→ 3개가 일렬로 정렬되어 나쁘지 않으나, 좀 빽빽함.

**추천: 통합 설정 패널**

테마 토글 버튼을 클릭하면 **설정 미니 패널**이 열려서, 다크모드 토글 + 텍스트 크기 조절이 함께 표시.

```html
<div class="settings-panel" id="settingsPanel">
  <div class="settings-row">
    <span class="settings-label">테마</span>
    <button class="settings-btn" onclick="toggleTheme()">
      <svg id="themeIcon">...</svg>
    </button>
  </div>
  <div class="settings-row">
    <span class="settings-label">글자 크기</span>
    <div class="font-size-group">
      <button class="font-size-btn" data-size="small" onclick="setFontSize('small')">가</button>
      <button class="font-size-btn active" data-size="medium" onclick="setFontSize('medium')">가</button>
      <button class="font-size-btn" data-size="large" onclick="setFontSize('large')">가</button>
    </div>
  </div>
</div>
```

그런데 이 방법은 기존 테마 토글 버튼의 의미가 바뀜. 너무 과하다.

**최종 추천: 독립 버튼 1개 (font-size 순환)**

```
[🔍 right:104px] [가 right:60px] [☀ right:16px]  ← guide.html
                  [가 right:60px] [☀ right:16px]  ← index.html (검색 없음)
```

### CSS

```css
.font-size-trigger {
  position: fixed;
  top: 12px;
  right: 60px;   /* guide: right:104px (검색 버튼이 60px 차지) */
  z-index: 200;
  width: 36px; height: 36px; border-radius: 50%;
  border: 1.5px solid var(--border-strong);
  background: var(--housing);   /* guide: var(--card) */
  color: var(--text-mid);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.2s;
  font-family: var(--serif);
  font-size: 14px;
  font-weight: 700;
}
.font-size-trigger:active { transform: scale(0.9); }

/* 크기별 root 변수 오버라이드 */
:root[data-fontsize="small"] { --base-font: 14px; --body-size: 13px; }
:root[data-fontsize="medium"] { --base-font: 16px; --body-size: 14px; } /* 기본값 */
:root[data-fontsize="large"] { --base-font: 18px; --body-size: 16px; }
```

### JS

```javascript
var fontSizes = ['medium', 'large', 'small']; // 순환 순서

function initFontSize() {
  var saved = localStorage.getItem('gj_fontsize') || 'medium';
  document.documentElement.setAttribute('data-fontsize', saved);
  updateFontSizeIcon(saved);
}

function cycleFontSize() {
  var current = document.documentElement.getAttribute('data-fontsize') || 'medium';
  var idx = fontSizes.indexOf(current);
  var next = fontSizes[(idx + 1) % fontSizes.length];
  document.documentElement.setAttribute('data-fontsize', next);
  localStorage.setItem('gj_fontsize', next);
  updateFontSizeIcon(next);
}

function updateFontSizeIcon(size) {
  var btn = document.getElementById('fontSizeTrigger');
  if (!btn) return;
  var labels = { small: '가-', medium: '가', large: '가+' };
  btn.textContent = labels[size];
}
```

### 적용할 CSS 속성

기존 하드코딩된 `font-size` 값을 CSS 변수로 교체:

```css
/* 기본 텍스트 */
body { font-size: var(--base-font, 16px); }

/* 카드 이름 */
.card-name { font-size: calc(var(--base-font, 16px) + 2px); }

/* 본문 */
.option-info, .place-info-row, .item-note-row { font-size: var(--body-size, 14px); }

/* 작은 텍스트 (라벨, 태그)는 변경하지 않음 — 이미 작아서 */
```

---

## Feature 7: 웹앱 내 챗봇 대화 (검토 보고서)

### 핵심 발견

`claude_api_handler.py`의 `process_message_api()` 함수는 **텔레그램에 비의존적**이다.
- 입력: `(json_data: dict, user_message: str)`
- 출력: `ApiResponse(text, data_modified, updated_data)`

따라서 HTTP API로 래핑하기가 단순하다.

### 추천 아키텍처: 옵션 A — VPS에 HTTP API 추가

```
웹앱 (브라우저)
  ↓ fetch('/api/chat')
Vercel Serverless (프록시)
  ↓ HTTP POST
VPS FastAPI (/chat)
  ↓ process_message_api()
Anthropic API + jsonbin.io
```

**왜 이 방식인가:**
- `process_message_api()` + 13개 도구를 그대로 재사용 (JS 포팅 불필요)
- 도구 추가/변경 시 Python 1곳만 수정
- 추가 비용 없음 (VPS 이미 운영 중)
- Vercel 시간 제한(10초) 걱정 없음 (VPS는 무제한)

### 추천 UI: 플로팅 챗 버블 + 하단 시트

```
┌──────────────────────────┐
│  [일정 보기 화면]          │
│                           │
│                           │
│                           │
│                           │
│                    [💬]    │  ← 플로팅 버블 (right:16px, bottom:24px)
└──────────────────────────┘

┌──────────────────────────┐  ← 버블 클릭 시
│  [일정 보기 화면]          │
├──────────────────────────┤
│  포저와 대화               │  ← 챗 시트 (60~70vh)
│  ─────────────────────    │
│  👤 경주 홈플러스 영업시간?   │
│  🤖 홈플러스 경주점은 09:00  │
│     ~22:00 영업합니다...    │
│                           │
│  [메시지 입력...]    [전송] │
└──────────────────────────┘
```

### 구현 단계

| Phase | 내용 | 예상 시간 |
|---|---|---|
| **Phase 1** | VPS: FastAPI HTTP 서버 + `/chat` 엔드포인트 + 비밀번호 인증 | 2~3시간 |
| **Phase 2** | Vercel: `/api/chat.js` 프록시 | 30분 |
| **Phase 3** | 웹앱: 플로팅 버블 + 챗 시트 UI | 2~3시간 |
| **Phase 4** | 향상: SSE 스트리밍, 대화 이력, 인라인 "물어보기" 버튼 | 추후 |

### 비용 예측

- API 비용: 1회 대화당 약 15~30원 (Claude Sonnet 기준)
- 여행 전~중 총 100~170회 → 약 1,500~4,500원
- Vercel: 무료 Hobby 플랜 유지 가능 (프록시만 하므로 10초 내 충분)
- VPS: 추가 비용 없음

### 보안

- API 키: VPS 환경변수에만 저장 (브라우저 노출 없음)
- 접근 제한: 간단한 비밀번호 (가족 공유) + Rate Limiting (분당 10회)
- 또는 Vercel 환경변수에 `CHAT_SECRET` 설정 후 세션 토큰 발급

### 리스크

| 리스크 | 대응 |
|---|---|
| VPS 장애 시 챗 불가 | 텔레그램 봇도 같은 VPS이므로 동일한 리스크. 일정 조회는 영향 없음 |
| 모바일 키보드로 챗 시트 가림 | `visualViewport` API로 키보드 높이 감지 후 시트 조정 |
| Tool Use 다중 라운드 시 응답 지연 | "포저가 생각하는 중..." 애니메이션 + 최대 30초 타임아웃 |
| 동시 접속 시 데이터 충돌 | jsonbin 쓰기는 봇과 동일 메커니즘이므로 현행과 동일한 리스크 |

---

## 구현 순서 (의존 관계 고려)

```
Phase A (데이터 준비)
  ├── [1] 홈플러스 guide 데이터 추가 (jsonbin)
  └── [4] 소아과 하드코딩 데이터 준비

Phase B (guide.html 변경) — Phase A 완료 후
  ├── [3] 일정 탭 제거
  ├── [4] 장소에 홈플러스·소아과 추가
  └── [5] 식당/카페 분리 서브탭

Phase C (index.html 변경) — Phase A 완료 후
  ├── [2] renderPlaceDetail() 함수 추가
  ├── [2] renderStayDetail() 함수 추가
  ├── [2] renderItemCard() 수정
  └── [2] STAY_DATA 임베드

Phase D (공통) — Phase B, C와 병렬 가능
  └── [6] 텍스트 크기 조절 (양쪽 페이지)

Phase E (별도 스프린트)
  └── [7] 웹앱 내 챗봇 (VPS API + UI)
```

### 예상 총 소요 시간

| Phase | 시간 |
|---|---|
| A (데이터) | 30분 |
| B (guide.html) | 2시간 |
| C (index.html) | 2~3시간 |
| D (텍스트 크기) | 1시간 |
| E (챗봇) | 5~6시간 |
| **A~D 합계** | **약 5~6시간** |
| **E 포함 전체** | **약 11~12시간** |

---

## 변경 파일 요약

| 파일 | Feature | 변경 |
|---|---|---|
| `webapp/index.html` | 2, 6 | renderPlaceDetail/renderStayDetail 함수, STAY_DATA, place-detail CSS, 텍스트 크기 JS/CSS |
| `webapp/guide.html` | 3, 4, 5, 6 | section-nav 수정, overview 제거, 소아과 데이터, 서브탭, 텍스트 크기 JS/CSS |
| jsonbin 여행 데이터 | 1, 4 | 홈플러스 guide 데이터 추가 |
| `src/web_api.py` (신규) | 7 | FastAPI HTTP 서버 |
| `webapp/api/chat.js` (신규) | 7 | Vercel 프록시 |

---

## 참고: 홈플러스 휴무일 경고

**2/22(일)은 홈플러스 정기 휴무일!**

여행 4일차(2/22, 일요일)에 홈플러스 장보기가 있다면 일정 조정 필요.
장보기는 **2/19(수, 도착일)** 또는 **2/21(토)** 등 다른 날로 이동을 권장.

이 정보는 오너에게 반드시 전달해야 함.
