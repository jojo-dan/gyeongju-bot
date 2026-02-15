# Migration Roadmap v2 — 경주봇 디자인 리뉴얼

> 작성일: 2026-02-15
> 기반 문서: [design-tokens-v2.md](design-tokens-v2.md), [component-architecture-v2.md](component-architecture-v2.md)
> 여행일: 2026-02-19(목) ~ 02-24(화)
> **데드라인: 2026-02-18(화) 저녁 — 부모님 공유 전 완료**

---

## 1. 전략 요약

### 핵심 원칙

| 원칙 | 설명 |
|---|---|
| **빌드리스 유지** | Vite 등 도입 없음. 단일 index.html 구조 유지 |
| **점진적 교체** | 4단계 Phase, 각 Phase는 독립 배포 가능 |
| **비파괴적 접근** | 기존 기능(다크모드, 폰트사이즈, 위치 정렬) 100% 보존 |
| **데이터 스키마 무변경** | jsonbin.io 구조 그대로. 백엔드 수정 불필요 |
| **모바일 퍼스트** | 50~60대 부모님 + 모바일 브라우저 최적화 |

### 변경 규모 추정

| 항목 | 현재 | 리뉴얼 후 |
|---|---|---|
| index.html 총 줄수 | ~1,662줄 | ~1,800~2,000줄 |
| CSS 변수 수 | ~30개 | ~50개 |
| 렌더 함수 수 | ~15개 | ~25개 (atomic 추가) |
| 외부 폰트 | Spectral + KoPub + DM Mono | Noto Serif KR + Noto Sans Mono |
| 아이콘 | 인라인 SVG | Lucide CDN + 인라인 SVG 병행 |

---

## 2. Phase 정의

### Phase 1: 디자인 토큰 교체 (Day 1 — 2/16 일)

> **목표**: 색상·폰트·간격 변수만 교체. 시각적으로 즉시 변화 확인.

**작업 내용:**

1. **Google Fonts 링크 교체**
   - 기존: Spectral, DM Mono, KoPub Batang
   - 신규: Noto Serif KR (400, 500, 700) + Noto Sans Mono (400, 500, 600)

2. **CSS 변수 전면 교체** (`:root` + `[data-theme="dark"]` + `@media prefers-color-scheme`)
   - 색상: design-tokens-v2.md §1 전체 반영
   - 폰트: `--font-serif`, `--font-mono` 교체
   - 간격: semantic spacing tokens 추가
   - 카드: radius 20px → 16px, shadow 교체
   - 장식 제거: grain 텍스처, 장식 원형 오버레이, 액센트 라인

3. **기존 변수명 → 신규 변수명 치환**
   - `--serif` → `--font-serif`
   - `--mono` → `--font-mono`
   - `--text` → `--text-primary` (참조하는 모든 곳)
   - `--card` → `--bg-card`
   - 등 (design-tokens-v2.md §6 매핑 테이블 기준)

**산출물**: 폰트·색상이 새 디자인으로 바뀐 webapp
**검증**: 라이트/다크 모드 전환, 폰트사이즈 3단계, 모바일 Safari 확인
**리스크**: 낮음 — CSS 변수 치환만으로 JS 로직 무변경
**예상 작업량**: 2~3시간

---

### Phase 2: Atomic 컴포넌트 추가 (Day 1~2 — 2/16~17)

> **목표**: 재사용 가능한 atomic 렌더 함수 추가. 기존 함수 내부에서 호출 시작.

**작업 내용:**

1. **CSS 클래스 추가** (기존과 공존, 점진적 교체)
   - `.ctx-header`, `.sec-title`, `.menu-table`, `.info-table`
   - `.tag-row`, `.badge`, `.map-link`, `.chevron`
   - BEM-lite 네이밍: `.block__element--modifier`

2. **JS 렌더 함수 추가** (8개 신규)
   ```
   renderContextHeader(data) → string
   renderSectionTitle(text, sub?) → string
   renderMenuTable(menuDetail[]) → string
   renderInfoTable(entries[]) → string
   renderTagRow(tags[]) → string
   renderBadge(text, type) → string
   renderMapLink(url, text?) → string
   renderChevron() → string
   ```

3. **기존 함수에서 atomic 호출 시작**
   - `renderOptionCard()` 내부에서 `renderMenuTable()`, `renderInfoTable()`, `renderBadge()` 호출
   - `renderGuidePlace()` 내부에서 `renderInfoTable()`, `renderTagRow()`, `renderMapLink()` 호출
   - 기존 인라인 HTML을 atomic 함수 호출로 점진 교체

