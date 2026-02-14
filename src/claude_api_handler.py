"""Anthropic API Tool Use 기반 메시지 처리 모듈

Claude CLI subprocess 방식을 대체하여 Anthropic SDK의
Messages API와 Tool Use를 사용한다.

흐름:
    사용자 메시지 -> 시스템 프롬프트(일정 개요 포함) -> API 호출 ->
    tool_use 응답이면 -> 도구 실행 -> 결과를 Claude에 반환 -> 반복
    text 응답이면 -> 최종 응답 반환
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

import anthropic
from anthropic import AsyncAnthropic

from tool_definitions import TOOLS
from tool_executor import ExecutionContext, execute_tool

logger = logging.getLogger(__name__)

# ── 상수 ──────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-5-20250929"
MAX_TOOL_ROUNDS = 10
MAX_TOKENS = 2048

KST = timezone(timedelta(hours=9))
TRIP_START = datetime(2026, 2, 19, tzinfo=KST)
TRIP_END = datetime(2026, 2, 24, 23, 59, 59, tzinfo=KST)

# ── 시스템 프롬프트 ───────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """너는 '포저'다. 죠죠의 경주 가족여행을 가장 가까이에서 보필하는 여행 보좌관이다.

[포저의 역할]
- 단순 일정 안내가 아니라, 가족 상황을 고려한 우선순위와 대안을 제안하는 전략적 여행 참모다.
- 죠죠의 요청에 따라 도구를 사용하여 일정을 조회하거나 변경한다.

[톤앤매너]
- 사용자를 항상 '죠죠'로 부른다.
- 존댓말을 기본으로 하되, 딱딱하지 않고 따뜻한 톤을 유지한다. "~입니다/~습니다"와 "~할까요/~드릴까요/~이에요"를 자연스럽게 섞는다.
- 반말("~야", "~해볼까?")은 금지한다.
- 이모지를 사용하지 않는다.
- 담백하되 무성의하지 않다. 불필요한 장식은 걷어내되, 죠죠가 다시 물어볼 필요 없을 만큼 충분한 밀도를 담는다.
- 맥락 없는 친절("오늘 하루도 힘내세요" 등)은 쓰지 않는다.
- 텔레그램 마크다운 형식을 사용한다. 표는 쓰지 않는다.

[응답의 호흡]
- 단순 사실 확인: 간결하게 끝낸다.
- 일정 조회/보고: 죠죠가 재질문하지 않아도 될 만큼의 맥락을 담는다. 결론을 먼저 말하고, 참고할 점까지 한 호흡에 전달한다.
- 추천/의사결정: 선택지, 주의사항(아버지 당뇨·히로 알러지), 포저의 의견을 갖추어 전달한다.

[사려 깊은 연결]
- 답변 전에 "죠죠가 왜 이것을 물었을까"를 먼저 고려한다. 표면적 질문 뒤의 의도까지 해소하는 응답을 한다.
- 보고할 때 단순 나열이 아니라 "이 부분만 확인이 필요합니다" 같은 결과론적 요약을 병행한다.

[가족 정보]
- 인원: 아버지(당뇨 관리), 어머니(운전 담당), 죠죠, 아내, 히로(27개월, 밀/계란 알러지)
- 숙소: 까사멜로우(경북 경주시 북군4길 75)
- 특별 일정: 2/22(일) 대구국제마라톤 풀코스 (죠죠 참가)
- 오늘 날짜: {today}
- 여행 {day_status}

[도구 사용 — 절대 규칙]
- 일정을 조회·변경·기록할 때는 반드시 도구를 호출해야 한다. 도구 없이 "반영했습니다", "완료했습니다", "옮겼습니다" 등의 완료 표현을 절대 사용하지 않는다.
- 도구를 호출하지 않았으면 데이터는 바뀌지 않은 것이다. 바뀌지 않은 것을 바꿨다고 말하는 것은 거짓말이다.
- 죠죠가 일정 변경을 요청하면, 제안만 하지 말고 실제로 도구를 호출하여 변경을 실행한다. "이렇게 바꾸면 어떨까요?"로 끝내지 말고, 실행까지 해야 한다.
- 죠죠가 먼저 제안을 요청한 경우에만 제안 후 확인을 기다린다. "옮겨줘", "바꿔줘", "변경해줘" 같은 직접 지시에는 즉시 실행한다.

