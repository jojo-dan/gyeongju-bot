"""
jsonbin.io API 클라이언트 모듈.

jsonbin.io의 GET/PUT API를 통해 여행 일정 JSON 데이터를 읽고 쓴다.
로컬 캐시를 유지하여 jsonbin 장애 시 폴백으로 사용한다.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# 한국 표준시 (UTC+9)
KST = timezone(timedelta(hours=9))

# 타임아웃 (초)
REQUEST_TIMEOUT = 15


class JsonBinError(Exception):
    """jsonbin.io API 호출 실패 시 발생하는 예외"""
    pass


class JsonBinClient:
    """jsonbin.io GET/PUT 클라이언트"""

    def __init__(self, bin_id: str, api_key: str) -> None:
        """
        클라이언트 초기화.

        Args:
            bin_id: jsonbin.io Bin ID
            api_key: jsonbin.io Master Key
        """
        self.bin_id = bin_id
        self.api_key = api_key
        self.base_url = "https://api.jsonbin.io/v3/b"
        self._cache: Optional[dict] = None

    @property
    def _headers(self) -> dict:
        """공통 요청 헤더"""
        return {
            "X-Master-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def get_data(self) -> dict:
        """
        현재 여행 데이터를 jsonbin.io에서 가져온다.

        성공 시 로컬 캐시에 저장한다.
        실패 시 캐시가 있으면 캐시를 반환하고, 없으면 예외를 발생시킨다.

        Returns:
            여행 일정 JSON 데이터 (dict)

        Raises:
            JsonBinError: API 호출 실패 시 (캐시도 없는 경우)
        """
        url = f"{self.base_url}/{self.bin_id}/latest"

        try:
            response = requests.get(
                url,
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()
            # jsonbin v3 응답에서 record 추출
            record = data.get("record", data)

            # 캐시 업데이트
            self._cache = record
            logger.info("jsonbin GET 성공, 캐시 업데이트 완료")
            return record

        except requests.exceptions.Timeout:
            logger.error("jsonbin GET 타임아웃 (%d초)", REQUEST_TIMEOUT)
            return self._fallback_to_cache("타임아웃")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            self._log_http_error(status_code)
            return self._fallback_to_cache(f"HTTP {status_code}")

        except requests.exceptions.ConnectionError:
            logger.error("jsonbin GET 연결 실패")
            return self._fallback_to_cache("연결 실패")

        except requests.exceptions.RequestException as e:
            logger.error("jsonbin GET 요청 실패: %s", e)
            return self._fallback_to_cache(str(e))

    def put_data(self, data: dict) -> bool:
        """
        여행 데이터를 jsonbin.io에 업데이트한다.

        업데이트 전 meta.lastUpdated를 현재 KST 시각으로 설정한다.

        Args:
            data: 업데이트할 여행 일정 JSON 데이터

        Returns:
            성공 여부 (bool)

        Raises:
            JsonBinError: API 호출 실패 시
        """
        url = f"{self.base_url}/{self.bin_id}"

        # meta.lastUpdated를 현재 KST 시각으로 업데이트
        self._update_last_updated(data)

        try:
            response = requests.put(
                url,
                json=data,
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            # 성공 시 캐시도 업데이트
            self._cache = data
            logger.info("jsonbin PUT 성공, 데이터 업데이트 완료")
            return True

        except requests.exceptions.Timeout:
            logger.error("jsonbin PUT 타임아웃 (%d초)", REQUEST_TIMEOUT)
            raise JsonBinError(f"jsonbin PUT 타임아웃 ({REQUEST_TIMEOUT}초)")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            self._log_http_error(status_code)
            raise JsonBinError(f"jsonbin PUT 실패: HTTP {status_code}")

        except requests.exceptions.ConnectionError:
            logger.error("jsonbin PUT 연결 실패")
            raise JsonBinError("jsonbin PUT 연결 실패")

        except requests.exceptions.RequestException as e:
            logger.error("jsonbin PUT 요청 실패: %s", e)
            raise JsonBinError(f"jsonbin PUT 요청 실패: {e}")

    def get_cached(self) -> Optional[dict]:
        """
        캐시된 데이터를 반환한다.

        jsonbin 장애 시 폴백으로 사용한다.

        Returns:
            캐시된 여행 데이터 또는 None
        """
        return self._cache

    def _fallback_to_cache(self, reason: str) -> dict:
        """
        캐시 폴백 처리.

        Args:
            reason: 원래 요청 실패 사유

        Returns:
            캐시된 데이터

        Raises:
            JsonBinError: 캐시도 없는 경우
        """
        if self._cache is not None:
            logger.warning("jsonbin GET 실패 (%s), 캐시 데이터 사용", reason)
            return self._cache
        raise JsonBinError(f"jsonbin GET 실패 ({reason}), 캐시 없음")

    @staticmethod
    def _update_last_updated(data: dict) -> None:
        """
        data의 meta.lastUpdated를 현재 KST 시각(ISO8601)으로 업데이트한다.

        Args:
            data: 여행 일정 데이터
        """
        if "meta" not in data:
            data["meta"] = {}
        now_kst = datetime.now(KST)
        data["meta"]["lastUpdated"] = now_kst.isoformat()

    @staticmethod
    def _log_http_error(status_code: Optional[int]) -> None:
        """
        HTTP 상태 코드별 에러 로깅.

        Args:
            status_code: HTTP 상태 코드
        """
        error_messages = {
            401: "인증 실패 - API 키를 확인하세요",
            403: "접근 거부 - 권한을 확인하세요",
            404: "Bin을 찾을 수 없음 - Bin ID를 확인하세요",
            422: "잘못된 데이터 형식",
            429: "요청 한도 초과 - 잠시 후 다시 시도하세요",
            500: "jsonbin 서버 내부 오류",
        }
        message = error_messages.get(status_code, f"HTTP 오류 ({status_code})")
        logger.error("jsonbin 오류: %s", message)
