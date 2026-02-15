# Design Tokens v2 — 경주봇 디자인 리뉴얼

> 작성일: 2026-02-15
> 소스: pencil.dev `.pen` 디자인 파일 (프레임 ST3ni / YAcg1)
> 상태: Draft

---

## 1. Color Tokens

### 1.1 Semantic Color Variables

```css
:root {
  /* ── Background ── */
  --bg:             #F7F7F7;
  --bg-card:        #FFFFFF;

  /* ── Text ── */
  --text-primary:   #111111;
  --text-secondary: #999999;
  --text-tertiary:  #555555;

  /* ── Border & Divider ── */
  --border:         #E5E5E5;
  --divider:        #EEEEEE;

  /* ── Accent: Red ── */
  --accent-red:     #C41E3A;
  --accent-red-bg:  rgba(196, 30, 58, 0.08);

  /* ── Accent: Blue ── */
  --accent-blue:    #0066CC;
  --accent-blue-bg: rgba(0, 102, 204, 0.08);

  /* ── Accent: Green ── */
  --accent-green:       #1A8754;
  --accent-green-bg:    rgba(26, 135, 84, 0.10);
  --accent-green-border: #1A8754;
}

[data-theme="dark"] {
  /* ── Background ── */
  --bg:             #111111;
  --bg-card:        #1A1A1A;

  /* ── Text ── */
  --text-primary:   #FFFFFF;
  --text-secondary: #666666;
  --text-tertiary:  #999999;

  /* ── Border & Divider ── */
  --border:         #2E2E2E;
  --divider:        #2E2E2E;

  /* ── Accent: Red ── */
  --accent-red:     #FF5C33;
  --accent-red-bg:  rgba(255, 92, 51, 0.12);

  /* ── Accent: Blue ── */
  --accent-blue:    #4D9AFF;
  --accent-blue-bg: rgba(77, 154, 255, 0.12);

  /* ── Accent: Green ── */
  --accent-green:       #2ECC71;
  --accent-green-bg:    rgba(46, 204, 113, 0.12);
  --accent-green-border: #2ECC71;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:             #111111;
    --bg-card:        #1A1A1A;
    --text-primary:   #FFFFFF;
    --text-secondary: #666666;
    --text-tertiary:  #999999;
    --border:         #2E2E2E;
    --divider:        #2E2E2E;
    --accent-red:     #FF5C33;
    --accent-red-bg:  rgba(255, 92, 51, 0.12);
    --accent-blue:    #4D9AFF;
    --accent-blue-bg: rgba(77, 154, 255, 0.12);
    --accent-green:       #2ECC71;
    --accent-green-bg:    rgba(46, 204, 113, 0.12);
    --accent-green-border: #2ECC71;
  }
}
```

### 1.2 Color Palette Reference

| Token | Light | Dark | 용도 |
|---|---|---|---|
| `--bg` | `#F7F7F7` | `#111111` | 페이지 배경 |
| `--bg-card` | `#FFFFFF` | `#1A1A1A` | 카드 배경 |
| `--text-primary` | `#111111` | `#FFFFFF` | 제목, 본문 |
| `--text-secondary` | `#999999` | `#666666` | 보조 텍스트, 라벨 |
| `--text-tertiary` | `#555555` | `#999999` | 중간 강조 텍스트 |
| `--border` | `#E5E5E5` | `#2E2E2E` | 카드/컴포넌트 테두리 |
| `--divider` | `#EEEEEE` | `#2E2E2E` | 메뉴 행 구분선 |
| `--accent-red` | `#C41E3A` | `#FF5C33` | 카테고리 뱃지, 강조 |
| `--accent-blue` | `#0066CC` | `#4D9AFF` | 지도 링크, 아이콘 |
| `--accent-green` | `#1A8754` | `#2ECC71` | 영업중 뱃지 |

---

## 2. Typography Scale

### 2.1 Font Stacks

```css
:root {
  --font-serif: 'Noto Serif KR', Georgia, serif;
  --font-mono:  'Noto Sans Mono', 'SF Mono', monospace;
}
```

**Google Fonts 로드:**

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700&family=Noto+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### 2.2 Type Scale Tokens

