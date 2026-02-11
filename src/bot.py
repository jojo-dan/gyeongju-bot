"""
경주 가족여행 텔레그램 봇 (엔트리포인트)

텔레그램 메시지를 수신하여 Anthropic API(Tool Use) 또는 Claude CLI로 처리하고,
jsonbin.io의 여행 데이터를 업데이트하거나 조회 결과를 응답한다.

USE_TOOL_API=true (기본): Anthropic SDK + Tool Use
USE_TOOL_API=false: Claude CLI subprocess (레거시, 롤백용)
"""

import asyncio
import os
import logging
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from jsonbin_client import JsonBinClient

# 환경 변수 로드
load_dotenv()

# API 모드 전환 (기본: Tool Use API)
USE_TOOL_API = os.getenv("USE_TOOL_API", "true").lower() in ("true", "1", "yes")

if USE_TOOL_API:
    from claude_api_handler import process_message_api
else:
    from claude_handler import process_message

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# 설정값
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
JSONBIN_BIN_ID = os.getenv("JSONBIN_BIN_ID", "")
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY", "")
ALLOWED_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
]

# 텔레그램 메시지 길이 제한
MAX_MESSAGE_LENGTH = 4096

# 한국 표준시
KST = timezone(timedelta(hours=9))

# jsonbin 클라이언트 (전역 인스턴스)
jsonbin = JsonBinClient(bin_id=JSONBIN_BIN_ID, api_key=JSONBIN_API_KEY)


def _is_allowed(user_id: int) -> bool:
    """허용된 사용자인지 확인한다."""
    return user_id in ALLOWED_USER_IDS


async def _send_long_message(update: Update, text: str) -> None:
    """긴 메시지를 4096자 단위로 분할하여 전송한다."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text)
        return

    # 4096자 단위로 분할
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        chunk = text[i : i + MAX_MESSAGE_LENGTH]
        await update.message.reply_text(chunk)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start 명령어 핸들러"""
    user_id = update.effective_user.id
    if not _is_allowed(user_id):
        logger.warning("허용되지 않은 사용자의 /start: %d", user_id)
        return

    welcome = (
        "안녕! 경주 가족여행 봇이야 :)\n\n"
        "여행 일정을 자연어로 관리할 수 있어.\n\n"
        "사용 예시:\n"
        '- "내일 점심 복길로 확정"\n'
        '- "대릉원 다녀왔어"\n'
        '- "오늘 일정 알려줘"\n'
        '- "아버지한테 괜찮은 저녁?"\n\n'
        "명령어:\n"
        "/today - 오늘 일정 요약\n"
    )
    await update.message.reply_text(welcome)


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/today 명령어 핸들러 - 오늘 일정 요약 숏컷"""
    user_id = update.effective_user.id
    if not _is_allowed(user_id):
        logger.warning("허용되지 않은 사용자의 /today: %d", user_id)
        return

    logger.info("/today 명령어 수신 (user: %d)", user_id)
    await _handle_user_message(update, "오늘 일정 알려줘")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """텍스트 메시지 핸들러"""
    user_id = update.effective_user.id
    if not _is_allowed(user_id):
        logger.warning("허용되지 않은 사용자: %d", user_id)
        return

    user_message = update.message.text
    if not user_message:
        return

    logger.info("메시지 수신 (user: %d): %s", user_id, user_message[:100])
    await _handle_user_message(update, user_message)


async def _handle_user_message(update: Update, user_message: str) -> None:
    """
    사용자 메시지를 처리하는 핵심 로직.

    USE_TOOL_API=true: Anthropic API + Tool Use (기본)
    USE_TOOL_API=false: Claude CLI subprocess (레거시)
    """
    try:
        # 0. 타이핑 표시
        await update.message.chat.send_action(ChatAction.TYPING)

        # 1. 현재 데이터 가져오기
        try:
            json_data = jsonbin.get_data()
        except Exception as e:
            logger.error("jsonbin 데이터 조회 실패: %s", e)
            cached = jsonbin.get_cached()
            if cached:
                logger.info("캐시된 데이터로 대체")
                json_data = cached
            else:
                await update.message.reply_text(
                    "데이터를 가져오는 데 문제가 있어요. 잠시 후 다시 시도해주세요."
                )
                return

        # 2. 타이핑 표시 유지
        typing_active = True

        async def _keep_typing():
            while typing_active:
                await asyncio.sleep(4)
                if typing_active:
                    try:
                        await update.message.chat.send_action(ChatAction.TYPING)
                    except Exception:
                        pass

        typing_task = asyncio.create_task(_keep_typing())

        try:
            if USE_TOOL_API:
                reply = await _process_with_api(json_data, user_message)
            else:
                reply = await _process_with_cli(json_data, user_message)
        finally:
            typing_active = False
            typing_task.cancel()

        # 3. 응답 전송
        await _send_long_message(update, reply)

    except Exception as e:
        logger.error("메시지 처리 중 예외: %s", e, exc_info=True)
        await update.message.reply_text(
            "처리 중 문제가 발생했어요. 잠시 후 다시 시도해주세요."
        )


async def _process_with_api(json_data: dict, user_message: str) -> str:
    """Anthropic API + Tool Use로 메시지를 처리한다."""
    response = await process_message_api(json_data, user_message)

    if response.error:
        logger.error("API 에러: %s", response.error)

    # 데이터 변경이 있으면 jsonbin에 저장
    if response.data_modified and response.updated_data:
        try:
            success = jsonbin.put_data(response.updated_data)
            if not success:
                logger.error("jsonbin PUT 실패")
        except Exception as e:
            logger.error("jsonbin PUT 실패: %s", e)

    return response.text or "처리 중 문제가 발생했어요."


async def _process_with_cli(json_data: dict, user_message: str) -> str:
    """Claude CLI subprocess로 메시지를 처리한다 (레거시)."""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, process_message, json_data, user_message
    )

    if response.response_type == "update" and response.updated_json:
        try:
            success = jsonbin.put_data(response.updated_json)
            if success:
                update_note = response.updated_json.get("meta", {}).get(
                    "updateNote", "업데이트"
                )
                return f"업데이트 완료! ({update_note})"
            else:
                return "데이터 업데이트에 실패했어요. 다시 시도해주세요."
        except Exception as e:
            logger.error("jsonbin PUT 실패: %s", e)
            return "데이터 저장 중 문제가 발생했어요."

    elif response.response_type == "text":
        return response.text_response

    else:
        if response.error_message:
            logger.error("Claude 에러: %s", response.error_message)
        return response.text_response


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """전역 에러 핸들러"""
    logger.error("봇 에러 발생: %s", context.error, exc_info=context.error)


def main() -> None:
    """봇을 시작한다."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다")
        return

    if not ALLOWED_USER_IDS:
        logger.warning("ALLOWED_USER_IDS가 비어 있습니다. 모든 메시지가 무시됩니다.")

    mode = "Anthropic API (Tool Use)" if USE_TOOL_API else "Claude CLI (레거시)"
    logger.info("봇 시작 (모드: %s, 허용 사용자: %s)", mode, ALLOWED_USER_IDS)

    # Application 빌더 패턴으로 봇 초기화
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # 명령어 핸들러 등록
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("today", today_command))

    # 텍스트 메시지 핸들러 등록
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 에러 핸들러 등록
    app.add_error_handler(error_handler)

    # 폴링 시작
    app.run_polling()


if __name__ == "__main__":
    main()
