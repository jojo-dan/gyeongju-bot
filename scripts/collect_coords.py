#!/usr/bin/env python3
"""
경주 여행 데이터 좌표 수집 스크립트.

여행 JSON 내 장소(음식점/카페/관광지)의 위치 좌표(lat/lng)를
수집하여 jsonbin 데이터에 반영한다.

사용법:
    python scripts/collect_coords.py --dry-run    # 결과만 출력 (jsonbin 변경 없음)
    python scripts/collect_coords.py --apply       # jsonbin에 실제 반영
    python scripts/collect_coords.py --kakao       # Kakao REST API로 검증 (API 키 필요)
"""

import argparse
import json
import logging
import os
import sys
from typing import Optional

import requests
from dotenv import load_dotenv

# 프로젝트 루트의 .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# 타임아웃 (초)
REQUEST_TIMEOUT = 15

# ============================================================
# 알려진 장소 좌표 딕셔너리
# 출처: 경주문화관광(gyeongju.go.kr), 네이버지도, 카카오맵 등
# "미확인" 표시가 있는 좌표는 근접 장소 기반 추정값
# ============================================================
KNOWN_COORDS: dict[str, dict] = {
    # --- 식당 ---
    "온목당": {
        "lat": 35.8378,
        "lng": 129.2088,
        "address": "경주시 사정로57번길 6",
        "note": "미확인 - 향화정(같은 골목 57번길) 기반 추정",
    },
    "수리산 정식점": {
        "lat": 35.8371,
        "lng": 129.2100,
        "address": "경주시 황리단길 인근",
        "note": "미확인 - 황리단길 중심부 기반 추정",
    },
    "향화정": {
        "lat": 35.8380366087077,
        "lng": 129.209183921076,
        "address": "경주시 사정로57번길 17",
        "note": "경주문화관광 공식 좌표",
    },
    "교동쌈밥": {
        "lat": 35.8343,
        "lng": 129.2128,
        "address": "경주시 첨성로 77",
        "note": "미확인 - 황남동 첨성로 인근 추정",
    },
    "경주원조콩국": {
        "lat": 35.8334489053257,
        "lng": 129.214714928085,
        "address": "경주시 첨성로 113",
        "note": "경주문화관광 공식 좌표",
    },
    "거송갈비찜": {
        "lat": 35.8359998835662,
        "lng": 129.211549103414,
        "address": "경주시 포석로1068번길 20-2",
        "note": "경주문화관광 공식 좌표",
    },
    "정수가성": {
        "lat": 35.8100,
        "lng": 129.3042,
        "address": "경주시 보불로 318 (하동)",
        "note": "미확인 - 보불로 기반 추정 (불국사 근처)",
    },
    "전주시골밥상": {
        "lat": 35.7900,
        "lng": 129.3310,
        "address": "경주시 불국사 인근",
        "note": "미확인 - 불국사 인근 추정",
    },
    "불국사 인근 곰탕집": {
        "lat": 35.7880,
        "lng": 129.3320,
        "address": "경주시 불국사 인근",
        "note": "미확인 - 불국사 인근 추정",
    },
    "산드레": {
        "lat": 35.8096347883772,
        "lng": 129.306279230268,
        "address": "경주시 보불로 299-5 (하동)",
        "note": "경주문화관광 공식 좌표",
    },
    "바다속해물": {
        "lat": 35.8420,
        "lng": 129.2250,
        "address": "경주시 동천로93번길 4 (동천동)",
        "note": "미확인 - 동천동 인근 추정",
    },
    "하연지": {
        "lat": 35.82394889574371,
        "lng": 129.21099774274853,
        "address": "경주시 포석로 932-4",
        "note": "경주문화관광 공식 좌표",
    },
    "이조한정식": {
        "lat": 35.8404848637853,
        "lng": 129.248774741049,
        "address": "경주시 숲머리길 136 (보문동)",
        "note": "경주문화관광 공식 좌표 (현재 고도벌한정식)",
    },
    "맷돌순두부": {
        "lat": 35.833012837872296,
        "lng": 129.21337820897398,
        "address": "경주시 황남동 (황남맷돌순두부)",
        "note": "경주문화관광 공식 좌표 (황남맷돌순두부)",
    },
    "조돌칼국수": {
        "lat": 35.8511496998376,
        "lng": 129.261750324885,
        "address": "경주시 북군길 3-6 (북군동)",
        "note": "경주문화관광 공식 좌표",
    },
    # --- 카페 ---
    "설월당": {
        "lat": 35.8340,
        "lng": 129.2140,
        "address": "경주시 첨성로81번길 22-13",
        "note": "미확인 - 첨성대/대릉원 인접 추정",
    },
    "청수당 경주": {
        "lat": 35.8342,
        "lng": 129.2138,
        "address": "경주시 첨성로81번길 21-1",
        "note": "미확인 - 설월당과 같은 골목 기반 추정",
    },
    "올리브": {
        "lat": 35.8373690465692,
        "lng": 129.209055300937,
        "address": "경주시 사정로57번길 7-6",
        "note": "경주문화관광 공식 좌표",
    },
    "바실라(Basilla)": {
        "lat": 35.8050,
        "lng": 129.2960,
        "address": "경주시 하동못안길 88",
        "note": "미확인 - 하동 저수지 인근 추정",
    },
    "카페 메이플": {
        "lat": 35.7847193812723,
        "lng": 129.329596054508,
        "address": "경주시 영불로 262",
        "note": "경주문화관광 공식 좌표",
    },
    "내류사": {
        "lat": 35.7870,
        "lng": 129.3300,
        "address": "경주시 불국사 인근",
        "note": "미확인 - 불국사 인근 한옥 카페 추정",
    },
    "아덴(Aden)": {
        "lat": 35.83675189153001,
        "lng": 129.2091842490869,
        "address": "경주시 황리단길 (황남아덴)",
        "note": "경주문화관광 공식 좌표",
    },
    "엘로우(LLOW)": {
        "lat": 35.845105499316944,
        "lng": 129.27183192276013,
        "address": "경주시 경감로 375-16 (천군동)",
        "note": "경주문화관광 공식 좌표",
    },
}