```css
:root {
  /* ── Serif Scale (Noto Serif KR) ── */
  --type-section-title-size:    24px;
  --type-section-title-weight:  700;
  --type-section-title-ls:      -0.5px;

  --type-restaurant-name-size:   20px;
  --type-restaurant-name-weight: 700;
  --type-restaurant-name-ls:     0;

  --type-alt-heading-size:      16px;
  --type-alt-heading-weight:    500;
  --type-alt-heading-ls:        0;

  --type-menu-name-size:        14px;
  --type-menu-name-weight:      400;
  --type-menu-name-ls:          0;

  /* ── Mono Scale (Noto Sans Mono) ── */
  --type-score-size:            16px;
  --type-score-weight:          600;

  --type-price-size:            13px;
  --type-price-weight:          500;

  --type-badge-size:            12px;
  --type-badge-weight:          600;

  --type-label-size:            12px;
  --type-label-weight:          500;

  --type-info-value-size:       12px;
  --type-info-value-weight:     400;

  --type-tag-size:              11px;
  --type-tag-weight:            400;
}
```

### 2.3 Typography Usage Matrix

| 용도 | Font | Size | Weight | Letter-spacing | Token Prefix |
|---|---|---|---|---|---|
| 섹션 타이틀 ("저녁식사") | Serif | 24px | 700 | -0.5px | `--type-section-title-*` |
| 식당 이름 | Serif | 20px | 700 | 0 | `--type-restaurant-name-*` |
| 대안 섹션 제목 | Serif | 16px | 500 | 0 | `--type-alt-heading-*` |
| 메뉴 이름 | Serif | 14px | 400 | 0 | `--type-menu-name-*` |
| 점수 | Mono | 16px | 600 | — | `--type-score-*` |
| 가격 | Mono | 13px | 500 | — | `--type-price-*` |
| 카테고리 뱃지 | Mono | 12px | 600 | — | `--type-badge-*` |
| 정보 라벨 / 지도 링크 | Mono | 12px | 500 | — | `--type-label-*` |
| 시간·서브텍스트·정보 값 | Mono | 12px | 400 | — | `--type-info-value-*` |
| 태그 / 상세보기 | Mono | 11px | 400 | — | `--type-tag-*` |

---

## 3. Spacing Scale

### 3.1 Base Spacing Tokens

```css
:root {
  --space-2:  2px;
  --space-3:  3px;
  --space-4:  4px;
  --space-8:  8px;
  --space-10: 10px;
  --space-12: 12px;
  --space-16: 16px;
  --space-20: 20px;
  --space-24: 24px;
}
```

### 3.2 Semantic Spacing Tokens

```css
:root {
  /* ── Card ── */
  --card-padding:         24px;
  --card-inner-gap:       16px;
  --card-margin-bottom:   12px;

  /* ── Header ── */
  --header-padding-v:     16px;
  --header-padding-h:     24px;

  /* ── Section Title ── */
  --section-title-padding: 20px 24px 24px 24px;

  /* ── Tags & Badges ── */
  --tag-padding:          4px 10px;
  --tag-gap:              8px;
  --badge-padding:        3px 8px;

  /* ── Info Rows ── */
  --info-row-gap:         8px;

  /* ── Menu Row ── */
  --menu-row-padding:     8px 0;

  /* ── Layout ── */
  --container-max-width:  440px;
  --container-padding-h:  16px;
}
```

### 3.3 Spacing Usage Map

| 컴포넌트 | 속성 | 값 | Token |
|---|---|---|---|
| 카드 | padding | 24px | `--card-padding` |
| 카드 내부 | gap | 16px | `--card-inner-gap` |
| contextHeader | padding | 16px 24px | `--header-padding-v` / `--header-padding-h` |
| sectionTitle 영역 | padding | 20px 24px 24px 24px | `--section-title-padding` |
| 태그 | padding | 4px 10px | `--tag-padding` |
| 태그 간 | gap | 8px | `--tag-gap` |
| 뱃지 | padding | 3px 8px | `--badge-padding` |
| 정보 행 | gap | 8px | `--info-row-gap` |
| 메뉴 행 | padding | 8px 0 | `--menu-row-padding` |

---

## 4. Component Tokens

### 4.1 Card

```css
:root {
  --card-bg:          var(--bg-card);
  --card-radius:      16px;
  --card-border:      1px solid var(--border);
  --card-shadow:      0 1px 3px rgba(0, 0, 0, 0.04),
                      0 4px 16px rgba(0, 0, 0, 0.03);
  --card-shadow-hover: 0 2px 8px rgba(0, 0, 0, 0.08),
                       0 8px 24px rgba(0, 0, 0, 0.05);
}

[data-theme="dark"] {
  --card-shadow:      0 1px 3px rgba(0, 0, 0, 0.2),
                      0 4px 16px rgba(0, 0, 0, 0.15);
  --card-shadow-hover: 0 2px 8px rgba(0, 0, 0, 0.3),
                       0 8px 24px rgba(0, 0, 0, 0.2);
}
```

