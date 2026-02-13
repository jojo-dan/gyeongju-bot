#!/usr/bin/env python3
"""T-004 Phase 1-4: 리서치 결과를 JSON 스키마에 맞게 정리하여 jsonbin 데이터에 병합"""
import json
import os
import sys
import urllib.request

# 리서치 결과 데이터 (4개 배치 통합)
ENRICHMENT_DATA = {
    # === Batch 1: 황리단길 식당 ===
    "온목당": {
        "rating": 4.3,
        "ratingSource": "naver",
        "reviewCount": 850,
        "priceRange": "8,000~21,000",
        "menuDetail": [
            {"item": "맑은 한돈 곰탕", "price": 11000},
            {"item": "냉수육", "price": 21000},
            {"item": "곰탕 칼국수", "price": 12000}
        ],
        "mapUrl": "https://map.naver.com/p/search/온목당 경주",
        "category": "한식 · 곰탕",
        "phone": "0507-1363-9861",
        "hours": "11:00~21:30 (브레이크 16:00~17:00)"
    },
    "향화정": {
        "rating": 4.3,
        "ratingSource": "diningcode",
        "reviewCount": 1200,
        "priceRange": "13,500~29,900",
        "menuDetail": [
            {"item": "꼬막무침비빔밥(2인)", "price": 28500},
            {"item": "경주육회물회", "price": 13500},
            {"item": "해물파전", "price": 15000}
        ],
        "mapUrl": "https://map.naver.com/p/search/향화정 경주",
        "category": "한식 · 꼬막 · 육회물회",
        "phone": "0507-1359-8765",
        "hours": "11:00~21:30 (브레이크 15:00~17:00)"
    },
    "교동쌈밥": {
        "rating": 3.9,
        "ratingSource": "diningcode",
        "reviewCount": 77,
        "priceRange": "18,000~21,000",
        "menuDetail": [
            {"item": "한우 불고기 쌈밥", "price": 21000},
            {"item": "오리 불고기 쌈밥", "price": 19000},
            {"item": "돼지 불고기 쌈밥", "price": 18000}
        ],
        "mapUrl": "https://map.naver.com/p/search/별채반 교동쌈밥 경주",
        "category": "한식 · 쌈밥",
        "phone": "0507-1437-3324",
        "hours": "11:00~16:00, 17:00~21:00"
    },
    "경주원조콩국": {
        "rating": 4.4,
        "ratingSource": "naver",
        "reviewCount": 520,
        "priceRange": "7,000~13,000",
        "menuDetail": [
            {"item": "콩국(도넛+검은깨)", "price": 8000},
            {"item": "순두부찌개", "price": 12000},
            {"item": "콩국수 대", "price": 10000}
        ],
        "mapUrl": "https://map.naver.com/p/search/경주원조콩국",
        "category": "한식 · 콩국 · 순두부",
        "phone": "054-743-9643",
        "hours": "09:00~19:45 (일요일 휴무, 브레이크 16:30~17:00)"
    },
    "복길 경주본점": {
        "rating": 4.8,
        "ratingSource": "diningcode",
        "reviewCount": 1118,
        "priceRange": "12,000~44,000",
        "menuDetail": [
            {"item": "2인 세트", "price": 44000},
            {"item": "전복솥밥", "price": 17000},
            {"item": "고등어구이", "price": 12000}
        ],
        "mapUrl": "https://map.naver.com/p/search/복길 경주본점",
        "category": "한식 · 솥밥 · 전복요리",
        "phone": "054-748-3555",
        "hours": "10:30~21:00 (브레이크 16:00~17:00)"
    },
    "거송갈비찜": {
        "rating": 4.6,
        "ratingSource": "diningcode",
        "reviewCount": 380,
        "priceRange": "14,000~39,000",
        "menuDetail": [
            {"item": "소갈비찜(2인)", "price": 39000},
            {"item": "육회비빔밥", "price": 14000},
            {"item": "육회물회", "price": 14000}
        ],
        "mapUrl": "https://map.naver.com/p/search/거송갈비찜 황남점",
        "category": "한식 · 갈비찜",
        "phone": "0507-1414-0187",
        "hours": "11:00~21:00 (브레이크 15:30~17:00)"
    },

    # === Batch 2: 카페/보문/기타 ===
    "설월당": {
        "rating": 4.2,
        "ratingSource": "naver",
        "reviewCount": 350,
        "priceRange": "5,000~9,000",
        "menuDetail": [
            {"item": "아메리카노", "price": 5500},
            {"item": "경주빵크림라떼", "price": 7000}
        ],
        "mapUrl": "https://map.naver.com/p/search/설월당 경주",
        "category": "카페 · 디저트",
        "phone": "",
        "hours": "11:00~21:00"
    },
    "청수당 경주": {
        "rating": 4.4,
        "ratingSource": "naver",
        "reviewCount": 600,
        "priceRange": "7,000~18,000",
        "menuDetail": [
            {"item": "계란커피", "price": 7000},
            {"item": "딸기듬뿍 프로마주", "price": 18000}
        ],
        "mapUrl": "https://map.naver.com/p/search/청수당 경주",
        "category": "카페 · 한옥",
        "phone": "0507-1392-5612",
        "hours": "10:00~22:00 (L.O. 21:30)"
    },
    "올리브": {
        "rating": 4.1,
        "ratingSource": "naver",
        "reviewCount": 200,
        "priceRange": "5,000~8,000",
        "menuDetail": [
            {"item": "아메리카노", "price": 5000},
            {"item": "카페라떼", "price": 5500}
        ],
        "mapUrl": "https://map.naver.com/p/search/올리브 경주 황리단길",
        "category": "카페",
        "phone": "",
        "hours": ""
    },
    "산드레": {
        "rating": 4.5,
        "ratingSource": "naver",
        "reviewCount": 450,
        "priceRange": "18,000~35,000",
        "menuDetail": [
            {"item": "홍화밥 코스", "price": 25000},
            {"item": "약선 한정식", "price": 35000}
        ],
        "mapUrl": "https://map.naver.com/p/search/산드레 경주",
        "category": "한식 · 약선 한정식",
        "phone": "",
        "hours": "화~토 11:00~20:00 (일·월 휴무)"
    },
    "정수가성": {
        "rating": 4.3,
        "ratingSource": "naver",
        "reviewCount": 180,
        "priceRange": "12,000~25,000",
        "menuDetail": [
            {"item": "떡갈비 정식", "price": 15000},
            {"item": "한정식", "price": 25000}
        ],
        "mapUrl": "https://map.naver.com/p/search/정수가성 경주",
        "category": "한식 · 떡갈비",
        "phone": "",
        "hours": ""
    },
    "맷돌순두부": {
        "rating": 4.3,
        "ratingSource": "naver",
        "reviewCount": 400,
        "priceRange": "8,000~15,000",
        "menuDetail": [
            {"item": "순두부찌개", "price": 12000},
            {"item": "녹두전", "price": 13000},
            {"item": "통삼겹 수육", "price": 15000}
        ],
        "mapUrl": "https://map.naver.com/p/search/맷돌순두부 경주",
        "category": "한식 · 순두부",
        "phone": "054-620-9000",
        "hours": "08:00~21:00 (브레이크 16:00~17:00, 목요일 휴무)"
    },

    # === Batch 3: 불국사/보문 식당 ===
    "전주시골밥상": {
        "rating": 4.5,
        "ratingSource": "diningcode",
        "reviewCount": 150,
        "priceRange": "9,000~18,000",
        "menuDetail": [
            {"item": "제육볶음 정식", "price": 9000},
            {"item": "버섯불고기전골(B세트)", "price": 15000},
            {"item": "산채불고기+된장(A세트)", "price": 18000}
        ],
        "mapUrl": "https://map.naver.com/p/search/전주시골밥상 경주",
        "category": "한식 · 정식",
        "phone": "054-748-7183",
        "hours": "09:00~21:00"
    },
    "경주시락국밥": {
        "rating": 4.2,
        "ratingSource": "naver",
        "reviewCount": 320,
        "priceRange": "7,000~10,000",
        "menuDetail": [
            {"item": "시락국밥", "price": 7000},
            {"item": "수제 떡갈비", "price": 9000}
        ],
        "mapUrl": "https://map.naver.com/p/search/경주시락국밥 불국사",
        "category": "한식 · 국밥",
        "phone": "",
        "hours": "10:00~20:00 (브레이크 15:00~17:00)"
    },
    "조돌칼국수": {
        "rating": 4.3,
        "ratingSource": "diningcode",
        "reviewCount": 280,
        "priceRange": "7,500~13,000",
        "menuDetail": [
            {"item": "동죽칼국수", "price": 7500},
            {"item": "새우해물파전", "price": 13000},
            {"item": "물총조개탕", "price": 10000}
        ],
        "mapUrl": "https://map.naver.com/p/search/조돌칼국수 경주",
        "category": "한식 · 칼국수",
        "phone": "0507-1360-3752",
        "hours": "10:00~21:30 (브레이크 16:00~17:00)"
    },
    "바다속해물": {
        "rating": 4.5,
        "ratingSource": "diningcode",
        "reviewCount": 85,
        "priceRange": "45,000~75,000 (2인 기준)",
        "menuDetail": [
            {"item": "해물탕(2인)", "price": 45000},
            {"item": "조개찜(2인)", "price": 50000},
            {"item": "가리비찜(2인)", "price": 50000}
        ],
        "mapUrl": "https://map.naver.com/p/search/바다속해물 경주",
        "category": "해산물 · 조개찜",
        "phone": "0507-1480-2241",
        "hours": "12:00~23:00 (브레이크 14:00~17:00)"
    },
    "이조한정식": {
        "rating": 3.0,
        "ratingSource": "diningcode",
        "reviewCount": 45,
        "priceRange": "25,000~45,000",
        "menuDetail": [
            {"item": "B코스", "price": 25000},
            {"item": "A코스", "price": 35000},
            {"item": "정코스", "price": 45000}
        ],
        "mapUrl": "https://map.naver.com/p/search/이조한정식 경주",
        "category": "한정식",
        "phone": "054-775-3260",
        "hours": "11:00~21:00 (브레이크 15:00~17:00)"
    },
    "하연지": {
        "rating": 4.5,
        "ratingSource": "diningcode",
        "reviewCount": 92,
        "priceRange": "16,500~19,800",
        "menuDetail": [
            {"item": "원효상(연잎밥)", "price": 19800},
            {"item": "선덕상(공기밥)", "price": 16500},
            {"item": "연잎두부전", "price": 12000}
        ],
        "mapUrl": "https://map.naver.com/p/search/하연지 경주",
        "category": "한정식 · 연잎밥",
        "phone": "054-777-5432",
        "hours": "영업시간 유동적 (전화 확인 필요)"
    },

    # === Batch 4: 카페 ===
    "바실라(Basilla)": {
        "rating": 4.0,
        "ratingSource": "naver",
        "reviewCount": 400,
        "priceRange": "6,000~18,000",
        "menuDetail": [
            {"item": "아메리카노", "price": 6000},
            {"item": "바실랑떼", "price": 8000},
            {"item": "바실라 팥빙수", "price": 18000}
        ],
        "mapUrl": "https://map.naver.com/p/search/바실라 경주",
        "category": "카페",
        "phone": "054-621-8000",
        "hours": "평일 11:00~21:00, 주말 10:30~21:00"
    },
    "카페 메이플": {
        "rating": 4.2,
        "ratingSource": "naver",
        "reviewCount": 350,
        "priceRange": "5,000~12,000",
        "menuDetail": [
            {"item": "아메리카노", "price": 5500},
            {"item": "와플(하겐다즈)", "price": 11000}
        ],
        "mapUrl": "https://map.naver.com/p/search/카페메이플 경주",
        "category": "카페",
        "phone": "0507-1426-5962",
        "hours": "09:00~20:00 (L.O. 19:30)"
    },
    "내류사": {
        "rating": 4.3,
        "ratingSource": "naver",
        "reviewCount": 450,
        "priceRange": "5,500~10,000",
        "menuDetail": [
            {"item": "내류사 오렌지", "price": 7500},
            {"item": "카푸치노", "price": 6000},
            {"item": "블랙말차", "price": 6500}
        ],
        "mapUrl": "https://map.naver.com/p/search/내류사 경주",
        "category": "카페 · 베이커리",
        "phone": "054-746-1223",
        "hours": "10:00~21:00"
    },
    "아덴(Aden)": {
        "rating": 4.1,
        "ratingSource": "diningcode",
        "reviewCount": 520,
        "priceRange": "5,000~7,000",
        "menuDetail": [
            {"item": "아메리카노", "price": 5300},
            {"item": "카페라떼", "price": 5800},
            {"item": "투모로우 모카", "price": 6800}
        ],
        "mapUrl": "https://map.naver.com/p/search/아덴 경주 보문",
        "category": "카페",
        "phone": "054-774-2016",
        "hours": "10:00~23:00"
    },
    "엘로우(LLOW)": {
        "rating": 4.1,
        "ratingSource": "diningcode",
        "reviewCount": 680,
        "priceRange": "5,500~13,000",
        "menuDetail": [
            {"item": "아메리카노", "price": 5500},
            {"item": "크로플", "price": 13000}
        ],
        "mapUrl": "https://map.naver.com/p/search/엘로우 경주",
        "category": "카페",
        "phone": "0507-1436-1151",
        "hours": "10:00~22:00 (노키즈존)"
    },
}


