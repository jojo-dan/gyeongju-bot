#!/usr/bin/env python3
"""
경주 여행 데이터 검증 스크립트
사용법: python verify_trip_data.py [JSON 파일 경로]
       python verify_trip_data.py --from-jsonbin

jsonbin.io에서 직접 가져오거나, 로컬 JSON 파일을 검증한다.
"""

import json
import sys
import os

# ============================================================
# 검증 기준 데이터 — 반드시 포함되어야 하는 장소들
# ============================================================

# 아내가 추가한 20개 장소
WIFE_LIST = {
    "경주동궁원":    {"aliases": ["경주 동궁원", "동궁원"], "expected_in": "items", "id_hint": "d5_donggungwon"},
    "동궁과월지":    {"aliases": ["동궁과 월지", "동궁월지"], "expected_in": "items", "id_hint": "d1_donggung,d2_donggung"},
    "대릉원":       {"aliases": ["대릉원(천마총)", "천마총"], "expected_in": "items", "id_hint": "d2_daereungwon"},
    "경주어보":      {"aliases": [], "expected_in": "options", "id_hint": "d2_lunch"},
    "소옥":         {"aliases": [], "expected_in": "options", "id_hint": "d2_dinner"},
    "프리제커피 브루어스": {"aliases": ["프리제커피", "프리제"], "expected_in": "options", "id_hint": "d2_cafe"},
    "금복식당":      {"aliases": [], "expected_in": "options", "id_hint": "d3_dinner"},
    "정록쌈밥":      {"aliases": [], "expected_in": "options", "id_hint": "d2_lunch"},
    "야드":         {"aliases": ["야드(Yard)", "Yard"], "expected_in": "options", "id_hint": "d5_cafe"},
    "꼬푸":         {"aliases": [], "expected_in": "options", "id_hint": "d2_cafe"},
    "산드레":       {"aliases": [], "expected_in": "options", "id_hint": "d2_dinner"},
    "아리랑식당":    {"aliases": [], "expected_in": "options", "id_hint": "d2_dinner,d3_dinner"},
    "반월성한우":    {"aliases": [], "expected_in": "options", "id_hint": "d1_dinner,d5_dinner"},
    "신라제면":      {"aliases": [], "expected_in": "markdown_only", "id_hint": "N/A (히로 부적합)"},
    "복길":         {"aliases": [], "expected_in": "options", "id_hint": "d2_lunch"},
    "맷돌순두부":    {"aliases": [], "expected_in": "options", "id_hint": "d3_dinner,d5_lunch"},
    "사랑의소아청소년과": {"aliases": ["소아청소년과", "사랑의소아"], "expected_in": "contacts", "id_hint": "reference.contacts"},
    "홈플러스":      {"aliases": ["홈플러스 경주점", "홈플러스 메가푸드마켓"], "expected_in": "items", "id_hint": "d1_shop"},
    "한살림":       {"aliases": ["한살림 경주매장"], "expected_in": "items", "id_hint": "d1_shop (desc)"},
    "까사멜로우":    {"aliases": ["까사멜로우풀빌라", "Casa Mellow"], "expected_in": "items", "id_hint": "d1_checkin"},
}

# 기존 계획에 포함된 식당/카페 (누락되면 안 됨)
ORIGINAL_RESTAURANTS = [
    "온목당", "수리산 정식점", "향화정", "경주원조콩국",
    "거송갈비찜", "정수가성", "전주시골밥상",
    "바다속해물", "이조한정식", "하연지", "조돌칼국수",
    "소향몽", "해물왕창",
]

ORIGINAL_CAFES = [
    "설월당", "청수당 경주", "올리브",
    "아덴", "엘로우",
    "바실라", "카페 메이플", "내류사",
]