**CSS 적용 예시:**

```css
.card {
  background: var(--card-bg);
  border-radius: var(--card-radius);
  border: var(--card-border);
  box-shadow: var(--card-shadow);
  padding: var(--card-padding);
  display: flex;
  flex-direction: column;
  gap: var(--card-inner-gap);
  transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  box-shadow: var(--card-shadow-hover);
}
```

### 4.2 Category Badge (카테고리 뱃지)

```css
:root {
  --badge-radius:     4px;
  --badge-font:       var(--font-mono);
  --badge-font-size:  var(--type-badge-size);   /* 12px */
  --badge-font-weight: var(--type-badge-weight); /* 600 */
}

.badge-category {
  display: inline-flex;
  align-items: center;
  padding: var(--badge-padding);         /* 3px 8px */
  border-radius: var(--badge-radius);
  font-family: var(--badge-font);
  font-size: var(--badge-font-size);
  font-weight: var(--badge-font-weight);
  background: var(--accent-red-bg);
  color: var(--accent-red);
  letter-spacing: 0.2px;
}
```

### 4.3 Status Badge (영업중/닫힘)

```css
.badge-status {
  display: inline-flex;
  align-items: center;
  padding: var(--badge-padding);
  border-radius: var(--badge-radius);
  font-family: var(--font-mono);
  font-size: var(--type-badge-size);
  font-weight: var(--type-badge-weight);
}

.badge-status--open {
  background: var(--accent-green-bg);
  color: var(--accent-green);
  border: 1px solid var(--accent-green-border);
}

.badge-status--closed {
  background: rgba(153, 153, 153, 0.1);
  color: var(--text-secondary);
}
```

### 4.4 Tag

```css
:root {
  --tag-radius: 6px;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: var(--tag-padding);           /* 4px 10px */
  border-radius: var(--tag-radius);
  font-family: var(--font-mono);
  font-size: var(--type-tag-size);       /* 11px */
  font-weight: var(--type-tag-weight);   /* 400 */
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-tertiary);
}

[data-theme="dark"] .tag {
  background: rgba(255, 255, 255, 0.06);
}
```

### 4.5 Divider (구분선)

```css
.divider {
  height: 1px;
  background: var(--divider);
  border: none;
  margin: 0;
}

/* 메뉴 행 사이 구분선 */
.menu-row + .menu-row {
  border-top: 1px solid var(--divider);
}
```

### 4.6 Info Row (정보 행)

```css
.info-row {
  display: flex;
  align-items: baseline;
  gap: var(--info-row-gap);
}

.info-row__label {
  font-family: var(--font-mono);
  font-size: var(--type-label-size);
  font-weight: var(--type-label-weight);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.info-row__value {
  font-family: var(--font-mono);
  font-size: var(--type-info-value-size);
  font-weight: var(--type-info-value-weight);
  color: var(--text-primary);
}
```

### 4.7 Map Link

```css
.map-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: var(--type-label-size);     /* 12px */
  font-weight: var(--type-label-weight); /* 500 */
  color: var(--accent-blue);
  text-decoration: none;
}

.map-link:hover {
  text-decoration: underline;
}
```

---

## 5. Icons

Lucide 아이콘 라이브러리 사용.

**CDN 로드:**

```html
<script src="https://unpkg.com/lucide@latest"></script>
```

또는 ESM import:

```js
import { MapPin, ChevronRight, Clock, Star, ExternalLink } from 'lucide';
```

### 사용 아이콘 목록

| 아이콘 | Lucide 이름 | 크기 | 색상 | 용도 |
|---|---|---|---|---|
| 위치 핀 | `map-pin` | 14px | `var(--accent-blue)` | 지도 링크 |
| 화살표 | `chevron-right` | 16px | `var(--text-secondary)` | 상세보기, 네비게이션 |
| 시계 | `clock` | 14px | `var(--text-secondary)` | 영업시간 |
| 별 | `star` | 14px | `var(--accent-red)` | 평점/점수 |
| 외부 링크 | `external-link` | 12px | `var(--accent-blue)` | 외부 링크 표시 |

### 아이콘 스타일 기본값

```css
.icon {
  width: 14px;
  height: 14px;
  stroke-width: 1.5;
  flex-shrink: 0;
}

.icon--sm {
  width: 12px;
  height: 12px;
}

.icon--lg {
  width: 16px;
  height: 16px;
}
```

---

## 6. Migration Mapping

### 6.1 Color Variable Migration

