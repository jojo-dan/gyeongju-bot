"""경주 여행 봇 도구 정의 모듈.

Anthropic Messages API의 tools 파라미터에 전달할 도구 목록을 정의한다.
읽기 도구 5개, 쓰기 도구 8개, 메타 도구 1개로 총 14개의 도구를 포함한다.
옵션 스키마에 lat/lng 좌표 필드를 포함한다.
"""

TOOLS = [
    # ──────────────────────────────────────────────
    # 읽기 도구 (5개)
    # ──────────────────────────────────────────────
    {
        "name": "get_schedule",
        "description": (
            "특정 일차의 전체 일정을 조회한다. "
            "day_num(일차 번호) 또는 date(날짜) 중 하나 이상을 반드시 제공해야 한다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "day_num": {
                    "type": "integer",
                    "description": "일차 번호 (1~6)",
                },
                "date": {
                    "type": "string",
                    "description": "날짜 (YYYY-MM-DD 형식)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "find_item",
        "description": (
            "이름 또는 키워드로 항목을 검색한다. "
            "항목 제목(title)과 옵션 이름(option name) 모두에서 부분 일치로 검색한다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색 키워드",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_items",
        "description": (
            "조건 필터링으로 항목을 검색한다. "
            "여러 조건을 동시에 지정하면 AND 결합으로 모든 조건을 만족하는 항목만 반환한다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cat": {
                    "type": "string",
                    "enum": ["meal", "cafe", "activity"],
                    "description": "카테고리",
                },
                "dad": {
                    "type": "string",
                    "enum": ["good", "caution"],
                    "description": "아버지 당뇨 적합성",
                },
                "hiro": {
                    "type": "string",
                    "enum": ["good", "caution"],
                    "description": "히로 알러지 적합성",
                },
                "status": {
                    "type": "string",
                    "enum": ["planned", "done", "skipped"],
                    "description": "상태",
                },
                "day_num": {
                    "type": "integer",
                    "description": "일차 번호",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_item_detail",
        "description": "특정 항목의 상세 정보를 조회한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID (예: d1_dinner)",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "get_trip_summary",
        "description": "여행 전체 통계를 조회한다. 완료/미완료/확정 수 등 전반적인 현황을 반환한다.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    # ──────────────────────────────────────────────
    # 쓰기 도구 (8개)
    # ──────────────────────────────────────────────
    {
        "name": "update_item",
        "description": (
            "항목의 기본 정보(시간, 제목)를 수정한다. "
            "시간 변경, 제목 변경 등에 사용한다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID",
                },
                "time": {
                    "type": "string",
                    "description": "새 시간 (예: \"09:00\", \"14:00~16:00\")",
                },
                "title": {
                    "type": "string",
                    "description": "새 제목",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "update_status",
        "description": "항목의 상태를 변경한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID",
                },
                "status": {
                    "type": "string",
                    "enum": ["planned", "done", "skipped"],
                    "description": "새 상태",
                },
            },
            "required": ["item_id", "status"],
        },
    },
    {
        "name": "update_visit",
        "description": (
            "장소/식당/숙소의 방문 여부를 기록한다. "
            "옵션이 있는 항목(식당 등)은 어떤 옵션을 방문했는지도 함께 기록한다. "
            "방문 기록 시 status가 planned이면 자동으로 done으로 변경된다."
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
    },
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
    },
    {
        "name": "update_note",
        "description": "항목에 메모를 추가하거나 수정한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID",
                },
                "note": {
                    "type": "string",
                    "description": "메모 내용",
                },
                "mode": {
                    "type": "string",
                    "enum": ["append", "replace"],
                    "description": "추가(append) 또는 교체(replace). 기본값: append",
                },
            },
            "required": ["item_id", "note"],
        },
    },
    {
        "name": "update_option",
        "description": (
            "옵션의 세부정보를 수정한다. "
            "옵션 이름은 부분 일치로 매칭되므로 정확한 전체 이름을 입력하지 않아도 된다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID",
                },
                "option_name": {
                    "type": "string",
                    "description": "옵션 이름 (부분 일치 가능)",
                },
                "fields": {
                    "type": "object",
                    "description": "수정할 필드들",
                    "properties": {
                        "menu": {
                            "type": "string",
                            "description": "대표 메뉴",
                        },
                        "dad": {
                            "type": "string",
                            "enum": ["good", "caution"],
                            "description": "아버지 당뇨 적합성",
                        },
                        "hiro": {
                            "type": "string",
                            "enum": ["good", "caution"],
                            "description": "히로 알러지 적합성",
                        },
                        "hiroNote": {
                            "type": "string",
                            "description": "히로 알러지 관련 메모",
                        },
                        "hours": {
                            "type": "string",
                            "description": "영업시간",
                        },
                        "address": {
                            "type": "string",
                            "description": "주소",
                        },
                        "phone": {
                            "type": "string",
                            "description": "전화번호",
                        },
                        "photo_url": {
                            "type": "string",
                            "description": "사진 URL",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "태그",
                        },
                        "lat": {
                            "type": "number",
                            "description": "위도 (latitude)",
                        },
                        "lng": {
                            "type": "number",
                            "description": "경도 (longitude)",
                        },
                    },
                },
            },
            "required": ["item_id", "option_name", "fields"],
        },
    },
    {
        "name": "add_item",
        "description": (
            "새 일정 항목을 추가한다. "
            "after_item_id를 지정하면 해당 항목 뒤에 삽입된다. 미지정 시 일차 마지막에 추가된다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "day_num": {
                    "type": "integer",
                    "description": "일차 번호",
                },
                "title": {
                    "type": "string",
                    "description": "항목 제목",
                },
                "cat": {
                    "type": "string",
                    "enum": ["meal", "cafe", "activity"],
                    "description": "카테고리",
                },
                "time": {
                    "type": "string",
                    "description": "시간 (예: \"14:00~\")",
                },
                "after_item_id": {
                    "type": "string",
                    "description": "이 항목 뒤에 삽입 (예: \"d1_travel\"이면 이동 항목 바로 뒤)",
                },
                "options": {
                    "type": "array",
                    "description": "옵션 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "옵션 이름",
                            },
                            "menu": {
                                "type": "string",
                                "description": "대표 메뉴",
                            },
                            "dad": {
                                "type": "string",
                                "enum": ["good", "caution"],
                                "description": "아버지 당뇨 적합성",
                            },
                            "hiro": {
                                "type": "string",
                                "enum": ["good", "caution"],
                                "description": "히로 알러지 적합성",
                            },
                            "hiroNote": {
                                "type": "string",
                                "description": "히로 알러지 관련 메모",
                            },
                            "lat": {
                                "type": "number",
                                "description": "위도 (latitude)",
                            },
                            "lng": {
                                "type": "number",
                                "description": "경도 (longitude)",
                            },
                        },
                        "required": ["name"],
                    },
                },
            },
            "required": ["day_num", "title", "cat"],
        },
    },
    {
        "name": "add_option",
        "description": "기존 항목에 새 옵션을 추가한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID",
                },
                "name": {
                    "type": "string",
                    "description": "옵션 이름",
                },
                "menu": {
                    "type": "string",
                    "description": "대표 메뉴",
                },
                "dad": {
                    "type": "string",
                    "enum": ["good", "caution"],
                    "description": "아버지 당뇨 적합성",
                },
                "hiro": {
                    "type": "string",
                    "enum": ["good", "caution"],
                    "description": "히로 알러지 적합성",
                },
                "hiroNote": {
                    "type": "string",
                    "description": "히로 알러지 관련 메모",
                },
                "lat": {
                    "type": "number",
                    "description": "위도 (latitude)",
                },
                "lng": {
                    "type": "number",
                    "description": "경도 (longitude)",
                },
            },
            "required": ["item_id", "name"],
        },
    },
    {
        "name": "move_item",
        "description": (
            "항목을 다른 일차로 이동한다. "
            "after_item_id를 지정하면 해당 항목 뒤에 삽입된다. 미지정 시 일차 마지막에 추가된다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "항목 ID",
                },
                "to_day_num": {
                    "type": "integer",
                    "description": "이동할 일차 번호",
                },
                "new_time": {
                    "type": "string",
                    "description": "새 시간",
                },
                "after_item_id": {
                    "type": "string",
                    "description": "이 항목 뒤에 삽입",
                },
            },
            "required": ["item_id", "to_day_num"],
        },
    },
    # ──────────────────────────────────────────────
    # 메타 도구 (1개)
    # ──────────────────────────────────────────────
    {
        "name": "remove_item",
        "description": "항목을 완전히 삭제한다.",
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
]
