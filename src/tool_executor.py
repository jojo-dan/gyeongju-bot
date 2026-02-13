"""
tool_executor.py
Tool 실행 로직: Claude tool_use 응답을 처리하고 in-memory JSON 여행 데이터에 대해 실행.
"""

import copy
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))


# ---------------------------------------------------------------------------
# ExecutionContext
# ---------------------------------------------------------------------------

class ExecutionContext:
    """Tool 실행 컨텍스트. in-memory 데이터와 변경 추적."""

    def __init__(self, data: dict):
        self._data = copy.deepcopy(data)
        self._modified = False

    # -- properties ---------------------------------------------------------

    @property
    def modified(self) -> bool:
        return self._modified

    @property
    def data(self) -> dict:
        return self._data

    # -- mutation helpers ---------------------------------------------------

    def mark_modified(self, update_note: str = ""):
        """Mark data as modified, update meta.lastUpdated (KST ISO8601) and optionally meta.updateNote."""
        self._modified = True
        meta = self._data.setdefault("meta", {})
        meta["lastUpdated"] = datetime.now(KST).isoformat()
        if update_note:
            meta["updateNote"] = update_note

    # -- lookup helpers -----------------------------------------------------

    def find_item(self, item_id: str) -> Optional[Tuple[dict, dict]]:
        """Find item by ID. Returns (day_dict, item_dict) or None."""
        for day in self._data.get("days", []):
            for item in day.get("items", []):
                if item.get("id") == item_id:
                    return day, item
        return None

    def find_items_by_query(self, query: str) -> List[dict]:
        """Partial match search on item titles and option names.
        Returns list of items with added '_dayNum' field."""
        query_lower = query.lower()
        results: List[dict] = []
        for day in self._data.get("days", []):
            day_num = day.get("dayNum")
            for item in day.get("items", []):
                matched = False
                # title 검색
                if query_lower in item.get("title", "").lower():
                    matched = True
                # option name 검색
                if not matched:
                    for opt in item.get("options", []):
                        if query_lower in opt.get("name", "").lower():
                            matched = True
                            break
                if matched:
                    entry = copy.deepcopy(item)
                    entry["_dayNum"] = day_num
                    results.append(entry)
        return results

    def find_day(self, day_num: int = None, date: str = None) -> Optional[dict]:
        """Find day by day_num or date string."""
        for day in self._data.get("days", []):
            if day_num is not None and day.get("dayNum") == day_num:
                return day
            if date is not None and day.get("date") == date:
                return day
        return None

    def find_option(self, item: dict, option_name: str) -> Optional[dict]:
        """Find option by partial name match within an item's options list."""
        name_lower = option_name.lower()
        for opt in item.get("options", []):
            if name_lower in opt.get("name", "").lower():
                return opt
        return None


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_HANDLERS = {}


def _register(tool_name: str):
    """Decorator to register a handler for a tool name."""
    def decorator(fn):
        _HANDLERS[tool_name] = fn
        return fn
    return decorator


def execute_tool(ctx: ExecutionContext, tool_name: str, tool_input: dict) -> dict:
    """Dispatch tool call to the appropriate handler. Returns a result dict."""
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        logger.warning("Unknown tool requested: %s", tool_name)
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return handler(ctx, tool_input)
    except Exception as exc:
        logger.exception("Tool execution failed: %s", tool_name)
        return {"error": f"Tool execution failed: {exc}"}


# ---------------------------------------------------------------------------
# Read Handlers
# ---------------------------------------------------------------------------

def _status_icon(status: str) -> str:
    """상태값을 아이콘 문자열로 변환."""
    return {"planned": "[ ]", "done": "[v]", "skipped": "[x]"}.get(status, "[?]")