| v1 (현재) | v2 (신규) | 비고 |
|---|---|---|
| `--bg` (#FAF7F2) | `--bg` (#F7F7F7) | 따뜻한 크림 → 쿨 그레이 |
| `--bg-warm` (#F3EDE4) | — | 제거 (카드 내부 bg 역할 없음) |
| `--card` (#FFFFFF) | `--bg-card` (#FFFFFF) | 이름 변경 |
| `--card-hover` | — | 제거 (shadow로 대체) |
| `--hero` (#3D2E1F) | — | 제거 (hero 카드 패턴 변경) |
| `--hero-text` | — | 제거 |
| `--hero-dim` | — | 제거 |
| `--accent` (#C45D3E) | `--accent-red` (#C41E3A) | 테라코타 → 진홍 |
| `--accent-soft` | — | 제거 |
| `--accent-bg` | `--accent-red-bg` | 이름 변경 |
| `--sage` (#7B8F6B) | `--accent-green` (#1A8754) | 세이지 → 그린 |
| `--sage-bg` | `--accent-green-bg` | 이름 변경 |
| `--blue` (#4A6FA5) | `--accent-blue` (#0066CC) | 색상 변경 |
| `--blue-bg` | `--accent-blue-bg` | 이름 변경 |
| `--text` (#2C2218) | `--text-primary` (#111111) | 따뜻한 갈색 → 순수 검정 |
| `--text-mid` (#5C4F42) | `--text-tertiary` (#555555) | 이름 · 색상 변경 |
| `--text-light` (#8C7E72) | `--text-secondary` (#999999) | 역할 재배치 |
| `--text-muted` (#A89E94) | — | 제거 (`--text-secondary`로 통합) |
| `--border` (rgba) | `--border` (#E5E5E5) | rgba → 고정 hex |
| `--border-strong` | — | 제거 (`--border`로 통합) |

### 6.2 Font Migration

| v1 (현재) | v2 (신규) | 비고 |
|---|---|---|
| `--serif` (Spectral, KoPub Batang) | `--font-serif` (Noto Serif KR) | 한국어 최적화 세리프로 교체 |
| `--body` (= --serif) | — | 제거 (`--font-serif` 사용) |
| `--mono` (DM Mono) | `--font-mono` (Noto Sans Mono) | 모노스페이스 교체 |

### 6.3 Border Radius Migration

| v1 (현재) | v2 (신규) | 비고 |
|---|---|---|
| `--r-card` (20px) | `--card-radius` (16px) | 더 타이트한 radius |
| `--r-btn` (12px) | — | 뱃지/태그 radius로 대체 |
| `--r-tag` (6px) | `--tag-radius` (6px) | 동일 유지 |

### 6.4 Shadow Migration

| v1 (현재) | v2 (신규) | 비고 |
|---|---|---|
| `--shadow-card` | `--card-shadow` | 더 미세한 그림자 |
| `--shadow-card-hover` | `--card-shadow-hover` | 이름 변경 |
| `--shadow-hero` | — | 제거 (hero 카드 패턴 제거) |
| `--shadow-btn` | — | 제거 (플랫 버튼으로 변경) |

### 6.5 Decoration Migration

| v1 요소 | v2 상태 | 비고 |
|---|---|---|
| 그레인 텍스처 (`body::before`) | **제거** | 클린 모던 디자인으로 전환 |
| 장식 원형 오버레이 (`.display-card::before/after`) | **제거** | hero 카드 패턴 제거 |
| 액센트 라인 (`.header::after`) | **제거** | 미니멀 헤더로 전환 |

---

## 7. Design Direction Summary

### v1 → v2 전환 핵심

| 항목 | v1 (현재) | v2 (신규) |
|---|---|---|
| **톤** | 따뜻한 내추럴 (크림·테라코타) | 쿨 모던 (그레이·화이트) |
| **서체** | Spectral + KoPub Batang + DM Mono | Noto Serif KR + Noto Sans Mono |
| **색상 전략** | 3색 (terracotta·sage·blue) | 3색 (red·blue·green) |
| **장식** | 텍스처·오버레이·그라데이션 | 플랫·미니멀·보더 기반 |
| **카드** | 둥근(20px) + 진한 shadow | 타이트(16px) + 미세 shadow + border |
| **다크 모드** | 따뜻한 다크 (#1A1714) | 순수 다크 (#111111) |

### 적용 순서 권장

1. CSS 변수 정의 교체 (`:root` / `[data-theme="dark"]`)
2. Google Fonts 링크 교체
3. 컴포넌트별 클래스 업데이트 (카드 → 뱃지 → 태그 → 정보행)
4. 장식 요소 제거 (텍스처, 오버레이)
5. Lucide 아이콘 통합
6. 다크 모드 QA
