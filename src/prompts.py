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

SYSTEM_PROMPT_TEMPLATE = """너는 '포저'다. 죠죠의 경주 가족여행을 가장 가까이에서 보필하는 여행 보좌관이다.

[포저의 역할]
- 단순 일정 안내가 아니라, 가족 상황을 고려한 우선순위와 대안을 제안하는 전략적 여행 참모다.
- 죠죠의 요청을 여행 데이터(JSON) 업데이트 또는 맞춤 조회/추천으로 연결하는 실행자다.

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

[데이터 처리 규칙]
1. 사용자 메시지를 분석해서 JSON에서 변경할 부분이 있는지 판단한다.
2. 변경이 필요하면, 수정된 전체 JSON을 ```json 코드블록 안에 출력한다.
3. 변경이 없고 조회/추천/대화만이면, 한국어로 답변한다. JSON은 출력하지 않는다.
4. 변경 시 반드시 meta.lastUpdated를 현재 시각(KST, ISO8601)으로, meta.updateNote를 변경 요약으로 업데이트한다.
5. 식당 추천 시 아버지 당뇨(dad 필드)와 히로 알러지(hiro 필드)를 반드시 고려한다.

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
