# T-005 최종 보완 기획서 (v2)

> 작성일: 2026-02-14
> 상태: **검토 요청 (오너)**
> 범위: 장소명 정합성, UI 기본값, 자동 갱신, 식당 필터, 홈쿡 탭 신설, 출발 전 체크리스트

---

## 전체 요약

| # | 이슈 | 난이도 | 변경 범위 |
|---|------|--------|-----------|
| 1 | 장소 카드에서 행위 분리 (4건) | 낮음 | index.html JS (guide에 placeName 추가) |
| 2 | 폰트 크기 '크게' + 라이트 모드 기본값 | 낮음 | index.html JS |
| 3 | 자동 갱신(30초 폴링) 제거 | 낮음 | index.html JS |
| 4 | 식당 가이드에서 숙소 옵션 제외 | 낮음 | index.html JS |
| 5 | **홈쿡 탭** 신설 (5번째 탭) | 중간 | index.html (탭 + UI) |
| 6 | **출발 전** 하위 탭 (일정 탭 내) | 중간 | index.html JS + jsonbin 데이터 |
| 7 | 배달/새벽배송 리서치 반영 | - | 데이터 정보 |

---

## Issue 1: 장소 카드에서 행위 분리

### 문제
일정 카드의 **title**은 행위를 포함해도 OK ("홈플러스 장보기", "교촌마을 산책" 등).
하지만 카드 안에 접히는 **장소 상세 카드**(accordion)에는 **순수 장소명**만 들어가야 한다.

현재 `renderPlaceDetail(item)` → `renderSinglePlaceCardInline(item.title, ...)` 로 `item.title`을 그대로 장소명으로 사용하고 있어서, "홈플러스 장보기"가 장소 카드 이름에도 그대로 나온다.

`renderPlaces()` (장소 탭)에서도 동일하게 `item.title`을 장소명으로 사용: `renderGuidePlace({name:item.title, ...}, ...)`.

### 해결

**guide 데이터에 `placeName` 필드 추가:**

```javascript
// renderPlaceDetail() 수정 (line 969~971)
// 변경 전
var g = item.guide;
if(!g) return '';
return renderSinglePlaceCardInline(item.title, g.subtitle, g);

// 변경 후
var g = item.guide;
if(!g) return '';
return renderSinglePlaceCardInline(g.placeName || item.title, g.subtitle, g);
```

```javascript
// renderPlaces() 수정 (line 1213)
// 변경 전
html += renderGuidePlace({name:item.title, subtitle:g.subtitle, guide:g, babyTips:g.babyTips}, cardIndex++, days);

// 변경 후
html += renderGuidePlace({name:g.placeName || item.title, subtitle:g.subtitle, guide:g, babyTips:g.babyTips}, cardIndex++, days);
```

**4개 항목에 placeName 추가 (patchGuideData 또는 jsonbin):**

| 일정 카드 title (유지) | 장소 카드 placeName (추가) |
|----------------------|--------------------------|
| "홈플러스 장보기" | "홈플러스" |
| "동궁과 월지 야경" | "동궁과 월지" |
| "교촌마을 산책" | "교촌마을" |
| "보문호수 산책" | "보문호수" |

**patchGuideData에서 처리하는 방식:**
```javascript
// 홈플러스 가이드에 placeName 추가
if(item.title && item.title.indexOf('홈플러스') !== -1 && !item.guide){
  item.guide = {
    placeName: '홈플러스',
    subtitle: '경주 유일의 대형 할인점 · 2024 메가푸드마켓 리뉴얼',
    // ... 기존 guide 데이터
  };
}
```

```javascript
// 동궁과 월지, 교촌마을, 보문호수 — jsonbin guide에 placeName 추가
// 또는 patchGuideData에서 패치
if(item.guide && !item.guide.placeName) {
  if(item.title.indexOf('동궁과 월지') !== -1) item.guide.placeName = '동궁과 월지';
  if(item.title.indexOf('교촌마을') !== -1) item.guide.placeName = '교촌마을';
  if(item.title.indexOf('보문호수') !== -1) item.guide.placeName = '보문호수';
}
```

