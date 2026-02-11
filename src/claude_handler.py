"""
Claude CLI subprocess 래퍼 모듈

Claude CLI를 subprocess로 호출하고, 응답을 파싱하여
JSON 변경 또는 텍스트 응답을 구분한다.
타임아웃, 재시도, 인증 만료 감지를 처리한다.
"""

import json
import logging
import re
import subprocess
from dataclasses import dataclass
from typing import Optional

from prompts import build_prompt

logger = logging.getLogger(__name__)

# Claude CLI 설정
CLAUDE_TIMEOUT = 120  # 초
MAX_RETRIES = 1

# 인증 에러 감지 키워드
AUTH_ERROR_KEYWORDS = ["authentication", "oauth", "expired", "401", "login"]

# JSON 코드블록 추출 정규식
JSON_BLOCK_PATTERN = re.compile(r"```json\s*\n(.*?)\n\s*```", re.DOTALL)


@dataclass
class ClaudeResponse:
    """Claude CLI 응답을 담는 데이터 클래스"""
    success: bool
    response_type: str  # "update" | "text" | "error"
    text_response: str  # 텔레그램에 보낼 메시지
    updated_json: Optional[dict] = None  # response_type이 "update"일 때만
    error_message: Optional[str] = None  # response_type이 "error"일 때만


def _is_auth_error(stderr: str) -> bool:
    """stderr에서 인증 관련 에러를 감지한다."""
    stderr_lower = stderr.lower()
    return any(kw in stderr_lower for kw in AUTH_ERROR_KEYWORDS)


def _parse_response(raw_output: str) -> ClaudeResponse:
    """
    Claude CLI의 원본 출력을 파싱한다.

    - ```json 코드블록이 있으면 → JSON 업데이트 응답
    - 없으면 → 텍스트 응답 (조회/추천/대화)
    """
    match = JSON_BLOCK_PATTERN.search(raw_output)

    if match:
        json_str = match.group(1).strip()
        try:
            updated_data = json.loads(json_str)
            logger.info("JSON 업데이트 응답 감지")
            return ClaudeResponse(
                success=True,
                response_type="update",
                text_response="업데이트 완료!",
                updated_json=updated_data,
            )
        except json.JSONDecodeError as e:
            logger.error("JSON 파싱 실패: %s", e)
            # JSON 파싱 실패 시 텍스트 응답으로 전환
            return ClaudeResponse(
                success=True,
                response_type="text",
                text_response=raw_output.strip(),
            )

    # JSON 코드블록 없음 → 텍스트 응답
    logger.info("텍스트 응답 감지")
    return ClaudeResponse(
        success=True,
        response_type="text",
        text_response=raw_output.strip(),
    )


def _call_claude(prompt: str) -> ClaudeResponse:
    """
    Claude CLI를 한 번 호출한다.

    Args:
        prompt: Claude에 전달할 전체 프롬프트

    Returns:
        ClaudeResponse 객체
    """
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT,
        )

        # stderr 확인 (인증 에러 감지)
        if result.stderr:
            logger.debug("Claude stderr: %s", result.stderr.strip())
            if _is_auth_error(result.stderr):
                logger.error("Claude 인증 만료 감지!")
                return ClaudeResponse(
                    success=False,
                    response_type="error",
                    text_response="Claude 인증이 만료되었어요. 서버에서 재인증이 필요합니다.",
                    error_message=f"인증 에러: {result.stderr.strip()}",
                )

        # 비정상 종료
        if result.returncode != 0:
            logger.error("Claude CLI 비정상 종료 (code: %d): %s", result.returncode, result.stderr.strip())
            return ClaudeResponse(
                success=False,
                response_type="error",
                text_response="Claude 처리 중 문제가 발생했어요.",
                error_message=f"종료 코드 {result.returncode}: {result.stderr.strip()}",
            )

        # 정상 응답 파싱
        if not result.stdout.strip():
            logger.warning("Claude가 빈 응답을 반환함")
            return ClaudeResponse(
                success=False,
                response_type="error",
                text_response="Claude로부터 응답을 받지 못했어요.",
                error_message="빈 응답",
            )

        return _parse_response(result.stdout)

    except subprocess.TimeoutExpired:
        logger.error("Claude CLI 타임아웃 (%d초)", CLAUDE_TIMEOUT)
        return ClaudeResponse(
            success=False,
            response_type="error",
            text_response="Claude 응답 시간이 초과되었어요. 잠시 후 다시 시도해주세요.",
            error_message=f"타임아웃 ({CLAUDE_TIMEOUT}초)",
        )
    except FileNotFoundError:
        logger.error("Claude CLI를 찾을 수 없음")
        return ClaudeResponse(
            success=False,
            response_type="error",
            text_response="서버에 Claude CLI가 설치되어 있지 않아요.",
            error_message="claude 명령어를 찾을 수 없음",
        )
    except Exception as e:
        logger.error("Claude CLI 호출 중 예외: %s", e)
        return ClaudeResponse(
            success=False,
            response_type="error",
            text_response="처리 중 문제가 발생했어요.",
            error_message=str(e),
        )


def process_message(json_data: dict, user_message: str) -> ClaudeResponse:
    """
    사용자 메시지를 Claude CLI로 처리한다.

    현재 JSON 데이터와 사용자 메시지로 프롬프트를 구성하고,
    Claude CLI를 호출하여 응답을 파싱한다.
    실패 시 1회 재시도한다.

    Args:
        json_data: jsonbin에서 가져온 현재 여행 데이터
        user_message: 사용자가 텔레그램에 보낸 메시지

    Returns:
        ClaudeResponse 객체
    """
    prompt = build_prompt(json_data, user_message)
    logger.info("Claude CLI 호출 시작 (프롬프트 길이: %d자)", len(prompt))

    # 첫 번째 시도
    response = _call_claude(prompt)

    # 성공 또는 인증 에러면 바로 반환 (재시도 불필요)
    if response.success or (response.error_message and "인증" in response.error_message):
        return response

    # 재시도 (네트워크 일시 장애 대비)
    logger.warning("첫 번째 시도 실패, 재시도 중... (%s)", response.error_message)
    retry_response = _call_claude(prompt)

    if retry_response.success:
        logger.info("재시도 성공")
        return retry_response

    logger.error("재시도도 실패: %s", retry_response.error_message)
    return retry_response
