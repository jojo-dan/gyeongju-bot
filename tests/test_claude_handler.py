"""
claude_handler 모듈 테스트.

mock subprocess를 사용하여 실제 Claude CLI를 호출하지 않고 테스트한다.
"""

import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from typing import Optional

# src/ 디렉토리를 모듈 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

# claude_handler가 아직 작성되지 않았을 수 있으므로 임포트 시도
try:
    from claude_handler import process_message, ClaudeResponse
except ImportError:
    # 모듈이 없으면 테스트에서 사용할 스텁 정의
    @dataclass
    class ClaudeResponse:
        success: bool
        response_type: str
        text_response: str
        updated_json: Optional[dict]
        error_message: Optional[str]

    process_message = None


SAMPLE_JSON = {
    "meta": {
        "lastUpdated": "2026-02-10T09:00:00+09:00",
        "updateNote": "초기 데이터",
    },
    "days": [
        {
            "date": "2026-02-19",
            "dow": "목",
            "dayNum": 1,
            "title": "출발 & 도착",
            "items": [
                {
                    "id": "d1_dinner",
                    "time": "18:00~",
                    "cat": "meal",
                    "title": "저녁 식사",
                    "options": [],
                    "chosen": "",
                    "status": "planned",
                    "note": "",
                }
            ],
        }
    ],
    "reference": {},
}


@unittest.skipIf(process_message is None, "claude_handler 모듈 미구현")
class TestProcessMessage(unittest.TestCase):
    """process_message 함수 테스트"""

    @patch("claude_handler.subprocess.run")
    def test_json_update_response(self, mock_run):
        """JSON 코드블록이 있는 응답은 update 타입이어야 한다"""
        updated_json = {**SAMPLE_JSON, "meta": {"lastUpdated": "2026-02-10T10:00:00+09:00", "updateNote": "저녁 확정"}}
        claude_output = f"저녁 식사를 확정했어요!\n\n```json\n{json.dumps(updated_json, ensure_ascii=False)}\n```"

        mock_run.return_value = MagicMock(
            stdout=claude_output,
            stderr="",
            returncode=0,
        )

        result = process_message(SAMPLE_JSON, "저녁 복길로 확정")

        self.assertTrue(result.success)
        self.assertEqual(result.response_type, "update")
        self.assertIsNotNone(result.updated_json)
        self.assertIsNone(result.error_message)

    @patch("claude_handler.subprocess.run")
    def test_text_response(self, mock_run):
        """JSON 코드블록이 없는 응답은 text 타입이어야 한다"""
        claude_output = "오늘 일정은 대릉원 관람과 점심 식사가 있어요!"

        mock_run.return_value = MagicMock(
            stdout=claude_output,
            stderr="",
            returncode=0,
        )

        result = process_message(SAMPLE_JSON, "오늘 일정 알려줘")

        self.assertTrue(result.success)
        self.assertEqual(result.response_type, "text")
        self.assertIn("대릉원", result.text_response)
        self.assertIsNone(result.updated_json)
        self.assertIsNone(result.error_message)

    @patch("claude_handler.subprocess.run")
    def test_subprocess_timeout(self, mock_run):
        """subprocess 타임아웃 시 error 타입을 반환해야 한다"""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=120)

        result = process_message(SAMPLE_JSON, "오늘 일정 알려줘")

        self.assertFalse(result.success)
        self.assertEqual(result.response_type, "error")
        self.assertIsNotNone(result.error_message)

    @patch("claude_handler.subprocess.run")
    def test_auth_error_detection(self, mock_run):
        """stderr에 인증 관련 키워드가 있으면 error 타입이어야 한다"""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="OAuth token expired. Please login again.",
            returncode=1,
        )

        result = process_message(SAMPLE_JSON, "일정 보여줘")

        self.assertFalse(result.success)
        self.assertEqual(result.response_type, "error")

    @patch("claude_handler.subprocess.run")
    def test_empty_stdout(self, mock_run):
        """stdout이 비어있으면 error 타입을 반환해야 한다"""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="",
            returncode=0,
        )

        result = process_message(SAMPLE_JSON, "테스트")

        self.assertFalse(result.success)
        self.assertEqual(result.response_type, "error")

    @patch("claude_handler.subprocess.run")
    def test_invalid_json_in_code_block(self, mock_run):
        """코드블록 내 JSON이 유효하지 않으면 텍스트 응답으로 폴백해야 한다"""
        claude_output = "업데이트할게요!\n\n```json\n{invalid json}\n```"

        mock_run.return_value = MagicMock(
            stdout=claude_output,
            stderr="",
            returncode=0,
        )

        result = process_message(SAMPLE_JSON, "테스트")

        # JSON 파싱 실패 시 텍스트 응답으로 폴백
        self.assertTrue(result.success)
        self.assertEqual(result.response_type, "text")
        self.assertIsNone(result.updated_json)

    @patch("claude_handler.subprocess.run")
    def test_nonzero_returncode_with_stderr(self, mock_run):
        """returncode가 0이 아니고 stderr가 있으면 error 타입이어야 한다"""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="Error: something went wrong",
            returncode=1,
        )

        result = process_message(SAMPLE_JSON, "테스트")

        self.assertFalse(result.success)
        self.assertEqual(result.response_type, "error")


@unittest.skipIf(process_message is None, "claude_handler 모듈 미구현")
class TestClaudeResponse(unittest.TestCase):
    """ClaudeResponse 데이터클래스 테스트"""

    def test_create_update_response(self):
        """update 타입 응답 생성"""
        resp = ClaudeResponse(
            success=True,
            response_type="update",
            text_response="업데이트 완료!",
            updated_json={"meta": {}},
            error_message=None,
        )
        self.assertTrue(resp.success)
        self.assertEqual(resp.response_type, "update")

    def test_create_text_response(self):
        """text 타입 응답 생성"""
        resp = ClaudeResponse(
            success=True,
            response_type="text",
            text_response="오늘 일정은...",
            updated_json=None,
            error_message=None,
        )
        self.assertTrue(resp.success)
        self.assertIsNone(resp.updated_json)

    def test_create_error_response(self):
        """error 타입 응답 생성"""
        resp = ClaudeResponse(
            success=False,
            response_type="error",
            text_response="",
            updated_json=None,
            error_message="타임아웃",
        )
        self.assertFalse(resp.success)
        self.assertEqual(resp.error_message, "타임아웃")


if __name__ == "__main__":
    unittest.main()