**핵심 원칙:** `item.title`은 **변경하지 않는다**. 일정 카드에서는 행위 포함 title이 그대로 쓰이고, 장소 카드에서만 `placeName`을 우선 사용.

---

## Issue 2: 폰트 크기 '크게' + 라이트 모드 기본값

### 변경

**폰트 크기 기본값: medium → large**
```javascript
// line 774
// 변경 전
var saved = localStorage.getItem('gj_fontsize') || 'medium';
// 변경 후
var saved = localStorage.getItem('gj_fontsize') || 'large';
```

**테마 기본값: 시스템 따름 → 라이트**
```javascript
// line 748~751
// 변경 전
function initTheme(){
  var saved = localStorage.getItem('gj_theme');
  if(saved) document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon();
}
// 변경 후
function initTheme(){
  var saved = localStorage.getItem('gj_theme');
  document.documentElement.setAttribute('data-theme', saved || 'light');
  updateThemeIcon();
}
```

- 첫 방문 시: 라이트 모드 + 큰 폰트
- 기존에 설정을 바꾼 사용자: localStorage에 값이 있으므로 영향 없음

---

## Issue 3: 자동 갱신 제거

### 현재
```javascript
var POLL_INTERVAL = 30000;  // 30초
(function init(){
  fetchData();
  pollTimer = setInterval(fetchData, POLL_INTERVAL);
})();
```

30초마다 전체 innerHTML 교체 → 깜빡임, 스크롤 초기화, `<details>` 닫힘.

### 변경
```javascript
// 폴링 제거, 초기 로드만 유지
(function init(){
  fetchData();
})();

// 삭제:
// var pollTimer = null;
// var POLL_INTERVAL = 30000;
```

**제거 안전성:** 데이터 변경은 포저(챗봇) 통해서만 발생하며, 포저가 데이터 수정 시 이미 `fetchData()` 호출됨. 수동 새로고침은 브라우저 기본 기능으로 충분.

---

## Issue 4: 식당 가이드에서 숙소 옵션 제외

### 변경
```javascript
// extractRestaurants() 내부
item.options.forEach(function(opt){
  var key = opt.name; if(!key) return;
  if(opt.loc === '숙소') return;  // 숙소 옵션 제외
  // ...
```

**제외 항목 (3개):** "숙소에서 간단히", "숙소에서 직접 조리", "숙소 바비큐"

일정 탭의 해당 일자 카드에서는 여전히 표시됨 (식당 가이드에서만 제외).

---

## Issue 5: 홈쿡 탭 신설

### 탭 구조 변경
```
변경 전: [일정] [장소] [식당] [숙소]
변경 후: [일정] [장소] [식당] [숙소] [홈쿡]
```

### 홈쿡 탭 콘텐츠

```
[홈쿡] 탭
├── 섹션 히어로 (Home Cook / 숙소 식사 가이드)
│
├── 아침 추천 (아코디언 카드들)
│   ├── 간편 아침 조리 (마트 구매, 메뉴/장보기 목록)
│   ├── 새벽배송 활용 (쿠팡/컬리)
│   └── 히로 전용 메뉴
│
├── 저녁 추천 (아코디언 카드들)
│   ├── 숙소 바비큐 (BBQ 데크 + 전기 그릴 기본 제공)
│   ├── 배달 음식 (배민 카테고리)
│   └── 밀키트 직접 조리
│
└── 배달/배송 서비스 안내 카드
    ├── 쿠팡 로켓프레시 — 가능성 높음
    ├── 컬리 샛별배송 — 가능성 매우 높음
    ├── 배달의민족 — 가능성 높음
    ├── 쿠팡이츠 — 확인 불가
    └── "여행 전 앱에서 주소 입력하여 확인하세요" 안내
```

### 데이터

홈쿡 탭 데이터는 **프론트엔드(patchGuideData 또는 별도 상수)**에서 하드코딩.
jsonbin 데이터 변경 불필요 — 이 정보는 일정 데이터가 아니라 정적 가이드 정보이므로.

