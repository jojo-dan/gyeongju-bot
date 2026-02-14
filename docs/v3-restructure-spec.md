# V3 구조 개편 기획서

> 작성일: 2026-02-14
> 상태: **검토 요청 (오너)**
> 범위: 웹앱 통합 + 상태 시스템 재설계 + 포저 도구 확장

---

## 전체 요약

| # | 이슈 | 난이도 | 변경 범위 |
|---|------|--------|-----------|
| 1 | 확정 카드(온목당) 항상 펼쳐짐 | 낮음 | index.html JS 1줄 |
| 2 | 채팅 히스토리 유지 | 낮음 | JS (sessionStorage) |
| 3 | 포저 확정 해제 불가 | 중간 | tool_definitions.py + tool_executor.py + 시스템 프롬프트 |
| 4 | 장소 카드 이모지 제거 | 낮음 | index.html JS |
| 5 | Day 4 저녁 수정 (대구 제외, 이름 변경) | 낮음 | jsonbin 데이터 |
| 6 | 마지막 일차 참고 정보 제거 | 낮음 | jsonbin 데이터 + index.html |
| 7 | **일정+가이드 페이지 통합** | **높음** | guide.html 대규모 개편, index.html 폐기 |
| 8 | **상태 시스템 재설계 (확정→방문)** | **높음** | 데이터 모델 + 도구 + 프론트엔드 |
| 9 | **리뷰 기능** | 중간 | 데이터 모델 + 도구 + 프론트엔드 |

---

## Phase 1: 즉시 수정 (1, 4, 5, 6)

### Issue 1: 확정 카드 항상 펼쳐짐

**원인**: `renderOptionCard()`에서 `isChosen`이면 `<details open>` 속성을 강제 부여.

**해결**: `open` 속성 제거. 확정된 카드도 접힌 상태가 기본. `chosen` 클래스와 "확정" 뱃지로 구분은 유지.

```javascript
// 변경 전
let html = '<details class="option-card' + (isChosen ? ' chosen' : '') + '"'
  + (isChosen ? ' open' : '') + '>';

// 변경 후
let html = '<details class="option-card' + (isChosen ? ' chosen' : '') + '">';
```

### Issue 4: 장소 카드 이모지 제거

**현재**: `renderSinglePlaceCard()`에서 장소명 앞에 📍 이모지 추가.

**해결**: 이모지 제거. 식당과 동일하게 텍스트만 표시.

```javascript
// 변경 전
html += '<span class="place-detail-icon">\uD83D\uDCCD</span>';

// 변경 후: 해당 라인 제거
```

`renderPlaceDetail()` 내 `\uD83D\uDCCD` (📍)와 `\uD83C\uDFE0` (🏠) 아이콘도 동일하게 제거.

### Issue 5: Day 4 저녁 수정

**변경사항** (jsonbin 데이터):
- `d4_dinner.title`: "축하 저녁" → "저녁"
- `d4_dinner.note`: "첫 풀마라톤 완주 축하!" → "" (제거)
- `d4_dinner.options`에서 "대구에서 식사" 옵션 제거 (3개 옵션만 남김)

### Issue 6: 참고 정보 제거

**현재**: `travelData.reference` 객체에 거리/연락처/쇼핑 정보가 있고, 마지막 일차(Day 6) 하단에 표시.

**변경사항**:
- jsonbin에서 `reference` 필드 제거
- `renderReference()` 함수와 관련 CSS 삭제
- `renderDayContent()`에서 참고 섹션 렌더링 코드 삭제

> 거리/연락처 정보가 필요하면 포저에게 물어보면 되므로 웹앱에서 중복 표시할 필요 없음.

---

## Phase 2: 포저 도구 확장 (3)

### Issue 3: 확정 해제 기능

**현재 문제**: `set_chosen` 도구는 옵션명을 partial match하여 `item.chosen`에 설정. 빈 문자열을 보내면 옵션 매칭에 실패하여 에러 반환.

**해결: `unset_chosen` 도구 신규 추가**

#### tool_definitions.py

```python
{
    "name": "unset_chosen",
    "description": "항목의 확정을 해제한다. 확정된 옵션이 없는 원래 상태로 되돌린다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "string",
                "description": "항목 ID",
            },
        },
        "required": ["item_id"],
    },
},
```

#### tool_executor.py