# 구조 검증: 각 Day에 반드시 있어야 하는 item ID
REQUIRED_ITEM_IDS = {
    1: ["d1_move", "d1_shop", "d1_checkin", "d1_dinner", "d1_donggung"],
    2: ["d2_daereungwon", "d2_lunch", "d2_gyochon", "d2_cafe", "d2_dinner", "d2_donggung"],
    3: ["d3_bulguksa", "d3_lunch", "d3_cafe", "d3_dinner", "d3_prep"],
    4: ["d4_depart", "d4_marathon", "d4_family_wait", "d4_dinner"],
    5: ["d5_bomun", "d5_lunch", "d5_cafe", "d5_donggungwon", "d5_dinner"],
    6: ["d6_checkout", "d6_museum", "d6_lunch", "d6_return"],
}

# 식사 항목별 최소 옵션 수
MIN_OPTIONS = {
    "d1_dinner": 4,   # 반월성한우, 온목당, 수리산, 숙소
    "d2_lunch":  5,    # 복길, 경주어보, 향화정, 정록쌈밥, 경주원조콩국
    "d2_cafe":   5,    # 설월당, 청수당, 올리브, 프리제커피, 꼬푸
    "d2_dinner": 5,    # 산드레, 거송갈비찜, 정수가성, 아리랑, 소옥
    "d3_lunch":  2,    # 전주시골밥상, 곰탕집
    "d3_cafe":   3,    # 바실라, 메이플, 내류사
    "d3_dinner": 4,    # 숙소조리, 맷돌순두부, 아리랑, 금복식당
    "d4_dinner": 4,    # 바다속해물, 하연지, 대구식사, 숙소바비큐
    "d5_lunch":  3,    # 맷돌순두부, 조돌칼국수, 정수가성
    "d5_cafe":   3,    # 아덴, 엘로우, 야드
    "d5_dinner": 4,    # 바다속해물, 이조한정식, 하연지, 반월성한우
    "d6_lunch":  2,    # 경주 마지막식사, 휴게소
}


# ============================================================
# 검증 함수들
# ============================================================

def load_data(source):
    """JSON 데이터를 로드한다."""
    if source == "--from-jsonbin":
        import requests
        BIN_ID = os.environ.get("JSONBIN_BIN_ID", "698aa0ec43b1c97be973168e")
        API_KEY = os.environ.get("JSONBIN_API_KEY", "")
        if not API_KEY:
            print("⚠️  JSONBIN_API_KEY 환경변수가 설정되지 않음. .env 파일을 확인하세요.")
            sys.exit(1)
        r = requests.get(
            f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest",
            headers={"X-Master-Key": API_KEY}
        )
        r.raise_for_status()
        return r.json()["record"]
    else:
        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)


def flatten_text(data):
    """JSON 전체를 문자열로 평탄화 (검색용)."""
    return json.dumps(data, ensure_ascii=False)


def find_in_data(data, name, aliases):
    """데이터에서 이름 또는 별칭이 존재하는지 확인."""
    text = flatten_text(data)
    all_names = [name] + aliases
    for n in all_names:
        if n in text:
            return True, n
    return False, None


def get_all_items(data):
    """모든 day의 items를 {id: item} 딕셔너리로."""
    items = {}
    for day in data.get("days", []):
        for item in day.get("items", []):
            items[item["id"]] = item
    return items


def get_option_names(item):
    """item의 options에서 name 목록 추출."""
    return [opt.get("name", "") for opt in item.get("options", [])]


def verify_structure(data):
    """기본 구조 검증."""
    errors = []
    warnings = []

    # meta 확인
    if "meta" not in data:
        errors.append("meta 필드 없음")
    if "days" not in data:
        errors.append("days 필드 없음")
        return errors, warnings

    if len(data["days"]) != 6:
        errors.append(f"days 배열 길이: {len(data['days'])} (6이어야 함)")

    # reference 확인
    if "reference" not in data:
        errors.append("reference 필드 없음")
    else:
        ref = data["reference"]
        if "contacts" not in ref:
            errors.append("reference.contacts 없음")
        if "shopping" not in ref:
            errors.append("reference.shopping 없음")
        if "distances" not in ref:
            warnings.append("reference.distances 없음")

    # 각 Day의 item ID 확인
    items = get_all_items(data)
    for day_num, required_ids in REQUIRED_ITEM_IDS.items():
        for rid in required_ids:
            if rid not in items:
                errors.append(f"Day {day_num}: item '{rid}' 누락")

    return errors, warnings


