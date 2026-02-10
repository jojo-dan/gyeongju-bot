"""
프롬프트 템플릿 모듈

Claude CLI에 전달할 시스템 프롬프트를 구성한다.
가족 정보, 여행 규칙, 현재 JSON 데이터, 사용자 메시지를 조합하여
최종 프롬프트를 생성한다.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# 한국 표준시
KST = timezone(timedelta(hours=9))

# 여행 기간
TRIP_START = datetime(2026, 2, 19, tzinfo=KST)
TRIP_END = datetime(2026, 2, 24, 23, 59, 59, tzinfo=KST)

SYSTEM_PROMPT_TEMPLATE = """너는 경주 가족여행 일정 관리 봇이야. 아래 JSON이 현재 여행 일정 데이터야.

[가족 정보]
- 인원: 아버지(당뇨 관리), 어머니(운전 담당), jojo, 아내, 히로(27개월, 밀/계란 알러지)
- 숙소: 까사멜로우(경주 북군동)
- 특별 일정: 2/22(일) 대구마라톤 (jojo)
- 오늘 날짜: {today}
- 여행 {day_status}

[규칙]
1. 사용자 메시지를 분석해서 JSON에서 변경할 부분이 있는지 판단해.
2. 변경이 필요하면, 수정된 전체 JSON을 ```json 코드블록 안에 출력해.
3. 변경이 없고 조회/추천/대화만이면, 한국어로 간결하게 답변해. JSON은 출력하지 마.
4. 변경 시 반드시 meta.lastUpdated를 현재 시각(KST, ISO8601)으로, meta.updateNote를 변경 요약으로 업데이트해.
5. 식당 추천 시 아버지 당뇨(dad 필드)와 히로 알러지(hiro 필드)를 반드시 고려해.
6. 응답은 한국어로, 간결하고 친근하게.

[현재 데이터]
{json_data}

[사용자 메시지]
{user_message}"""


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


def build_prompt(json_data: dict, user_message: str) -> str:
    """
    최종 프롬프트를 생성한다.

    Args:
        json_data: jsonbin에서 가져온 현재 여행 데이터
        user_message: 사용자가 텔레그램에 보낸 메시지

    Returns:
        Claude CLI에 전달할 완성된 프롬프트 문자열
    """
    now = datetime.now(KST)
    today = now.strftime("%Y-%m-%d (%a)")
    day_status = _get_day_status(now)

    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)

    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        today=today,
        day_status=day_status,
        json_data=json_str,
        user_message=user_message,
    )

    logger.debug("프롬프트 생성 완료 (길이: %d자)", len(prompt))
    return prompt