# 비장소 (좌표 수집 제외 대상)
SKIP_NAMES = {
    "숙소에서 간단히",
    "숙소에서 직접 조리",
    "대구에서 식사",
    "숙소 바비큐",
    "경주에서 마지막 식사",
    "고속도로 휴게소",
}


def get_jsonbin_data(bin_id: str, api_key: str) -> dict:
    """jsonbin.io에서 여행 데이터를 가져온다."""
    url = f"https://api.jsonbin.io/v3/b/{bin_id}/latest"
    headers = {
        "X-Master-Key": api_key,
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()["record"]
    except requests.exceptions.RequestException as e:
        logger.error("jsonbin GET 실패: %s", e)
        sys.exit(1)


def put_jsonbin_data(bin_id: str, api_key: str, data: dict) -> bool:
    """jsonbin.io에 여행 데이터를 업데이트한다."""
    url = f"https://api.jsonbin.io/v3/b/{bin_id}"
    headers = {
        "X-Master-Key": api_key,
        "Content-Type": "application/json",
    }
    try:
        response = requests.put(
            url, json=data, headers=headers, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        logger.info("jsonbin PUT 성공")
        return True
    except requests.exceptions.RequestException as e:
        logger.error("jsonbin PUT 실패: %s", e)
        return False


def lookup_kakao(name: str, api_key: str) -> Optional[dict]:
    """Kakao REST API로 장소를 검색하여 좌표를 반환한다."""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": f"{name} 경주", "size": 1}
    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        docs = response.json().get("documents", [])
        if docs:
            doc = docs[0]
            return {
                "lat": float(doc["y"]),
                "lng": float(doc["x"]),
                "address": doc.get("road_address_name", doc.get("address_name", "")),
                "note": "Kakao API 검색 결과",
            }
        logger.warning("Kakao API: '%s' 검색 결과 없음", name)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Kakao API 검색 실패 (%s): %s", name, e)
        return None


def collect_coords(
    data: dict, use_kakao: bool = False, kakao_key: Optional[str] = None
) -> dict:
    """
    여행 데이터의 모든 option에 좌표를 매칭한다.

    Returns:
        {option_name: {"lat": float, "lng": float, "source": str}} 매핑
    """
    result = {}
    for day in data.get("days", []):
        for item in day.get("items", []):
            for opt in item.get("options", []):
                name = opt.get("name", "")
                if not name or name in SKIP_NAMES:
                    continue

                # 이미 좌표가 있으면 스킵
                if "lat" in opt and "lng" in opt:
                    result[name] = {
                        "lat": opt["lat"],
                        "lng": opt["lng"],
                        "source": "기존 데이터",
                    }
                    continue

                # KNOWN_COORDS에서 검색
                if name in KNOWN_COORDS:
                    coord = KNOWN_COORDS[name]
                    result[name] = {
                        "lat": coord["lat"],
                        "lng": coord["lng"],
                        "source": coord.get("note", "KNOWN_COORDS"),
                    }
                    continue

                # Kakao API 검색 (옵션)
                if use_kakao and kakao_key:
                    kakao_result = lookup_kakao(name, kakao_key)
                    if kakao_result:
                        result[name] = {
                            "lat": kakao_result["lat"],
                            "lng": kakao_result["lng"],
                            "source": f"Kakao API ({kakao_result['address']})",
                        }
                        continue

                # 좌표를 찾지 못한 경우
                result[name] = {"lat": None, "lng": None, "source": "좌표 미확보"}

    return result


def apply_coords(data: dict, coords: dict) -> int:
    """
    여행 데이터의 option 객체에 lat/lng 필드를 추가한다.

    Returns:
        업데이트된 option 수
    """
    updated = 0
    for day in data.get("days", []):
        for item in day.get("items", []):
            for opt in item.get("options", []):
                name = opt.get("name", "")
                if name in coords and coords[name]["lat"] is not None:
                    coord = coords[name]
                    if opt.get("lat") != coord["lat"] or opt.get("lng") != coord["lng"]:
                        opt["lat"] = coord["lat"]
                        opt["lng"] = coord["lng"]
                        updated += 1
    return updated


def print_report(coords: dict) -> None:
    """좌표 수집 결과를 출력한다."""
    confirmed = []
    estimated = []
    missing = []

    for name, info in sorted(coords.items()):
        if info["lat"] is None:
            missing.append((name, info))
        elif "미확인" in info.get("source", ""):
            estimated.append((name, info))
        else:
            confirmed.append((name, info))

    logger.info("=== 좌표 수집 결과 ===")
    logger.info("")
    logger.info("[확인된 좌표] %d개", len(confirmed))
    for name, info in confirmed:
        logger.info(
            "  %s: (%.6f, %.6f) - %s", name, info["lat"], info["lng"], info["source"]
        )

    logger.info("")
    logger.info("[추정 좌표 (미확인)] %d개", len(estimated))
    for name, info in estimated:
        logger.info(
            "  %s: (%.4f, %.4f) - %s", name, info["lat"], info["lng"], info["source"]
        )

    logger.info("")
    logger.info("[좌표 미확보] %d개", len(missing))
    for name, info in missing:
        logger.info("  %s - %s", name, info["source"])

    logger.info("")
    logger.info(
        "총계: 확인 %d / 추정 %d / 미확보 %d",
        len(confirmed),
        len(estimated),
        len(missing),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="경주 여행 데이터 좌표 수집")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--dry-run", action="store_true", help="결과만 출력 (jsonbin 변경 없음)"
    )
    group.add_argument(
        "--apply", action="store_true", help="jsonbin에 실제 반영"
    )
    parser.add_argument(
        "--kakao", action="store_true", help="Kakao REST API로 좌표 검증"
    )
    args = parser.parse_args()

    # 환경변수 확인
    bin_id = os.environ.get("JSONBIN_BIN_ID")
    api_key = os.environ.get("JSONBIN_API_KEY")
    if not bin_id or not api_key:
        logger.error("JSONBIN_BIN_ID, JSONBIN_API_KEY 환경변수가 필요합니다")
        return 1

    kakao_key = os.environ.get("KAKAO_REST_API_KEY")
    if args.kakao and not kakao_key:
        logger.error("--kakao 모드에는 KAKAO_REST_API_KEY 환경변수가 필요합니다")
        return 1

    # jsonbin에서 데이터 가져오기
    logger.info("jsonbin에서 여행 데이터를 가져오는 중...")
    data = get_jsonbin_data(bin_id, api_key)
    logger.info("데이터 로드 완료")

    # 좌표 수집
    coords = collect_coords(data, use_kakao=args.kakao, kakao_key=kakao_key)

    # 결과 출력
    print_report(coords)

    if args.dry_run:
        # dry-run: 적용 시 변경될 항목 수 미리보기
        updated = apply_coords(data, coords)
        logger.info("")
        logger.info("[dry-run] 적용 시 %d개 option이 업데이트됩니다", updated)
        return 0

    if args.apply:
        # 실제 적용
        updated = apply_coords(data, coords)
        if updated == 0:
            logger.info("변경 사항 없음 - jsonbin 업데이트 생략")
            return 0

        logger.info("%d개 option에 좌표를 추가합니다...", updated)
        success = put_jsonbin_data(bin_id, api_key, data)
        if success:
            logger.info("jsonbin 업데이트 완료! (%d개 option 갱신)", updated)
            return 0
        else:
            logger.error("jsonbin 업데이트 실패")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