def verify_wife_list(data):
    """아내 리스트 20개 장소 검증."""
    results = []
    items = get_all_items(data)

    for place, info in WIFE_LIST.items():
        found, matched_name = find_in_data(data, place, info["aliases"])

        if info["expected_in"] == "markdown_only":
            # 신라제면처럼 JSON에 없어도 되는 항목
            results.append({
                "place": place,
                "status": "SKIP",
                "note": "마크다운에만 포함 (JSON 불필요)",
            })
            continue

        if found:
            results.append({
                "place": place,
                "status": "OK",
                "note": f"'{matched_name}'으로 발견",
            })
        else:
            results.append({
                "place": place,
                "status": "MISSING",
                "note": f"기대 위치: {info['id_hint']}",
            })

    return results


def verify_original_list(data):
    """기존 계획 식당/카페 누락 검증."""
    results = []
    text = flatten_text(data)

    for name in ORIGINAL_RESTAURANTS:
        if name in text:
            results.append({"place": name, "type": "식당", "status": "OK"})
        else:
            results.append({"place": name, "type": "식당", "status": "MISSING"})

    for name in ORIGINAL_CAFES:
        # 일부 카페는 부분 이름으로 검색
        found = name in text
        if not found:
            # 짧은 이름으로 재검색
            short = name.split("(")[0].strip()
            found = short in text
        results.append({
            "place": name,
            "type": "카페",
            "status": "OK" if found else "MISSING",
        })

    return results


def verify_options_count(data):
    """각 식사/카페 항목의 옵션 수 확인."""
    results = []
    items = get_all_items(data)

    for item_id, min_count in MIN_OPTIONS.items():
        if item_id not in items:
            results.append({
                "id": item_id,
                "status": "MISSING_ITEM",
                "expected": min_count,
                "actual": 0,
            })
            continue

        options = items[item_id].get("options", [])
        actual = len(options)
        if actual >= min_count:
            results.append({
                "id": item_id,
                "status": "OK",
                "expected": min_count,
                "actual": actual,
            })
        else:
            results.append({
                "id": item_id,
                "status": "SHORT",
                "expected": min_count,
                "actual": actual,
                "names": [o.get("name", "?") for o in options],
            })

    return results


def verify_dietary_tags(data):
    """식사 옵션에 dad/hiro 태그가 있는지 확인."""
    errors = []
    items = get_all_items(data)

    for item_id, item in items.items():
        if item.get("cat") != "meal":
            continue
        for opt in item.get("options", []):
            name = opt.get("name", "?")
            if "dad" not in opt:
                errors.append(f"{item_id} > {name}: 'dad' 태그 없음")
            if "hiro" not in opt:
                errors.append(f"{item_id} > {name}: 'hiro' 태그 없음")

    return errors


def verify_contacts(data):
    """비상 연락처 확인."""
    contacts = data.get("reference", {}).get("contacts", [])
    names = [c.get("name", "") for c in contacts]

    results = []
    required = ["경주시 관광안내", "까사멜로우", "사랑의소아청소년과"]
    for req in required:
        found = any(req in n for n in names)
        results.append({"name": req, "status": "OK" if found else "MISSING"})

    return results


# ============================================================
# 메인
# ============================================================