@_register("get_schedule")
def _handle_get_schedule(ctx: ExecutionContext, inp: dict) -> dict:
    """일정 조회 (day_num 또는 date 기준)."""
    day = ctx.find_day(day_num=inp.get("day_num"), date=inp.get("date"))
    if day is None:
        return {"error": "해당 일자를 찾을 수 없습니다."}

    items_summary = []
    for item in day.get("items", []):
        icon = _status_icon(item.get("status", "planned"))
        chosen = item.get("chosen", "")
        options = [o.get("name", "") for o in item.get("options", [])]
        items_summary.append({
            "icon": icon,
            "id": item.get("id"),
            "time": item.get("time", ""),
            "title": item.get("title", ""),
            "chosen": chosen,
            "options": options,
        })

    return {
        "dayNum": day.get("dayNum"),
        "date": day.get("date"),
        "dow": day.get("dow"),
        "title": day.get("title", ""),
        "items": items_summary,
    }


@_register("find_item")
def _handle_find_item(ctx: ExecutionContext, inp: dict) -> dict:
    """키워드 부분 일치 검색."""
    query = inp.get("query", "")
    if not query:
        return {"error": "query가 필요합니다."}

    results = ctx.find_items_by_query(query)
    return {
        "count": len(results),
        "items": [
            {
                "dayNum": r.get("_dayNum"),
                "id": r.get("id"),
                "title": r.get("title"),
                "status": r.get("status"),
                "chosen": r.get("chosen", ""),
            }
            for r in results
        ],
    }


@_register("search_items")
def _handle_search_items(ctx: ExecutionContext, inp: dict) -> dict:
    """필터 기반 검색 (cat, dad, hiro, status, day_num AND 조합)."""
    cat_filter = inp.get("cat")
    dad_filter = inp.get("dad")
    hiro_filter = inp.get("hiro")
    status_filter = inp.get("status")
    day_num_filter = inp.get("day_num")

    results: List[dict] = []

    for day in ctx.data.get("days", []):
        d_num = day.get("dayNum")
        if day_num_filter is not None and d_num != day_num_filter:
            continue

        for item in day.get("items", []):
            # cat 필터
            if cat_filter and item.get("cat") != cat_filter:
                continue
            # status 필터
            if status_filter and item.get("status") != status_filter:
                continue
            # dad / hiro 필터: ANY option 일치
            if dad_filter:
                if not any(o.get("dad") == dad_filter for o in item.get("options", [])):
                    continue
            if hiro_filter:
                if not any(o.get("hiro") == hiro_filter for o in item.get("options", [])):
                    continue

            results.append({
                "dayNum": d_num,
                "id": item.get("id"),
                "title": item.get("title"),
                "cat": item.get("cat"),
                "status": item.get("status"),
                "chosen": item.get("chosen", ""),
            })

    return {"count": len(results), "items": results}


