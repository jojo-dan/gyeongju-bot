# 검색/필터 기능 기획서

> 상태: **DRAFT** — 오너 승인 대기
> 대상: `webapp/index.html`, `webapp/guide.html`
> 관련: 크라피카(UX), 히소카(UI) 브레인스토밍 결과 반영

---

## 1. 배경

경주 가족여행 웹앱의 두 페이지(일정 상세, 가이드)에 검색/필터 기능을 추가한다.
전체 데이터 규모가 ~50개 항목(일정 30~48 + 식당 ~20 + 장소 5~8 + 숙소 1)으로 작으므로,
대량 데이터 탐색보다는 **"이미 있는 정보를 빠르게 찾기"** 가 목적이다.

---

## 2. UX 방향: Approach B — Filter Bar (인라인 필터/하이라이트)

### 왜 이 방식인가

| 비교 | A: Spotlight (오버레이) | **B: Filter Bar** | C: Command Bar (하단 시트) |
|---|---|---|---|
| 구현 복잡도 | 중간 | **낮음** | 높음 |
| 맥락 유지 | 낮음 | **높음** | 중간 |
| 크로스 day 결과 | 좋음 | dot 힌트 | 좋음 |
| 데이터 규모 적합 | 과잉 | **최적** | 약간 과잉 |

- 현재 콘텐츠의 맥락을 유지하면서 in-place 필터링 + 하이라이트
- 기존 DOM 조작으로 show/hide — 가장 가벼운 구현
- 필터 칩만으로 80% 시나리오 커버 가능 (프리텍스트는 2차)

### MVP 범위 (1차)

**필터 칩만 구현.** 프리텍스트 검색은 2차에 추가.

---

## 3. 상세 설계

### 3-1. index.html (일정 상세)

#### 레이아웃

```
[Day 1][Day 2][Day 3][Day 4][Day 5][Day 6]  ← 기존 day tabs (sticky)
[🔍] 검색 또는 필터...                        ← 새 search bar (탭하면 확장)
[아이 OK][아빠 OK][카페][식사][관광]           ← 필터 칩 (확장 시)
```

#### 동작

1. **검색 트리거**: theme toggle 왼쪽에 동일 스타일 원형 버튼 (36x36px, `right: 60px`)
2. 탭하면 day tabs 아래에 search bar + 필터 칩이 슬라이드 확장 (`max-height` 애니메이션)
3. **검색 범위**: 전체 day 검색 (현재 day만 아님)
4. **필터 동작**:
   - 매칭되지 않는 item-card → `display: none`
   - 매칭되는 item 내 해당 텍스트에 `<mark>` 하이라이트 (2차 프리텍스트용)
   - 결과가 있는 day tab에 accent dot 표시
   - 현재 day에 결과 0건이면: "Day 3에 2건의 결과가 있습니다" 안내 표시
5. **칩 필터 매핑**:
   - `아이 OK` → `option.hiro === 'good'`
   - `아빠 OK` → `option.dad === 'good'`
   - `카페` → `item.cat === 'cafe'`
   - `식사` → `item.cat === 'meal'`
   - `관광` → `item.cat === 'activity'`
6. 칩은 토글 방식, 복수 선택 가능 (AND 조합)
7. "X" 버튼 → 필터 초기화 + bar 접힘

#### 프리텍스트 검색 대상 (2차)

| 필드 | 설명 |
|---|---|
| `item.title` | 활동 이름 |
| `item.note` | 메모 |
| `option.name` | 식당/장소 이름 |
| `option.menu` | 메뉴 설명 |
| `option.hiroNote` | 히로 주의사항 |
| badge 텍스트 | "아빠 OK" 등 |

### 3-2. guide.html (가이드)

#### 레이아웃

```
[일정][장소][식당][숙소]                      ← 기존 section nav (sticky)
[🔍] 검색 또는 필터...                        ← 새 search bar
[아이 OK][아빠 OK][수유실][유모차][영업중]    ← 필터 칩
```

#### 동작

1. 검색 범위: 4개 섹션 전체
2. **필터 동작**:
   - 매칭되지 않는 `<details>` 카드 → `display: none`
   - 매칭되는 카드 → 자동 `open` + `<mark>` 하이라이트
   - 매칭 섹션이 1개면 section nav도 자동 활성화
3. **추가 칩**:
   - `수유실` → `guide.babyTips.nursingRoom` 존재 여부
   - `유모차` → `guide.babyTips.stroller` 포함 여부
   - `영업중` → `parseOpenClosed()` 결과가 open (식당 섹션)
4. 기존 sort-bar(별점순/거리순)는 검색 바 아래 유지 (검색 + 정렬 조합 가능)

#### 프리텍스트 검색 대상 (2차)

| 필드 | 설명 |
|---|---|
| `place.title` | 장소 이름 |
| `guide.mustDo[]` | 필수 체험 |
| `guide.babyTips.*` | 유모차/수유실/화장실/쉴 곳 |
| `guide.practicalInfo.*` | 입장료/시간/주차 등 |
| `restaurant.name` | 식당 이름 |
| `restaurant.menu` | 메뉴 |
| `restaurant.menuDetail[].item` | 메뉴 상세 항목 |
| `restaurant.loc` | 위치 |
| `STAY_DATA` 전체 | 숙소 정보 |

---

## 4. UI 디자인

### 검색 트리거 버튼

theme toggle과 동일 스타일 — 원형 36x36, 같은 border/shadow/radius.