def main():
    source = sys.argv[1] if len(sys.argv) > 1 else None
    if not source:
        # 기본 경로 시도
        candidates = [
            "경주여행_데이터.json",
            "data/trip_data.json",
            "trip_data.json",
        ]
        for c in candidates:
            if os.path.exists(c):
                source = c
                break
        if not source:
            print("사용법: python verify_trip_data.py <JSON파일경로>")
            print("       python verify_trip_data.py --from-jsonbin")
            sys.exit(1)

    print(f"📂 데이터 소스: {source}")
    print("=" * 60)

    data = load_data(source)

    # 1. 구조 검증
    print("\n[1/6] 기본 구조 검증")
    print("-" * 40)
    errors, warnings = verify_structure(data)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    if warnings:
        for w in warnings:
            print(f"  ⚠️  {w}")
    if not errors and not warnings:
        print("  ✅ 구조 정상")
    struct_pass = len(errors) == 0

    # 2. 아내 리스트 검증
    print("\n[2/6] 아내 리스트 20개 장소 검증")
    print("-" * 40)
    wife_results = verify_wife_list(data)
    wife_ok = sum(1 for r in wife_results if r["status"] == "OK")
    wife_skip = sum(1 for r in wife_results if r["status"] == "SKIP")
    wife_miss = sum(1 for r in wife_results if r["status"] == "MISSING")
    for r in wife_results:
        icon = {"OK": "✅", "SKIP": "⏭️", "MISSING": "❌"}[r["status"]]
        print(f"  {icon} {r['place']}: {r['note']}")
    print(f"\n  결과: {wife_ok} OK / {wife_skip} 스킵 / {wife_miss} 누락")

    # 3. 기존 식당/카페 검증
    print("\n[3/6] 기존 계획 식당·카페 검증")
    print("-" * 40)
    orig_results = verify_original_list(data)
    orig_miss = [r for r in orig_results if r["status"] == "MISSING"]
    if orig_miss:
        for r in orig_miss:
            print(f"  ❌ {r['place']} ({r['type']})")
    else:
        print(f"  ✅ 기존 {len(orig_results)}개 장소 모두 존재")

    # 4. 옵션 수 검증
    print("\n[4/6] 식사·카페 옵션 수 검증")
    print("-" * 40)
    opt_results = verify_options_count(data)
    opt_short = [r for r in opt_results if r["status"] in ("SHORT", "MISSING_ITEM")]
    if opt_short:
        for r in opt_short:
            print(f"  ❌ {r['id']}: {r['actual']}개 (최소 {r['expected']}개 필요)")
            if "names" in r:
                print(f"     현재: {', '.join(r['names'])}")
    else:
        print(f"  ✅ 전체 {len(opt_results)}개 항목 옵션 수 충족")

    # 5. 식이 태그 검증
    print("\n[5/6] 식이 태그 (dad/hiro) 검증")
    print("-" * 40)
    diet_errors = verify_dietary_tags(data)
    if diet_errors:
        for e in diet_errors[:10]:  # 최대 10개만
            print(f"  ❌ {e}")
        if len(diet_errors) > 10:
            print(f"  ... 외 {len(diet_errors) - 10}건")
    else:
        print("  ✅ 모든 식사 옵션에 dad/hiro 태그 존재")

    # 6. 비상 연락처 검증
    print("\n[6/6] 비상 연락처 검증")
    print("-" * 40)
    contact_results = verify_contacts(data)
    for r in contact_results:
        icon = "✅" if r["status"] == "OK" else "❌"
        print(f"  {icon} {r['name']}")

    # 최종 요약
    print("\n" + "=" * 60)
    total_issues = (
        len(errors) + wife_miss + len(orig_miss) +
        len(opt_short) + len(diet_errors) +
        sum(1 for r in contact_results if r["status"] == "MISSING")
    )
    if total_issues == 0:
        print("🎉 전체 검증 통과! 모든 데이터가 정상입니다.")
    else:
        print(f"⚠️  총 {total_issues}건의 이슈가 발견되었습니다.")

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