[도구 목록]
- 조회: get_schedule, find_item, search_items, get_item_detail, get_trip_summary
- 변경: update_status, update_visit, update_review, update_note, update_option, add_item, add_option, move_item, remove_item
- item_id가 확실하지 않으면 find_item으로 먼저 검색한다.
- 변경 후에는 간결한 확인 메시지를 제공한다.
- 여러 변경이 필요하면 도구를 순차적으로 호출한다.
- 관광지 상세 정보(입장료, 주차, 유모차, 수유실, must-do 등)가 필요하면 get_item_detail로 해당 activity 아이템을 조회한다. guide 필드에 상세 가이드가 포함되어 있다.

[방문 기록 & 리뷰]
- 사용자가 "~~ 다녀왔어", "~~ 도착했어", "~~ 갔어" 등 방문 사실을 말하면 update_visit으로 기록
- 방문 기록 시 status가 자동으로 done으로 변경됨
- 옵션이 있는 항목(식당)은 어떤 옵션을 방문했는지 option_name도 함께 기록
- 사용자가 감상/평가를 남기면 update_review로 리뷰 기록
- "확정" 개념은 없음. 미리 정하는 대신, 다녀온 후 기록하는 방식

[맥락 유지]
- 이전 대화 내용이 함께 전달된다. 죠죠가 "거기", "그거", "아까 말한 것" 등 대명사를 쓰면 이전 대화에서 맥락을 찾는다.
- 맥락을 찾을 수 없으면 솔직하게 "어떤 항목을 말씀하시는 건지 다시 한번 알려주시겠어요?"라고 묻는다. 추측으로 엉뚱한 답변을 만들지 않는다.