```python
@_register("unset_chosen")
def _handle_unset_chosen(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템 선택지 확정 해제."""
    item_id = inp.get("item_id", "")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    old_chosen = item.get("chosen", "")
    if not old_chosen:
        return {"ok": True, "item_id": item_id, "message": "이미 확정된 옵션이 없습니다."}

    item["chosen"] = ""
    ctx.mark_modified(f"{item_id} 확정 해제: {old_chosen}")
    logger.info("Chosen unset: %s (was: %s)", item_id, old_chosen)

    return {"ok": True, "item_id": item_id, "old_chosen": old_chosen}
```

#### 시스템 프롬프트 업데이트

`claude_api_handler.py`의 시스템 프롬프트에 확정 해제 가능 사실 추가.

---

## Phase 3: 페이지 통합 (7) — 핵심 변경

### 현재 구조

```
index.html (일정 페이지)       guide.html (가이드 페이지)
├── Day 1~6 탭                 ├── 장소 섹션
├── 각 일정 카드               ├── 식당 섹션 (전체/식당/카페)
├── 옵션 카드                  ├── 숙소 섹션
├── 장소 상세                  └── 채팅
└── 채팅
```

### 변경 후 구조

```
guide.html (통합 페이지) ← index.html 흡수
├── 상단 네비게이션: [일정] [장소] [식당] [숙소]
│
├── [일정] 탭 활성 시:
│   ├── 서브탭: Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6
│   └── 해당 일차 일정 카드들 (현재 index.html의 renderDayContent)
│
├── [장소] 탭 활성 시:
│   └── 장소 아코디언 카드들 (현재 guide.html의 renderPlaces)
│
├── [식당] 탭 활성 시:
│   ├── 서브탭: 전체 | 식당 | 카페
│   ├── 정렬: 별점순 | 거리순
│   └── 식당/카페 카드들 (현재 guide.html의 renderRestaurants)
│
├── [숙소] 탭 활성 시:
│   └── 숙소 카드 (현재 guide.html의 renderStay)
│
└── 채팅 FAB + 시트
```

### 네비게이션 구현

**상단 탭 (4개)**:
```html
<div class="section-nav">
  <button class="section-nav-btn active" data-tab="schedule">일정</button>
  <button class="section-nav-btn" data-tab="places">장소</button>
  <button class="section-nav-btn" data-tab="restaurants">식당</button>
  <button class="section-nav-btn" data-tab="stay">숙소</button>
</div>
```

**일정 탭 선택 시 서브탭 (Day)**:
```html
<div class="day-tabs" id="dayTabs">
  <!-- JS로 동적 생성 -->
  <button class="day-tab active" data-day="0">2/19 목</button>
  <button class="day-tab" data-day="1">2/20 금</button>
  ...
</div>
```

**식당 탭 선택 시 서브탭 (필터)**:
```html
<div class="rest-sub-tabs" id="restSubTabs">
  <button class="rest-sub-tab active" data-type="all">전체</button>
  <button class="rest-sub-tab" data-type="meal">식당</button>
  <button class="rest-sub-tab" data-type="cafe">카페</button>
</div>
```

### 탭 전환 로직

```javascript
function switchTab(tabName) {
  // 1. 상단 탭 활성 상태 변경
  document.querySelectorAll('.section-nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });

  // 2. 서브탭 표시/숨기기
  document.getElementById('dayTabs').style.display = tabName === 'schedule' ? '' : 'none';
  document.getElementById('restSubTabs').style.display = tabName === 'restaurants' ? '' : 'none';
  document.getElementById('sortBar').style.display = tabName === 'restaurants' ? '' : 'none';

  // 3. 콘텐츠 렌더링
  renderContent(tabName);
}

function renderContent(tabName) {
  var area = document.getElementById('contentArea');
  switch (tabName) {
    case 'schedule': renderDayContent(activeDay); break;
    case 'places': area.innerHTML = renderPlaces(travelData.days); break;
    case 'restaurants': area.innerHTML = renderRestaurants(travelData.days); applyRestFilters(); break;
    case 'stay': area.innerHTML = renderStay(); break;
  }
}
```

### index.html → guide.html 통합 이관 대상

index.html에서 guide.html로 이동해야 할 코드:

| 기능 | 함수/코드 |
|------|-----------|
| 일정 렌더링 | `renderDayContent()`, `renderItemCard()` |
| 옵션 카드 | `renderOptionCard()`, `renderSimpleOption()`, `renderEnrichedOption()` |
| 장소 상세 | `renderPlaceDetail()`, `renderSinglePlaceCard()` (index 버전) |
| 숙소 상세 | `renderStayDetail()` |
| Day 탭 | `switchDay()`, `formatTabDate()` |
| 상태/시간 유틸 | `parseOpenClosed()`, `getStatusLabel()`, `distanceKm()` |
| patchGuideData | subPlaces 주입 로직 |
| 위치 기반 기능 | `initGeolocation()`, 거리 계산 |

### index.html 처리

통합 후 `index.html`은 `guide.html`로 리다이렉트:

```html
<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0;url=guide.html"></head>
<body><a href="guide.html">이동</a></body>
</html>
```

또는 Vercel의 `vercel.json`에서 리다이렉트 설정.

---

## Phase 4: 상태 시스템 재설계 (8)

### 현재 상태 모델

```
item.status: "planned" | "done" | "skipped"
item.chosen: "옵션명" | ""           ← 식당만 의미 있음
```

**문제점**:
- `chosen`은 "어디 갈지 정했다"이지 "다녀왔다"가 아님
- 관광지/숙소에는 chosen 개념이 없음
- "갔다 왔다" 표시가 일정 탭과 식당/장소 탭 간 연동되지 않음

### 새로운 상태 모델

```
item.status: "planned" | "done" | "skipped"    ← 기존과 동일
item.chosen: "옵션명" | ""                      ← 제거 (Phase 4에서)
item.visited: true | false                      ← 신규: "다녀왔는지"
item.review: "짧은 감상" | ""                   ← 신규 (Issue 9)
```

> **`chosen` 필드 존치 여부**: 현재 "확정"은 "이곳으로 가기로 했다"를 의미. 실제 사용 시나리오에서 식당을 미리 정하는 것보다, **다녀온 후 기록**하는 것이 더 중요하다는 피드백. 따라서:

**결정: `chosen` 필드 폐기, `visited` + `review`로 대체**

- `item.status = "done"` → 해당 일정 시간대를 완료했다
- `item.visited = true` + `item.visitedOption = "온목당"` → 실제 온목당에 다녀왔다
- `item.review = "곰탕 맛있었음"` → 한줄 감상

### 상태 흐름 (사용자 시나리오)

```
시나리오 1: "온목당 다녀왔어"
→ 포저: update_visit(item_id="d1_dinner", option_name="온목당", visited=true)
→ 결과: d1_dinner.visited = true, d1_dinner.visitedOption = "온목당"
→ 웹앱: 일정 탭 Day1 저녁 카드에 ✓ 표시, 식당 탭 온목당 카드에 ✓ 표시

시나리오 2: "온목당 다녀왔어. 곰탕이 좀 짜더라"
→ 포저: update_visit(item_id="d1_dinner", option_name="온목당", visited=true)
       + update_review(item_id="d1_dinner", review="곰탕이 좀 짜더라")
→ 결과: visited + review 모두 업데이트
→ 웹앱: ✓ + 리뷰 노트 표시

시나리오 3: "숙소 도착했어"
→ 포저: update_visit(item_id="d1_accommodation", visited=true)
→ 결과: 일정 카드 + 숙소 탭 모두 ✓

시나리오 4: "첨성대 안 가기로 했어"
→ 포저: update_status(item_id="d1_activity", status="skipped")
→ 결과: 일정 카드 취소선, 장소 탭에서도 스킵 표시
```

### 데이터 마이그레이션

기존 `chosen` → `visitedOption` 자동 변환은 하지 않음.
- 여행 시작 전이므로 모든 `visited`는 false에서 시작
- 기존 `chosen: "온목당"`은 제거 (확정 개념 폐기)

### 프론트엔드 표시

**일정 탭 카드**:
```
[방문 전]  ● 저녁  |  저녁 식사  |  3개 옵션
[방문 후]  ✓ 저녁  |  저녁 식사 — 온목당  |  "곰탕이 좀 짜더라"
[스킵]     ○ 저녁  |  저녁 식사  |  ─ (취소선)
```

**식당/장소/숙소 탭 카드**:
```
[미방문]  온목당  4.3 >        ← 기본 상태
[방문]    온목당  4.3 ✓ >      ← visited 뱃지 (초록색)
          "곰탕이 좀 짜더라"   ← review 표시 (접힌 상태에서도 보임)
```