```css
.search-trigger {
  position: fixed;
  top: 12px;
  right: 60px;  /* theme toggle(right:16px) + 36px(width) + 8px(gap) */
  z-index: 200;
  width: 36px; height: 36px; border-radius: 50%;
  border: 1.5px solid var(--border-strong);
  background: var(--housing);  /* guide: var(--card) */
  color: var(--text-mid);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.2s;
}
.search-trigger:active { transform: scale(0.9); }
.search-trigger.active {
  background: var(--display);  /* guide: var(--hero) */
  color: var(--display-text);  /* guide: var(--hero-text) */
  border-color: var(--display);
}
.search-trigger svg { width: 16px; height: 16px; }
```

### 검색 바

```css
.search-bar-wrapper {
  max-width: 440px;
  margin: 0 auto;
  padding: 0 16px;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.35s cubic-bezier(0.4,0,0.2,1),
              opacity 0.25s ease;
}
.search-bar-wrapper.open {
  max-height: 80px;
  opacity: 1;
  padding-bottom: 12px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--housing);  /* guide: var(--card) */
  border: 1.5px solid var(--border-strong);
  border-radius: 20px;
  padding: 12px 18px;
  box-shadow: var(--shadow-device);
}
.search-bar:focus-within {
  border-color: var(--accent-soft);
  box-shadow: var(--shadow-device), 0 0 0 3px var(--accent-bg);
}
.search-bar input {
  flex: 1; border: none; outline: none; background: transparent;
  font-family: var(--serif);
  font-size: 16px;  /* iOS zoom 방지 */
  color: var(--text);
}
.search-bar input::placeholder {
  color: var(--text-muted);
  font-style: italic;
  font-weight: 300;
}
```

### 필터 칩

```css
.search-filters {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: 0 16px 12px;
  max-width: 440px;
  margin: 0 auto;
}
.search-filters::-webkit-scrollbar { display: none; }

.filter-chip {
  flex-shrink: 0;
  font-family: var(--mono);
  font-size: 11px; font-weight: 500;
  letter-spacing: 0.3px;
  padding: 8px 14px;
  border-radius: 12px;
  border: 1.5px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  white-space: nowrap;
}
.filter-chip.active {
  background: var(--display);  /* guide: var(--hero) */
  color: var(--display-text);
  border-color: var(--display);
  box-shadow: 0 2px 8px rgba(61,46,31,0.15);
}
```

### 하이라이트 (2차 프리텍스트)

```css
.search-highlight {
  color: var(--accent);
  font-weight: 700;
  text-decoration: underline;
  text-decoration-color: var(--accent-bg);
  text-underline-offset: 2px;
  text-decoration-thickness: 2px;
}
```

### Empty State

```css
.search-empty {
  text-align: center;
  padding: 48px 24px;
}
.search-empty::before {
  content: '';
  display: block; width: 40px; height: 2px;
  background: var(--accent);
  margin: 0 auto 20px; border-radius: 1px;
}
.search-empty-title {
  font-family: var(--serif);
  font-size: 20px; font-weight: 600;
  color: var(--text);
  font-style: italic;
  margin-bottom: 8px;
}
.search-empty-desc {
  font-size: 14px;
  color: var(--text-light);
  line-height: 1.6;
}
```

텍스트: *"아직 찾지 못했어요"* / "다른 키워드로 검색하거나, 필터를 바꿔 보세요."

---

## 5. IME (한국어 입력) 처리 (2차)

```javascript
let isComposing = false;
searchInput.addEventListener('compositionstart', () => { isComposing = true; });
searchInput.addEventListener('compositionend', (e) => {
  isComposing = false;
  performSearch(e.target.value);
});
searchInput.addEventListener('input', (e) => {
  if (!isComposing) performSearch(e.target.value);
});
```

---

## 6. 구현 순서

### 1차 (MVP): 필터 칩만

1. 검색 트리거 버튼 HTML + CSS 추가
2. search-bar-wrapper HTML + CSS 추가 (input은 넣되 2차까지 비활성)
3. 필터 칩 HTML + CSS + JS (토글/필터 로직)
4. index.html: item-card show/hide + day tab dot 표시
5. guide.html: `<details>` show/hide + 자동 open
6. empty state
7. 다크모드 확인

### 2차: 프리텍스트 검색

1. input 활성화 + IME 처리
2. 검색 인덱스 구성 (각 카드의 searchable text 결합)
3. `<mark>` 하이라이트 렌더링
4. 결과 카운트 표시
5. 크로스페이지 힌트 (empty state에 "가이드에서 찾아보기" 링크)

---

## 7. 변경 파일

| 파일 | 변경 |
|---|---|
| `webapp/index.html` | CSS 추가, HTML (검색 트리거 + bar), JS (필터 로직) |
| `webapp/guide.html` | CSS 추가, HTML (검색 트리거 + bar), JS (필터 로직) |

---

## 8. 리스크

| 리스크 | 대응 |
|---|---|
| 필터 칩이 화면 폭 초과 | 가로 스크롤 + 우측 페이드 그래디언트 |
| guide.html의 sort-bar와 UI 겹침 | search-bar 아래에 sort-bar 유지, 자연스럽게 병합 |
| sticky 요소 겹침 (day tabs + search bar) | z-index 관리: day tabs(100) < search bar(110) < toggle(200) |
| 칩 복수 선택 시 결과 0건 | empty state 표시 + "필터를 줄여보세요" 안내 |