**산출물**: atomic 함수 8개 + CSS 클래스 + 기존 함수 내 부분 적용
**검증**: 식당 탭, 장소 탭에서 카드 렌더링 확인
**리스크**: 낮음 — 추가만, 기존 코드 삭제 없음
**예상 작업량**: 3~4시간

---

### Phase 3: Compound 컴포넌트 리팩토링 (Day 2~3 — 2/17~18)

> **목표**: 핵심 카드(식당, 장소, 일정) 전면 리팩토링. 새 디자인 레이아웃 적용.

**작업 내용:**

1. **RestaurantCard 리팩토링** (확장형 + 축소형)
   - 기존 `renderRestCards()` → `renderRestaurantCard()`
   - 구조: CardHeader(이름+점수+영업뱃지) → SubText → MenuTable → InfoTable → TagRow → MapLink
   - `.pen` 디자인과 1:1 매칭

2. **PlaceCard 리팩토링**
   - 기존 `renderGuidePlace()` → `renderPlaceCard()`
   - atomic 조합으로 재구성

3. **ScheduleItemCard 리팩토링**
   - 기존 `renderItemCard()` → `renderScheduleItemCard()`
   - ContextHeader + ItemTitle + OptionList 조합

4. **DayHeroCard 리팩토링**
   - 기존 `.display-card` → `.day-hero`
   - 새 톤(쿨 그레이 기반) 적용

5. **SectionHero 리팩토링**
   - 기존 `.section-hero` → `.sec-hero`
   - 장식 요소(원형 오버레이) 제거, 클린 디자인 적용

6. **AltSection 추가** (신규)
   - .pen 디자인의 대안 섹션 구현
   - "숙소에서 간단히 — 장봐온 재료 조리" 패턴

**산출물**: 핵심 카드 5종 + 신규 컴포넌트 1종 리팩토링 완료
**검증**: 전체 4탭 순회 + 다크모드 + 모바일 실기기
**리스크**: 중간 — 렌더 함수 교체로 UI 깨짐 가능. 탭별로 점진 적용 권장
**예상 작업량**: 4~5시간

---

### Phase 4: 정리 및 QA (Day 3 — 2/18)

> **목표**: 미사용 코드 정리, 최종 QA, 배포.

**작업 내용:**

1. **미사용 CSS 클래스 제거**
   - v1 클래스 중 v2로 대체된 것들 삭제
   - grain 텍스처, 장식 오버레이 CSS 제거

2. **미사용 JS 코드 정리**
   - 레거시 렌더 함수 중 완전히 대체된 것 삭제
   - Spectral/KoPub/DM Mono 폰트 참조 제거

3. **코드 정리**
   - 파일 내부 섹션 주석 정리 (component-architecture-v2.md §4 기준)
   - CSS 순서: TOKENS → RESET → LAYOUT → ATOMIC → COMPOUND → PAGE → UTILITIES

4. **최종 QA**
   - [ ] 라이트 모드 전 탭 확인
   - [ ] 다크 모드 전 탭 확인
   - [ ] 폰트사이즈 small/normal/large 확인
   - [ ] 모바일 Safari (iPhone) 실기기 테스트
   - [ ] 모바일 Chrome (Android) 테스트
   - [ ] 아코디언 열기/닫기 동작
   - [ ] 위치 기반 거리 표시 동작
   - [ ] 30초 폴링 데이터 갱신 확인
   - [ ] 테마 토글 + localStorage 유지 확인

5. **Vercel 배포**
   - main 브랜치 머지 후 Vercel 자동 배포
   - 부모님 공유 전 최종 확인

**산출물**: 프로덕션 배포 완료
**검증**: QA 체크리스트 전항 통과
**리스크**: 낮음 — 정리/삭제만
**예상 작업량**: 2~3시간

---

## 3. 일정표

```
2/15(토) ── 오늘 ──
  ✅ 디자인 파일 분석
  ✅ 디자인 토큰 명세서 작성
  ✅ 컴포넌트 아키텍처 설계
  ✅ 마이그레이션 로드맵 작성

2/16(일)
  🔵 Phase 1: 디자인 토큰 교체 (오전)
  🔵 Phase 2: Atomic 컴포넌트 추가 (오후~)

2/17(월)
  🔵 Phase 2: Atomic 적용 마무리 (오전)
  🟡 Phase 3: Compound 리팩토링 시작 (오후~)

2/18(화)
  🟡 Phase 3: Compound 리팩토링 마무리 (오전)
  🟢 Phase 4: 정리 + QA + 배포 (오후)
  📌 부모님 공유 가능 상태

2/19(목) ── 여행 출발 ──
```