```javascript
var HOME_COOK_DATA = {
  breakfast: [
    {
      title: '간편 아침 조리',
      desc: '홈플러스에서 장보기 시 함께 구매',
      items: ['잡곡 햇반', '즉석국 (된장/미역)', '계란', '김', '과일'],
      adultNote: '잡곡밥+국 조합이 든든',
      hiroNote: '흰쌀 으깬밥+국물, 바나나'
    },
    {
      title: '새벽배송 활용',
      desc: '전날 밤 주문 → 아침 도착',
      items: ['즉석죽 (비비고)', '계란', '우유', '과일', '아기 이유식'],
      services: ['쿠팡 로켓프레시 (자정 주문→7시)', '컬리 (23시 주문→8시)']
    }
  ],
  dinner: [
    {
      title: '숙소 바비큐',
      desc: '전 객실 BBQ 데크 + 전기 그릴 기본 제공',
      items: ['삼겹살/목살/양념갈비 (1인 200~300g)', '소시지', '쌈채소 세트', '양파/버섯/옥수수', '햇반/즉석 냉면'],
      buyAt: '홈플러스 경주점',
      hiroNote: '고기 잘게 자르기, 소시지 세로 반 가르기'
    },
    {
      title: '배달 음식',
      desc: '배달의민족에서 주문',
      categories: ['치킨', '피자', '중식 (짜장/탕수육)', '족발/보쌈'],
      note: '보문단지 인근 배달 가능. 정확한 범위는 앱에서 확인. 추가 배달비 발생 가능.'
    },
    {
      title: '밀키트 직접 조리',
      desc: '인덕션 + 조리도구 완비',
      items: ['부대찌개 밀키트', '샤브샤브 밀키트', '칼국수', '카레'],
      buyAt: '홈플러스 경주점'
    }
  ],
  deliveryServices: [
    {
      name: '쿠팡 로켓프레시',
      status: 'likely',
      statusText: '가능성 높음',
      hours: '밤 12시 주문 → 아침 7시 도착',
      evidence: '2025.6 기준 경주시 포함. 동 단위 차이 가능.',
      checkMethod: '쿠팡 앱에서 "경주시 북군4길 75" 입력'
    },
    {
      name: '컬리 샛별배송',
      status: 'likely',
      statusText: '가능성 매우 높음',
      hours: '밤 11시 주문 → 아침 8시 도착',
      evidence: '2024.2.29 경주시 서비스 개시 (공식 보도). 창원 물류센터 출발.',
      checkMethod: '컬리 앱에서 "경주시 북군4길 75" 입력'
    },
    {
      name: '배달의민족',
      status: 'yes',
      statusText: '가능성 높음',
      hours: '가게별 (보통 10:00~23:00)',
      evidence: '보문단지 인근 풀빌라 배달 후기 다수. 추가 배달비 발생 가능.',
      checkMethod: '배민 앱에서 위치 설정'
    },
    {
      name: '쿠팡이츠',
      status: 'unknown',
      statusText: '확인 불가',
      hours: '-',
      evidence: '경주시 서비스 여부 공식 확인 불가. 블로그/후기 0건.',
      checkMethod: '쿠팡이츠 앱에서 위치 설정'
    }
  ]
};
```

### 프론트엔드: renderHomeCook()

기존 디자인 시스템의 `section-hero` + `.card` + `<details>` 패턴을 그대로 사용.

---

## Issue 6: 출발 전 하위 탭 (일정 탭 내)

### 현재 구조
```
일정 탭: [1일차] [2일차] [3일차] [4일차] [5일차] [6일차]
```

### 변경 후
```
일정 탭: [출발 전] [1일차] [2일차] [3일차] [4일차] [5일차] [6일차]
```

### 구현 방식