def enrich_option(opt: dict) -> dict:
    """식당 option에 리서치 데이터를 병합"""
    name = opt.get("name", "")
    data = ENRICHMENT_DATA.get(name)
    if not data:
        return opt

    # 기존 필드는 유지하고 신규 필드만 추가
    enriched = dict(opt)
    for key in ["rating", "ratingSource", "reviewCount", "priceRange",
                 "menuDetail", "mapUrl", "category", "phone"]:
        if key in data and data[key]:
            enriched[key] = data[key]

    # hours: 리서치 데이터가 더 상세하면 덮어씀
    if data.get("hours") and (not opt.get("hours") or len(data["hours"]) > len(opt.get("hours", ""))):
        enriched["hours"] = data["hours"]

    return enriched


def main():
    # 현재 라이브 데이터 로드
    input_file = os.path.join(os.path.dirname(__file__), "..", "jsonbin_current.json")
    if not os.path.exists(input_file):
        print(f"ERROR: {input_file} not found. Run the Vercel API fetch first.")
        sys.exit(1)

    with open(input_file, "r") as f:
        data = json.load(f)

    # 각 day의 각 item의 각 option을 순회하며 데이터 보강
    enriched_count = 0
    skipped = []
    for day in data.get("days", []):
        for item in day.get("items", []):
            if "options" not in item:
                continue
            for i, opt in enumerate(item["options"]):
                name = opt.get("name", "")
                if name in ENRICHMENT_DATA:
                    item["options"][i] = enrich_option(opt)
                    enriched_count += 1
                elif name and name not in [
                    "숙소에서 간단히", "숙소 간편식", "숙소 간편식(전날 밥)",
                    "숙소에서 직접 조리", "대구에서 식사", "숙소 바비큐",
                    "경주에서 마지막 식사", "고속도로 휴게소"
                ]:
                    skipped.append(name)

    # meta 업데이트
    from datetime import datetime, timezone, timedelta
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).isoformat()
    data["meta"]["lastUpdated"] = now
    data["meta"]["updateNote"] = "T-004 Phase 1-1/1-2: 식당/카페 별점·메뉴·가격·지도URL 보강"

    # 결과 저장
    output_file = os.path.join(os.path.dirname(__file__), "..", "jsonbin_enriched.json")
    with open(output_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Enriched {enriched_count} restaurant options")
    if skipped:
        unique_skipped = list(set(skipped))
        print(f"Skipped (no data): {unique_skipped}")
    print(f"Output: {output_file}")

    return data


if __name__ == "__main__":
    main()
