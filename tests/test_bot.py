"""
bot 모듈 기본 테스트.

mock을 사용하여 텔레그램 API, jsonbin, claude_handler를 모킹한다.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

# src/ 디렉토리를 모듈 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

# 환경 변수 설정 (bot.py 임포트 시 필요)
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
os.environ["JSONBIN_BIN_ID"] = "test_bin_id"
os.environ["JSONBIN_API_KEY"] = "test_api_key"
os.environ["ALLOWED_USER_IDS"] = "12345,67890"
os.environ["USE_TOOL_API"] = "false"  # 테스트는 CLI 모드(레거시)로 실행

# bot.py 임포트 시도
bot_available = False
try:
    import bot
    bot_available = True
except Exception as e:
    _import_error = str(e)

SAMPLE_DATA = {
    "meta": {"lastUpdated": "2026-02-10T09:00:00+09:00", "updateNote": "초기"},
    "days": [],
    "reference": {},
}


def run_async(coro):
    """async 테스트를 동기적으로 실행하는 헬퍼"""
    return asyncio.get_event_loop().run_until_complete(coro)


@unittest.skipIf(not bot_available, "bot 모듈 미구현")
class TestAllowedUsers(unittest.TestCase):
    """허용 사용자 필터링 테스트"""

    def test_allowed_user_ids_parsing(self):
        """ALLOWED_USER_IDS 환경 변수가 올바르게 파싱되어야 한다"""
        self.assertIsInstance(bot.ALLOWED_USER_IDS, list)
        self.assertIn(12345, bot.ALLOWED_USER_IDS)
        self.assertIn(67890, bot.ALLOWED_USER_IDS)

    def test_is_allowed_true(self):
        """허용된 사용자 ID는 True를 반환해야 한다"""
        self.assertTrue(bot._is_allowed(12345))

    def test_is_allowed_false(self):
        """허용되지 않은 사용자 ID는 False를 반환해야 한다"""
        self.assertFalse(bot._is_allowed(99999))


@unittest.skipIf(not bot_available, "bot 모듈 미구현")
class TestHandleMessage(unittest.TestCase):
    """handle_message 함수 테스트"""

    def _make_update(self, user_id: int, text: str):
        """테스트용 Update 객체 생성"""
        update = MagicMock()
        update.effective_user.id = user_id
        update.message.text = text
        update.message.reply_text = AsyncMock()
        update.message.chat_id = 12345
        return update

    @patch.object(bot, "process_message")
    @patch.object(bot, "jsonbin")
    def test_unauthorized_user_ignored(self, mock_jsonbin, mock_process):
        """허용되지 않은 사용자의 메시지는 무시해야 한다"""
        update = self._make_update(user_id=99999, text="일정 보여줘")
        context = MagicMock()

        run_async(bot.handle_message(update, context))

        # process_message가 호출되지 않아야 한다
        mock_process.assert_not_called()
        # reply_text도 호출되지 않아야 한다
        update.message.reply_text.assert_not_called()

    @patch.object(bot, "process_message")
    @patch.object(bot, "jsonbin")
    def test_authorized_user_text_response(self, mock_jsonbin, mock_process):
        """허용된 사용자의 메시지에 대해 텍스트 응답을 전송해야 한다"""
        from claude_handler import ClaudeResponse

        mock_jsonbin.get_data.return_value = SAMPLE_DATA
        mock_process.return_value = ClaudeResponse(
            success=True,
            response_type="text",
            text_response="오늘 일정이에요!",
            updated_json=None,
            error_message=None,
        )

        update = self._make_update(user_id=12345, text="오늘 일정")
        context = MagicMock()

        run_async(bot.handle_message(update, context))

        # reply_text가 호출되어야 한다
        update.message.reply_text.assert_called()

    @patch.object(bot, "process_message")
    @patch.object(bot, "jsonbin")
    def test_authorized_user_update_response(self, mock_jsonbin, mock_process):
        """JSON 업데이트 응답 시 jsonbin PUT 후 확인 메시지를 전송해야 한다"""
        from claude_handler import ClaudeResponse

        updated = {**SAMPLE_DATA, "meta": {"lastUpdated": "2026-02-10T10:00:00+09:00", "updateNote": "저녁 확정"}}
        mock_jsonbin.get_data.return_value = SAMPLE_DATA
        mock_jsonbin.put_data.return_value = True
        mock_process.return_value = ClaudeResponse(
            success=True,
            response_type="update",
            text_response="업데이트 완료!",
            updated_json=updated,
            error_message=None,
        )

        update = self._make_update(user_id=12345, text="저녁 복길로 확정")
        context = MagicMock()

        run_async(bot.handle_message(update, context))

        # jsonbin PUT이 호출되어야 한다
        mock_jsonbin.put_data.assert_called_once_with(updated)
        # 확인 메시지가 전송되어야 한다
        update.message.reply_text.assert_called()


@unittest.skipIf(not bot_available, "bot 모듈 미구현")
class TestStartCommand(unittest.TestCase):
    """start 명령어 테스트"""

    def test_start_command_replies(self):
        """/start 명령어에 인사 메시지를 응답해야 한다"""
        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        run_async(bot.start_command(update, context))

        update.message.reply_text.assert_called_once()
        reply_text = update.message.reply_text.call_args[0][0]
        self.assertIn("경주", reply_text)

    def test_start_command_unauthorized(self):
        """/start 명령어 - 비허용 사용자는 무시해야 한다"""
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        run_async(bot.start_command(update, context))

        update.message.reply_text.assert_not_called()


@unittest.skipIf(not bot_available, "bot 모듈 미구현")
class TestSendLongMessage(unittest.TestCase):
    """긴 메시지 분할 전송 테스트"""

    def test_short_message_single_send(self):
        """4096자 이하 메시지는 한 번에 전송해야 한다"""
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        run_async(bot._send_long_message(update, "짧은 메시지"))

        update.message.reply_text.assert_called_once_with("짧은 메시지")

    def test_long_message_split(self):
        """4096자 초과 메시지는 분할 전송해야 한다"""
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        long_text = "가" * 5000
        run_async(bot._send_long_message(update, long_text))

        # 2번 호출되어야 한다 (4096 + 904)
        self.assertEqual(update.message.reply_text.call_count, 2)


if __name__ == "__main__":
    unittest.main()