**jsonbin 데이터에 dayNum: 0 추가:**
```json
{
  "days": [
    {
      "dayNum": 0,
      "date": "2026-02-18",
      "title": "출발 전 확인사항",
      "items": [
        {
          "id": "d0_check_coupang",
          "title": "쿠팡 앱에서 로켓프레시 확인",
          "desc": "배송지를 '경주시 북군4길 75'로 설정 → 로켓프레시 상품에 '새벽배송' 표시 확인",
          "cat": "todo",
          "status": "pending"
        },
        {
          "id": "d0_check_kurly",
          "title": "컬리 앱에서 샛별배송 확인",
          "desc": "배송지를 '경주시 북군4길 75'로 설정 → '샛별배송' 가능 표시 확인",
          "cat": "todo",
          "status": "pending"
        },
        {
          "id": "d0_check_baemin",
          "title": "배달의민족에서 배달 가능 음식점 탐색",
          "desc": "위치를 보문관광단지로 설정 → 주변 배달 가능 음식점 목록 확인",
          "cat": "todo",
          "status": "pending"
        },
        {
          "id": "d0_call_casa",
          "title": "까사멜로우 전화 확인",
          "desc": "010-3583-6648. 확인 사항: 전기 그릴 사양, 기본 조미료 범위, 새벽배송 수령 가능 여부",
          "cat": "todo",
          "status": "pending"
        }
      ]
    },
    {
      "dayNum": 1,
      "date": "2026-02-19",
      "title": "경주 도착 · 장보기 · 동궁과 월지",
      ...
    }
  ]
}
```

**renderDayTabs() 수정:**
```javascript
function renderDayTabs(){
  var tabs = document.getElementById('dayTabs');
  var days = travelData.days;
  tabs.innerHTML = '';
  days.forEach(function(day, idx){
    var tab = document.createElement('div');
    tab.className = 'day-tab' + (idx === activeDay ? ' active' : '');
    if(day.dayNum === 0){
      tab.innerHTML = '출발 전<span class="tab-date">' + formatTabDate(day.date) + '</span>';
    } else {
      tab.innerHTML = day.dayNum + '일차<span class="tab-date">' + formatTabDate(day.date) + '</span>';
    }
    tab.onclick = function(){ activeDay = idx; renderDayTabs(); renderDayContent() };
    tabs.appendChild(tab);
  });
  var activeTabEl = tabs.querySelector('.active');
  if(activeTabEl) activeTabEl.scrollIntoView({behavior:'smooth', inline:'center', block:'nearest'});
}
```

**renderDayContent() — 출발 전 탭 전용 레이아웃:**
dayNum === 0일 때 체크리스트 스타일로 렌더링. 기존 `renderItemCard()`를 재사용하되, `cat: 'todo'` 항목에 체크박스 스타일을 적용할 수 있음.

또는 기존 `status` 토글 (포저를 통한 done/pending 전환)을 그대로 활용 — 출발 전 확인을 완료하면 봇에게 "로켓프레시 확인 완료" 같이 말하면 됨.

---

## 리서치 결과 (배달/새벽배송)

> 까사멜로우 주소: **경주시 북군4길 75 (북군동)** — 보문관광단지 인근

### 서비스별 판정

| 서비스 | 판정 | 근거 수준 | 핵심 근거 |
|--------|------|----------|----------|
| **쿠팡 로켓프레시** | 가능성 높음 | 공식 지역 목록 | 2025.6 기준 경주시 포함 (bellanova4u.com). 동 단위 차이 가능 |
| **컬리 샛별배송** | 가능성 매우 높음 | 공식 보도자료 3건 | 2024.2.29 경주시 서비스 개시 (서울경제, 아주경제, 에너지경제) |
| **배달의민족** | 가능성 높음 | 간접 후기 다수 | 보문단지 인근 풀빌라에서 배달 주문 후기 존재. 추가 배달비 가능 |
| **쿠팡이츠** | 확인 불가 | 증거 없음 | 경주시 서비스 여부 공식 확인 불가. "경주 쿠팡이츠" 블로그 후기 0건 |

### 미확인 사항 (여행 전 직접 확인 필요)
- **쿠팡 로켓프레시**: 북군동(경주시 북군4길 75) 세부 배송 가능 여부 — 쿠팡 앱에서 주소 입력
- **컬리 샛별배송**: 동일 주소 배송 가능 여부 — 컬리 앱에서 주소 입력
- **배달의민족**: 보문단지 인근 실제 배달 가능 음식점 범위 — 배민 앱에서 위치 설정
- **쿠팡이츠**: 경주시 서비스 개통 여부 — 쿠팡이츠 앱에서 위치 설정
- **까사멜로우**: 전기 그릴 사양, 기본 조미료 범위, 새벽배송 수령 가능 여부 — 전화 010-3583-6648