@_register("get_item_detail")
def _handle_get_item_detail(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템 상세 조회."""
    item_id = inp.get("item_id", "")
    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    day, item = found

    result = {
        "dayNum": day.get("dayNum"),
        "date": day.get("date"),
        "id": item.get("id"),
        "time": item.get("time", ""),
        "cat": item.get("cat", ""),
        "title": item.get("title", ""),
        "options": copy.deepcopy(item.get("options", [])),
        "chosen": item.get("chosen", ""),
        "status": item.get("status", "planned"),
        "note": item.get("note", ""),
    }
    if "guide" in item:
        result["guide"] = copy.deepcopy(item["guide"])
    return result


@_register("get_trip_summary")
def _handle_get_trip_summary(ctx: ExecutionContext, inp: dict) -> dict:
    """여행 전체 요약 통계."""
    per_day: List[dict] = []
    total = planned = done = skipped = chosen_cnt = with_options = 0

    for day in ctx.data.get("days", []):
        d_total = d_planned = d_done = d_skipped = d_chosen = d_with_opts = 0
        for item in day.get("items", []):
            d_total += 1
            st = item.get("status", "planned")
            if st == "planned":
                d_planned += 1
            elif st == "done":
                d_done += 1
            elif st == "skipped":
                d_skipped += 1
            if item.get("chosen"):
                d_chosen += 1
            if item.get("options") and not item.get("chosen"):
                d_with_opts += 1

        per_day.append({
            "dayNum": day.get("dayNum"),
            "date": day.get("date"),
            "title": day.get("title", ""),
            "total": d_total,
            "planned": d_planned,
            "done": d_done,
            "skipped": d_skipped,
            "chosen": d_chosen,
            "with_options": d_with_opts,
        })
        total += d_total
        planned += d_planned
        done += d_done
        skipped += d_skipped
        chosen_cnt += d_chosen
        with_options += d_with_opts

    return {
        "days": per_day,
        "totals": {
            "total": total,
            "planned": planned,
            "done": done,
            "skipped": skipped,
            "chosen": chosen_cnt,
            "with_options": with_options,
        },
    }


# ---------------------------------------------------------------------------
# Write Handlers
# ---------------------------------------------------------------------------

_VALID_STATUSES = {"planned", "done", "skipped"}


@_register("update_status")
def _handle_update_status(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템 상태 변경."""
    item_id = inp.get("item_id", "")
    new_status = inp.get("status", "")

    if new_status not in _VALID_STATUSES:
        return {"error": f"유효하지 않은 상태값입니다: {new_status} (허용: {_VALID_STATUSES})"}

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    old_status = item.get("status", "planned")
    item["status"] = new_status
    ctx.mark_modified(f"{item_id} 상태 변경: {old_status} -> {new_status}")
    logger.info("Status updated: %s %s -> %s", item_id, old_status, new_status)

    return {"ok": True, "item_id": item_id, "old_status": old_status, "new_status": new_status}


@_register("set_chosen")
def _handle_set_chosen(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템 선택지 확정."""
    item_id = inp.get("item_id", "")
    chosen_value = inp.get("chosen", "")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    # partial match 로 full option name 결정
    matched_opt = ctx.find_option(item, chosen_value)
    if matched_opt is None:
        available = [o.get("name", "") for o in item.get("options", [])]
        return {"error": f"일치하는 옵션을 찾을 수 없습니다: '{chosen_value}'. 가능한 옵션: {available}"}

    full_name = matched_opt["name"]
    item["chosen"] = full_name
    ctx.mark_modified(f"{item_id} 선택 확정: {full_name}")
    logger.info("Chosen set: %s -> %s", item_id, full_name)

    return {"ok": True, "item_id": item_id, "chosen": full_name}


@_register("update_note")
def _handle_update_note(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템 메모 수정."""
    item_id = inp.get("item_id", "")
    note = inp.get("note", "")
    mode = inp.get("mode", "append")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    if mode == "replace":
        item["note"] = note
    else:  # append
        existing = item.get("note", "")
        if existing:
            item["note"] = existing + "\n" + note
        else:
            item["note"] = note

    ctx.mark_modified(f"{item_id} 메모 업데이트 ({mode})")
    logger.info("Note updated (%s): %s", mode, item_id)

    return {"ok": True, "item_id": item_id, "note": item["note"]}


_OPTION_FIELDS = {"menu", "dad", "hiro", "hiroNote", "hours", "address", "phone", "photo_url", "tags"}


@_register("update_option")
def _handle_update_option(ctx: ExecutionContext, inp: dict) -> dict:
    """옵션 필드 수정."""
    item_id = inp.get("item_id", "")
    option_name = inp.get("option_name", "")
    fields = inp.get("fields", {})

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    opt = ctx.find_option(item, option_name)
    if opt is None:
        available = [o.get("name", "") for o in item.get("options", [])]
        return {"error": f"옵션을 찾을 수 없습니다: '{option_name}'. 가능한 옵션: {available}"}

    updated_fields = []
    for key, value in fields.items():
        if key not in _OPTION_FIELDS:
            return {"error": f"지원하지 않는 필드입니다: {key} (허용: {_OPTION_FIELDS})"}
        opt[key] = value
        updated_fields.append(key)

    ctx.mark_modified(f"{item_id} 옵션 '{opt['name']}' 수정: {updated_fields}")
    logger.info("Option updated: %s / %s fields=%s", item_id, opt["name"], updated_fields)

    return {"ok": True, "item_id": item_id, "option": opt["name"], "updated_fields": updated_fields}


@_register("add_item")
def _handle_add_item(ctx: ExecutionContext, inp: dict) -> dict:
    """새 아이템 추가."""
    day_num = inp.get("day_num")
    title = inp.get("title", "")
    time_str = inp.get("time", "")
    cat = inp.get("cat", "activity")
    options = inp.get("options", [])

    if not title:
        return {"error": "title이 필요합니다."}

    day = ctx.find_day(day_num=day_num)
    if day is None:
        return {"error": f"Day {day_num}을(를) 찾을 수 없습니다."}

    # 아이템 ID 생성
    item_index = len(day.get("items", [])) + 1
    item_id = f"d{day_num}_item{item_index}"

    new_item: dict = {
        "id": item_id,
        "time": time_str,
        "cat": cat,
        "title": title,
        "options": [],
        "chosen": "",
        "status": "planned",
        "note": "",
    }

    # 옵션 추가
    for opt_data in options:
        opt_entry: dict = {"name": opt_data.get("name", "")}
        for field in ("menu", "dad", "hiro", "hiroNote"):
            if field in opt_data:
                opt_entry[field] = opt_data[field]
        new_item["options"].append(opt_entry)

    day.setdefault("items", []).append(new_item)
    ctx.mark_modified(f"아이템 추가: {item_id} ({title})")
    logger.info("Item added: %s to day %s", item_id, day_num)

    return {"ok": True, "item_id": item_id, "dayNum": day_num, "title": title}


@_register("add_option")
def _handle_add_option(ctx: ExecutionContext, inp: dict) -> dict:
    """기존 아이템에 옵션 추가."""
    item_id = inp.get("item_id", "")
    name = inp.get("name", "")

    if not name:
        return {"error": "name이 필요합니다."}

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    _day, item = found

    opt_entry: dict = {"name": name}
    for field in ("menu", "dad", "hiro", "hiroNote"):
        if field in inp:
            opt_entry[field] = inp[field]

    item.setdefault("options", []).append(opt_entry)
    ctx.mark_modified(f"{item_id} 옵션 추가: {name}")
    logger.info("Option added: %s -> %s", item_id, name)

    return {"ok": True, "item_id": item_id, "option_name": name}


@_register("move_item")
def _handle_move_item(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템을 다른 일자로 이동."""
    item_id = inp.get("item_id", "")
    to_day_num = inp.get("to_day_num")
    new_time = inp.get("new_time")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    src_day, item = found

    tgt_day = ctx.find_day(day_num=to_day_num)
    if tgt_day is None:
        return {"error": f"Day {to_day_num}을(를) 찾을 수 없습니다."}

    # source 에서 제거
    src_day["items"] = [i for i in src_day["items"] if i.get("id") != item_id]

    # 시간 변경
    if new_time is not None:
        item["time"] = new_time

    # ID 접두사 변경 (d{old}_xxx -> d{new}_xxx)
    old_prefix = f"d{src_day.get('dayNum')}_"
    if item_id.startswith(old_prefix):
        suffix = item_id[len(old_prefix):]
        item["id"] = f"d{to_day_num}_{suffix}"
    else:
        item["id"] = f"d{to_day_num}_{item_id}"

    new_id = item["id"]

    tgt_day.setdefault("items", []).append(item)
    ctx.mark_modified(f"아이템 이동: {item_id} -> Day {to_day_num} ({new_id})")
    logger.info("Item moved: %s -> day %s as %s", item_id, to_day_num, new_id)

    return {"ok": True, "old_id": item_id, "new_id": new_id, "to_day_num": to_day_num}


@_register("remove_item")
def _handle_remove_item(ctx: ExecutionContext, inp: dict) -> dict:
    """아이템 삭제."""
    item_id = inp.get("item_id", "")

    found = ctx.find_item(item_id)
    if found is None:
        return {"error": f"아이템을 찾을 수 없습니다: {item_id}"}
    day, item = found

    day["items"] = [i for i in day["items"] if i.get("id") != item_id]
    ctx.mark_modified(f"아이템 삭제: {item_id} ({item.get('title', '')})")
    logger.info("Item removed: %s", item_id)

    return {"ok": True, "item_id": item_id, "title": item.get("title", "")}
