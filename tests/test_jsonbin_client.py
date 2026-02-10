"""
jsonbin_client 모듈 테스트.

mock을 사용하여 실제 jsonbin.io API를 호출하지 않고 테스트한다.
"""

import unittest
from unittest.mock import patch, MagicMock

from jsonbin_client import JsonBinClient, JsonBinError, KST


class TestJsonBinClient(unittest.TestCase):
    """JsonBinClient 클래스 테스트"""

    def setUp(self):
        """각 테스트 전 클라이언트 인스턴스 초기화"""
        self.client = JsonBinClient(
            bin_id="test_bin_id",
            api_key="test_api_key",
        )
        self.sample_data = {
            "meta": {
                "lastUpdated": "2026-02-10T09:00:00+09:00",
                "updateNote": "테스트 데이터",
            },
            "days": [],
            "reference": {},
        }

    # --- GET 테스트 ---

    @patch("jsonbin_client.requests.get")
    def test_get_data_success(self, mock_get):
        """GET 성공 시 record 데이터를 반환해야 한다"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"record": self.sample_data}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_data()

        self.assertEqual(result, self.sample_data)
        mock_get.assert_called_once()
        # 캐시에도 저장되어야 한다
        self.assertEqual(self.client.get_cached(), self.sample_data)

    @patch("jsonbin_client.requests.get")
    def test_get_data_success_without_record_wrapper(self, mock_get):
        """record 키 없이 직접 데이터가 올 경우도 처리해야 한다"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_data()

        self.assertEqual(result, self.sample_data)

    @patch("jsonbin_client.requests.get")
    def test_get_data_timeout_with_cache(self, mock_get):
        """GET 타임아웃 시 캐시가 있으면 캐시를 반환해야 한다"""
        import requests as req

        self.client._cache = self.sample_data
        mock_get.side_effect = req.exceptions.Timeout("timeout")

        result = self.client.get_data()

        self.assertEqual(result, self.sample_data)

    @patch("jsonbin_client.requests.get")
    def test_get_data_timeout_without_cache(self, mock_get):
        """GET 타임아웃 시 캐시가 없으면 예외를 발생시켜야 한다"""
        import requests as req

        mock_get.side_effect = req.exceptions.Timeout("timeout")

        with self.assertRaises(JsonBinError) as ctx:
            self.client.get_data()

        self.assertIn("타임아웃", str(ctx.exception))

    @patch("jsonbin_client.requests.get")
    def test_get_data_http_error_with_cache(self, mock_get):
        """HTTP 에러 시 캐시가 있으면 캐시를 반환해야 한다"""
        import requests as req

        self.client._cache = self.sample_data
        mock_response = MagicMock()
        mock_response.status_code = 500
        http_error = req.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = MagicMock()
        mock_get.return_value.raise_for_status.side_effect = http_error

        result = self.client.get_data()

        self.assertEqual(result, self.sample_data)

    @patch("jsonbin_client.requests.get")
    def test_get_data_http_404_without_cache(self, mock_get):
        """HTTP 404 시 캐시가 없으면 예외를 발생시켜야 한다"""
        import requests as req

        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = req.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = MagicMock()
        mock_get.return_value.raise_for_status.side_effect = http_error

        with self.assertRaises(JsonBinError):
            self.client.get_data()

    @patch("jsonbin_client.requests.get")
    def test_get_data_connection_error_with_cache(self, mock_get):
        """연결 실패 시 캐시 폴백"""
        import requests as req

        self.client._cache = self.sample_data
        mock_get.side_effect = req.exceptions.ConnectionError("conn error")

        result = self.client.get_data()

        self.assertEqual(result, self.sample_data)

    # --- PUT 테스트 ---

    @patch("jsonbin_client.requests.put")
    def test_put_data_success(self, mock_put):
        """PUT 성공 시 True를 반환하고 캐시를 업데이트해야 한다"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        data = {"meta": {"updateNote": "테스트"}, "days": []}
        result = self.client.put_data(data)

        self.assertTrue(result)
        # meta.lastUpdated가 자동으로 설정되어야 한다
        self.assertIn("lastUpdated", data["meta"])
        # 캐시에도 저장되어야 한다
        self.assertEqual(self.client.get_cached(), data)

    @patch("jsonbin_client.requests.put")
    def test_put_data_updates_last_updated(self, mock_put):
        """PUT 전 meta.lastUpdated가 KST 현재 시각으로 업데이트되어야 한다"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        data = {"meta": {"lastUpdated": "old_value"}, "days": []}
        self.client.put_data(data)

        # lastUpdated가 "old_value"가 아니어야 한다
        self.assertNotEqual(data["meta"]["lastUpdated"], "old_value")
        # ISO 8601 형식이어야 한다 ("+09:00" 포함)
        self.assertIn("+09:00", data["meta"]["lastUpdated"])

    @patch("jsonbin_client.requests.put")
    def test_put_data_creates_meta_if_missing(self, mock_put):
        """meta 키가 없는 데이터에도 meta.lastUpdated를 추가해야 한다"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        data = {"days": []}
        self.client.put_data(data)

        self.assertIn("meta", data)
        self.assertIn("lastUpdated", data["meta"])

    @patch("jsonbin_client.requests.put")
    def test_put_data_timeout(self, mock_put):
        """PUT 타임아웃 시 JsonBinError를 발생시켜야 한다"""
        import requests as req

        mock_put.side_effect = req.exceptions.Timeout("timeout")

        with self.assertRaises(JsonBinError) as ctx:
            self.client.put_data({"meta": {}, "days": []})

        self.assertIn("타임아웃", str(ctx.exception))

    @patch("jsonbin_client.requests.put")
    def test_put_data_http_error(self, mock_put):
        """PUT HTTP 에러 시 JsonBinError를 발생시켜야 한다"""
        import requests as req

        mock_response = MagicMock()
        mock_response.status_code = 401
        http_error = req.exceptions.HTTPError(response=mock_response)
        mock_put.return_value = MagicMock()
        mock_put.return_value.raise_for_status.side_effect = http_error

        with self.assertRaises(JsonBinError) as ctx:
            self.client.put_data({"meta": {}, "days": []})

        self.assertIn("401", str(ctx.exception))

    @patch("jsonbin_client.requests.put")
    def test_put_data_connection_error(self, mock_put):
        """PUT 연결 실패 시 JsonBinError를 발생시켜야 한다"""
        import requests as req

        mock_put.side_effect = req.exceptions.ConnectionError("conn error")

        with self.assertRaises(JsonBinError):
            self.client.put_data({"meta": {}, "days": []})

    # --- 캐시 테스트 ---

    def test_get_cached_initially_none(self):
        """초기 상태에서 캐시는 None이어야 한다"""
        self.assertIsNone(self.client.get_cached())

    @patch("jsonbin_client.requests.get")
    def test_cache_updated_after_successful_get(self, mock_get):
        """GET 성공 후 캐시가 업데이트되어야 한다"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"record": self.sample_data}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.client.get_data()

        self.assertEqual(self.client.get_cached(), self.sample_data)

    # --- 헤더 테스트 ---

    def test_headers_contain_required_fields(self):
        """요청 헤더에 X-Master-Key와 Content-Type이 포함되어야 한다"""
        headers = self.client._headers
        self.assertEqual(headers["X-Master-Key"], "test_api_key")
        self.assertEqual(headers["Content-Type"], "application/json")

    # --- URL 구성 테스트 ---

    @patch("jsonbin_client.requests.get")
    def test_get_url_format(self, mock_get):
        """GET 요청 URL이 올바른 형식이어야 한다"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"record": self.sample_data}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.client.get_data()

        call_args = mock_get.call_args
        url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        self.assertIn("test_bin_id/latest", url)

    @patch("jsonbin_client.requests.put")
    def test_put_url_format(self, mock_put):
        """PUT 요청 URL이 올바른 형식이어야 한다"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        self.client.put_data({"meta": {}, "days": []})

        call_args = mock_put.call_args
        url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        self.assertIn("test_bin_id", url)
        self.assertNotIn("latest", url)


if __name__ == "__main__":
    unittest.main()