> 위 확인 사항이 **출발 전 체크리스트**로 들어가는 항목들임.

### 까사멜로우 시설 (스테이폴리오 확인)

| 시설 | 구비 |
|------|------|
| 인덕션 | O |
| 냉장고 | O |
| 전자레인지 | O |
| 식기세척기 | O |
| 조리도구 + 기본 조미료 | O |
| 토스터기 | O |
| 캡슐커피머신 | O |
| 젖병소독기 | O |
| **BBQ 데크 + 전기 그릴** | **전 객실 기본 제공** |

### 리서치 출처

**배달/새벽배송:**
- [쿠팡 로켓프레시 가능 지역 총정리 2025.6](https://bellanova4u.com/entry/2025%EB%85%84-6%EC%9B%94-%EA%B8%B0%EC%A4%80-%EC%BF%A0%ED%8C%A1-%EB%A1%9C%EC%BC%93%ED%94%84%EB%A0%88%EC%8B%9C-%EC%A0%84%EA%B5%AD-%EC%84%9C%EB%B9%84%EC%8A%A4-%EA%B0%80%EB%8A%A5-%EC%A7%80%EC%97%AD-%EC%B4%9D%EC%A0%95%EB%A6%AC)
- [컬리, 경주 포항 샛별배송 개시 (서울경제)](https://www.sedaily.com/NewsView/2D5JA5C30E)
- [컬리 경주 포항 샛별배송 (아주경제)](https://www.ajunews.com/view/20240228142922982)
- [컬리 경주 포항 샛별배송 (에너지경제)](https://m.ekn.kr/view.php?key=20240228023256167)
- [쿠팡이츠 나무위키](https://namu.wiki/w/%EC%BF%A0%ED%8C%A1%EC%9D%B4%EC%B8%A0)

**숙소 시설:**
- [까사멜로우 - 스테이폴리오](https://www.stayfolio.com/findstay/casa-mellow)

---

## 구현 순서

```
Phase A — 즉시 수정 (Issues 1~4)
  ├── [1] index.html: renderPlaceDetail/renderPlaces에 g.placeName 우선 사용
  ├── [1] index.html: patchGuideData에 placeName 패치 추가
  ├── [2] index.html: 폰트 기본값 large, 테마 기본값 light
  ├── [3] index.html: setInterval 폴링 제거 + 변수 정리
  └── [4] index.html: extractRestaurants에 loc==='숙소' 필터

Phase B — 탭 확장 (Issues 5~6)
  ├── [5] index.html: 홈쿡 탭 추가 (HTML + renderHomeCook JS)
  ├── [5] index.html: HOME_COOK_DATA 상수 + 렌더링 함수
  ├── [6] jsonbin: days 배열 맨 앞에 dayNum:0 "출발 전" 추가
  └── [6] index.html: renderDayTabs에서 dayNum===0 처리
```

---

## 변경 파일 요약

| 파일 | Phase | 변경 |
|------|-------|------|
| `webapp/index.html` | A, B | placeName(1), 기본값(2), 폴링 제거(3), 식당 필터(4), 홈쿡 탭(5), 출발전 탭(6) |
| jsonbin 데이터 | B | days 배열에 dayNum:0 추가(6) |

---

## 리스크

| 리스크 | 대응 |
|--------|------|
| 폴링 제거 후 포저 외 경로로 데이터 변경 시 반영 안 됨 | 현재 데이터 변경 경로는 포저뿐. 수동 새로고침으로 충분 |
| 배달 서비스 정보가 여행 시점에 변경될 수 있음 | 출발 전 체크리스트에서 앱으로 직접 확인하도록 안내 |
| dayNum:0 추가 시 기존 코드에서 dayNum 기반 로직 오류 가능 | dayNum===0 분기 처리 필요한 곳 확인 (formatTabDate, URL 파라미터 등) |
| 숙소 식사 옵션을 식당 탭에서 제거하면 사용자가 못 찾을 수 있음 | 홈쿡 탭에 해당 정보가 상세히 존재 + 일정 탭에서는 여전히 표시 |