### CSS 클래스

```css
/* 방문 완료 */
.option-card.visited { border-left: 3px solid var(--sage); }
.option-card.visited .visit-badge { display: inline-block; }
.card.visited { border-left: 3px solid var(--sage); }

/* 리뷰 */
.review-text {
  font-size: calc(12px + var(--delta, 0px));
  color: var(--text-mid);
  font-style: italic;
  padding: 4px 0;
}
```

---

## Phase 5: 포저 도구 재설계 (8, 9)

### 폐기할 도구

| 도구 | 사유 |
|------|------|
| `set_chosen` | `chosen` 개념 폐기. `update_visit`으로 대체 |
| `unset_chosen` | Phase 2에서 추가 예정이었으나 Phase 4에서 chosen 자체를 폐기하므로 불필요 |

### 신규 도구

#### `update_visit` — 방문 기록

```python
{
    "name": "update_visit",
    "description": (
        "장소/식당/숙소의 방문 여부를 기록한다. "
        "옵션이 있는 항목(식당 등)은 어떤 옵션을 방문했는지도 함께 기록한다."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "string",
                "description": "항목 ID",
            },
            "visited": {
                "type": "boolean",
                "description": "방문 여부 (true: 방문함, false: 방문 취소)",
            },
            "option_name": {
                "type": "string",
                "description": "방문한 옵션 이름 (식당 등 옵션이 있는 항목만. 부분 일치 가능)",
            },
        },
        "required": ["item_id", "visited"],
    },
}
```

#### `update_review` — 리뷰 기록

```python
{
    "name": "update_review",
    "description": "장소/식당에 대한 한줄 리뷰(감상)를 기록한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "string",
                "description": "항목 ID",
            },
            "review": {
                "type": "string",
                "description": "한줄 리뷰/감상",
            },
        },
        "required": ["item_id", "review"],
    },
}
```

### Executor 구현

```python
@_register("update_visit")
def _handle_update_visit(ctx: ExecutionContext, inp: dict) -> dict:
    """방문 기록 업데이트."""
    item_id = inp.get("item_id", "")
    visited = inp.get("visited", True)
    option_name = inp.get("option_name", "")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    item["visited"] = visited

    if option_name:
        matched = ctx.find_option(item, option_name)
        if matched:
            item["visitedOption"] = matched["name"]
        else:
            return {"error": f"옵션을 찾을 수 없습니다: {option_name}"}

    # 방문 시 자동으로 status를 done으로 변경
    if visited and item.get("status") == "planned":
        item["status"] = "done"

    action = "방문 기록" if visited else "방문 취소"
    ctx.mark_modified(f"{item_id} {action}")

    return {"ok": True, "item_id": item_id, "visited": visited,
            "visitedOption": item.get("visitedOption", "")}


@_register("update_review")
def _handle_update_review(ctx: ExecutionContext, inp: dict) -> dict:
    """리뷰 기록."""
    item_id = inp.get("item_id", "")
    review = inp.get("review", "")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    item["review"] = review
    ctx.mark_modified(f"{item_id} 리뷰: {review[:30]}")

    return {"ok": True, "item_id": item_id, "review": review}
```

### 시스템 프롬프트 변경

`claude_api_handler.py`의 시스템 프롬프트 수정:

```
기존:
- set_chosen: 식당 등 확정 시 사용

변경:
- update_visit: 사용자가 "~~ 다녀왔어", "~~ 도착했어" 등 말하면 방문 기록
- update_review: 사용자가 감상/평가를 남기면 리뷰 기록
- 방문 기록 시 자동으로 status도 done으로 변경됨
- "확정" 개념은 폐기됨. 미리 정하는 대신, 다녀온 후 기록하는 방식
```

---

## Phase 2 수정: 채팅 히스토리 유지 (2)

### 현재 문제
채팅 시트를 닫고 다시 열면 히스토리가 사라짐.

### 해결: sessionStorage 사용