[일정 개요]
{schedule_overview}"""


# ── 헬퍼 함수 ─────────────────────────────────────────────────

def _get_day_status(now: Optional[datetime] = None) -> str:
    """여행 진행 상태 문자열을 반환한다."""
    if now is None:
        now = datetime.now(KST)

    if now < TRIP_START:
        days_left = (TRIP_START.date() - now.date()).days
        return f"시작 전 (D-{days_left})"
    elif now > TRIP_END:
        return "종료됨"
    else:
        day_num = (now.date() - TRIP_START.date()).days + 1
        return f"Day {day_num} 진행 중"


def build_schedule_overview(data: dict) -> str:
    """여행 데이터에서 일정 개요 텍스트를 생성한다.

    각 일차별로 항목 ID, 시간, 제목, 상태, 확정/후보 정보를 포함한다.
    """
    lines = []
    for day in data.get("days", []):
        date = day.get("date", "")
        dow = day.get("dow", "")
        day_num = day.get("dayNum", "")
        title = day.get("title", "")
        lines.append(f"### Day {day_num} ({date}, {dow}) - {title}")

        for item in day.get("items", []):
            status = item.get("status", "planned")
            if status == "done":
                icon = "[v]"
            elif status == "skipped":
                icon = "[x]"
            else:
                icon = "[ ]"

            item_id = item.get("id", "")
            time = item.get("time", "")
            item_title = item.get("title", "")

            chosen = item.get("chosen", "")
            options = item.get("options", [])

            suffix = ""
            if chosen:
                suffix = f" [확정: {chosen}]"
            elif options:
                names = [o.get("name", "") for o in options if o.get("name")]
                if names:
                    suffix = f" (후보: {', '.join(names)})"

            lines.append(f"  {icon} {item_id} | {time} | {item_title}{suffix}")

        lines.append("")  # 일차 간 빈 줄

    return "\n".join(lines).rstrip()


def _extract_text(response) -> str:
    """API 응답에서 텍스트 블록을 추출한다."""
    texts = []
    for block in response.content:
        if hasattr(block, "text"):
            texts.append(block.text)
    return "\n".join(texts) if texts else ""


# ── 응답 데이터 클래스 ────────────────────────────────────────

@dataclass
class ApiResponse:
    """API 응답 결과"""
    text: str
    data_modified: bool
    updated_data: Optional[dict]
    error: Optional[str] = None


# ── 메인 처리 함수 ────────────────────────────────────────────

async def process_message_api(json_data: dict, user_message: str, history: list | None = None) -> ApiResponse:
    """Anthropic API로 사용자 메시지를 처리한다.

    시스템 프롬프트에 일정 개요를 포함하고, Tool Use 루프를 통해
    일정 조회/변경 도구를 실행한 뒤 최종 텍스트 응답을 반환한다.

    Args:
        json_data: jsonbin에서 가져온 현재 여행 데이터
        user_message: 사용자가 텔레그램에 보낸 메시지
        history: 이전 대화 히스토리 [{role, content}, ...]

    Returns:
        ApiResponse 객체 (텍스트, 데이터 변경 여부, 변경된 데이터)
    """
    # 1. 시스템 프롬프트 구성
    now = datetime.now(KST)
    today = now.strftime("%Y-%m-%d (%a)")
    day_status = _get_day_status(now)
    schedule_overview = build_schedule_overview(json_data)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        today=today,
        day_status=day_status,
        schedule_overview=schedule_overview,
    )

    # 2. Anthropic 클라이언트 및 실행 컨텍스트 초기화
    client = AsyncAnthropic()
    ctx = ExecutionContext(json_data)

    # 3. 초기 메시지 (대화 히스토리 포함)
    messages = []
    if history:
        for msg in history[:-1]:  # 마지막은 현재 메시지이므로 제외
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = None

    try:
        # 4. Tool Use 루프
        for round_num in range(MAX_TOOL_ROUNDS):
            logger.info("API 호출 (라운드 %d/%d)", round_num + 1, MAX_TOOL_ROUNDS)

            response = await client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                tools=TOOLS,
                messages=messages,
            )

            logger.debug("stop_reason: %s", response.stop_reason)

            # 텍스트 응답 완료
            if response.stop_reason == "end_turn":
                text = _extract_text(response)
                return ApiResponse(
                    text=text,
                    data_modified=ctx.modified,
                    updated_data=ctx.data if ctx.modified else None,
                )

            # 도구 호출 처리
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info("도구 실행: %s (input: %s)", block.name, block.input)
                        result = execute_tool(ctx, block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        })

                messages.append({"role": "user", "content": tool_results})
                continue

            # 예상치 못한 stop_reason
            logger.warning("예상치 못한 stop_reason: %s", response.stop_reason)
            break

        # 라운드 초과 시 마지막 응답에서 텍스트 추출
        text = _extract_text(response) if response else "처리 중 문제가 발생했어요."
        if not text:
            text = "처리 중 문제가 발생했어요."
        return ApiResponse(
            text=text,
            data_modified=ctx.modified,
            updated_data=ctx.data if ctx.modified else None,
        )

    except anthropic.AuthenticationError as e:
        logger.error("Anthropic 인증 에러: %s", e)
        return ApiResponse(
            text="API 인증에 문제가 있어요. 관리자에게 문의해주세요.",
            data_modified=False,
            updated_data=None,
            error=f"인증 에러: {e}",
        )
    except anthropic.APIError as e:
        logger.error("Anthropic API 에러: %s", e)
        return ApiResponse(
            text="API 호출 중 문제가 발생했어요. 잠시 후 다시 시도해주세요.",
            data_modified=False,
            updated_data=None,
            error=f"API 에러: {e}",
        )
    except Exception as e:
        logger.error("메시지 처리 중 예외 발생: %s", e, exc_info=True)
        return ApiResponse(
            text="처리 중 문제가 발생했어요.",
            data_modified=False,
            updated_data=None,
            error=str(e),
        )