---

## 4. 리스크 관리

| 리스크 | 확률 | 영향 | 대응 |
|---|---|---|---|
| Phase 3에서 UI 깨짐 | 중 | 중 | 탭 단위로 점진 적용. 문제 시 해당 탭만 롤백 |
| Noto Serif KR 로딩 느림 | 저 | 저 | `font-display: swap` + preconnect 적용 |
| 다크모드 색상 대비 부족 | 저 | 중 | QA에서 WCAG AA 기준 체크 |
| 일정 지연 | 중 | 고 | Phase 3를 식당탭만 우선 적용, 나머지는 여행 후 |
| 모바일 Safari 렌더링 차이 | 저 | 중 | 실기기 테스트 필수, `-webkit-` 접두사 확인 |

### 최소 배포 기준 (Fallback Plan)

Phase 3까지 완료하지 못할 경우, **Phase 2까지만으로도 배포 가능**:
- Phase 1: 새 색상/폰트 적용 → 시각적 개선 체감
- Phase 2: atomic 함수 적용 → 식당 카드 개선
- Phase 3 미완: 기존 레이아웃 유지하되 새 토큰으로 렌더 → 충분히 "개선된" 느낌

---

## 5. 호환성 체크리스트

### 기존 기능 보존 확인

| 기능 | 메커니즘 | Phase | 보존 방법 |
|---|---|---|---|
| 다크 모드 | `data-theme` + CSS 변수 + localStorage | 1 | 변수명만 교체, 메커니즘 동일 |
| 폰트 크기 조절 | `data-fontsize` + `--delta` | 1 | calc() 패턴 유지 |
| 위치 기반 정렬 | Geolocation API + `distKm` 필드 | 3 | 렌더 함수 내 로직 이식 |
| 30초 데이터 폴링 | `setInterval` + fetch `/api/data` | — | 무변경 |
| 아코디언 카드 | `<details>` + `<summary>` | 3 | HTML 패턴 유지 |
| 탭 네비게이션 | `switchTab()` + `activeTab` 전역 | 3 | 함수명만 리팩토링 |
| 테마 아이콘 토글 | `toggleTheme()` + SVG 교체 | — | 무변경 |
| 식당 필터링/정렬 | `applyRestFilters()` + 서브탭 | 3 | 로직 이식 |
| 방문 상태 표시 | `data-visited` + CSS | 3 | 클래스명만 교체 |

### 데이터 구조 (무변경)

jsonbin.io 스키마 변경 없음:
- `days[].items[].options[]` 구조 그대로
- `rating`, `hours`, `price`, `dad`, `hiro` 필드 그대로
- `menuDetail[]` 추가 데이터는 `patchGuideData()`에서 하드코딩 주입 (기존 방식 유지)

### 백엔드 변경 (없음)

- `src/` Python 코드: 변경 없음
- `webapp/api/`: 변경 없음
- VPS 봇 서비스: 재시작 불필요

---

## 6. 브랜치 전략

```
main (현재 프로덕션)
 └── work/T-005-design-v2 (리뉴얼 작업 브랜치)
      ├── commit: Phase 1 — 디자인 토큰 교체
      ├── commit: Phase 2 — atomic 컴포넌트 추가
      ├── commit: Phase 3 — compound 리팩토링
      └── commit: Phase 4 — 정리 + QA
```

- 티켓: `T-005` (신규 생성 필요)
- Phase별 커밋으로 롤백 용이성 확보
- Phase 2 완료 시점에서 중간 배포 가능 (fallback)

---

## 7. 참고 문서

| 문서 | 경로 | 용도 |
|---|---|---|
| 디자인 토큰 명세서 | `docs/design-tokens-v2.md` | Phase 1 CSS 변수 교체 시 참조 |
| 컴포넌트 아키텍처 | `docs/component-architecture-v2.md` | Phase 2~3 구현 시 참조 |
| 현재 디자인 시스템 | `docs/UI_DESIGN_SYSTEM.md` | v1 → v2 매핑 시 참조 |
| UX 기획서 | `docs/T-004-overview-guide-spec.md` | 요구사항 확인 |
| 디자인 원본 | `docs/gyeongjubot-designref-1` | .pen 파일 (pencil.dev) |