```javascript
var CHAT_STORAGE_KEY = 'gyeongju_chat_history';

function saveChatHistory() {
  var msgs = document.getElementById('chatMessages');
  sessionStorage.setItem(CHAT_STORAGE_KEY, msgs.innerHTML);
}

function loadChatHistory() {
  var saved = sessionStorage.getItem(CHAT_STORAGE_KEY);
  if (saved) {
    document.getElementById('chatMessages').innerHTML = saved;
    return true;  // 히스토리 있음 → 웰컴 화면 안 보여줌
  }
  return false;
}

// appendChatMsg 마지막에 saveChatHistory() 호출
// 페이지 로드 시 loadChatHistory()로 복원
```

**왜 sessionStorage?**
- `localStorage`: 브라우저 종료 후에도 유지 → 다음 날 접속 시 어제 대화가 보임 (불필요)
- `sessionStorage`: 탭이 열려있는 동안만 유지 → 채팅 시트 닫았다 열어도 유지, 탭 닫으면 초기화

---

## 구현 순서

```
Phase 1 — 즉시 수정 (간단)
  ├── [1] 확정 카드 open 제거
  ├── [4] 장소 이모지 제거
  ├── [5] Day 4 저녁 jsonbin 수정
  └── [6] 참고 정보 제거 (jsonbin + 코드)

Phase 2 — 채팅 개선
  └── [2] sessionStorage 히스토리

Phase 3 — 포저 도구 (chosen 폐기 + visit/review 추가)
  ├── [3] set_chosen 제거, unset_chosen 불필요
  ├── [8] update_visit 도구 추가
  ├── [9] update_review 도구 추가
  ├── 시스템 프롬프트 업데이트
  └── 테스트

Phase 4 — 페이지 통합
  ├── [7] guide.html에 일정 탭 추가
  ├── [7] index.html의 일정 렌더링 코드 이관
  ├── [7] index.html → guide.html 리다이렉트
  └── [7] 통합 탭 네비게이션 구현

Phase 5 — 방문/리뷰 UI
  ├── [8] visited 상태 표시 (일정/장소/식당/숙소 전체)
  ├── [8] visited 연동 (포저→데이터→UI 반영)
  ├── [9] review 표시 UI
  └── [8] chosen 관련 UI 전부 제거
```

---

## 변경 파일 요약

| 파일 | Phase | 변경 |
|------|-------|------|
| `webapp/guide.html` | 1,2,4,5 | 통합 페이지 (일정 탭 추가, 네비게이션, visited/review UI) |
| `webapp/index.html` | 4 | 리다이렉트 페이지로 축소 |
| `src/tool_definitions.py` | 3 | set_chosen 제거, update_visit/update_review 추가 |
| `src/tool_executor.py` | 3 | _handle_set_chosen 제거, visit/review 핸들러 추가 |
| `src/claude_api_handler.py` | 3 | 시스템 프롬프트 업데이트 |
| jsonbin 데이터 | 1 | Day 4 저녁 수정, reference 제거, chosen 필드 정리 |

---

## 리스크

| 리스크 | 대응 |
|--------|------|
| 페이지 통합 중 기능 누락 | index.html의 모든 함수를 체크리스트로 관리하며 이관 |
| chosen 폐기 시 기존 데이터 호환성 | 마이그레이션 스크립트로 chosen 필드 제거, visited=false 기본값 |
| 포저가 새 도구를 제대로 사용하지 못할 가능성 | 시스템 프롬프트에 명확한 사용 시나리오 예시 추가 |
| sessionStorage 히스토리가 페이지 통합 후에도 동작하는지 | 단일 페이지이므로 탭 전환 시 히스토리 유지됨 |
| 텔레그램 봇 호환성 | 텔레그램 봇도 동일 도구를 사용하므로 tool_definitions 변경이 봇에도 적용됨. 봇 재시작 필요. |

---

## 미결 사항 (오너 확인 필요)

1. **`chosen` 완전 폐기 vs 병행**: 현재 계획은 chosen을 완전히 폐기하고 visited로 대체. "미리 어디 갈지 정해두는" 기능이 필요하면 chosen 유지 가능. → **오너 결정 필요**

2. **참고 정보 완전 삭제**: 거리/연락처/쇼핑 정보를 포저한테 물어보는 것으로 대체. 별도 탭이나 섹션으로 남길지? → **오너 결정 필요**

3. **guide.html URL**: 통합 후 메인 URL을 `guide.html` 대신 `index.html`로 할지? Vercel에서 `/`가 자동으로 `index.html`을 서빙하므로, 통합 코드를 `index.html`에 넣는 것이 URL이 깔끔. → **오너 결정 필요**
