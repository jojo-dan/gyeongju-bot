"""웹앱용 HTTP API 서버

웹앱에서 포저(AI 여행 보좌관)와 직접 대화할 수 있도록
HTTP API 엔드포인트를 제공한다.

기존 텔레그램 봇과 동일한 process_message_api() 로직을 재사용하며,
별도 프로세스로 실행된다 (systemd: gyeongju-web-api.service).

엔드포인트:
    POST /chat  - 포저와 대화
    GET  /health - 헬스체크
"""

import asyncio
import json
import logging
import os
import secrets
import time
from collections import defaultdict

from aiohttp import web
from dotenv import load_dotenv

from jsonbin_client import JsonBinClient
from claude_api_handler import process_message_api

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── 설정 ──────────────────────────────────────────────────────

JSONBIN_BIN_ID = os.getenv("JSONBIN_BIN_ID", "")
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY", "")
CHAT_SECRET = os.getenv("CHAT_SECRET", "")
WEB_API_PORT = int(os.getenv("WEB_API_PORT", "8080"))

# Rate limiting: IP당 분당 최대 요청 수
RATE_LIMIT_PER_MIN = 10

# jsonbin 클라이언트
jsonbin = JsonBinClient(bin_id=JSONBIN_BIN_ID, api_key=JSONBIN_API_KEY)

# Rate limiter 저장소: {ip: [timestamp, ...]}
_rate_store: dict[str, list[float]] = defaultdict(list)


# ── Rate Limiting ─────────────────────────────────────────────

def _check_rate_limit(ip: str) -> bool:
    """IP 기반 요청 제한을 확인한다. True이면 허용."""
    now = time.time()
    window = 60  # 1분

    # 만료된 타임스탬프 정리
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < window]

    if len(_rate_store[ip]) >= RATE_LIMIT_PER_MIN:
        return False

    _rate_store[ip].append(now)
    return True


# ── CORS 미들웨어 ─────────────────────────────────────────────

@web.middleware
async def cors_middleware(request, handler):
    """CORS 헤더를 추가한다."""
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        try:
            response = await handler(request)
        except web.HTTPException as e:
            response = e

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response


# ── 핸들러 ────────────────────────────────────────────────────

async def health_handler(request: web.Request) -> web.Response:
    """헬스체크 엔드포인트"""
    return web.json_response({"status": "ok", "service": "gyeongju-web-api"})


async def chat_handler(request: web.Request) -> web.Response:
    """POST /chat — 포저와 대화

    Request JSON:
        {
            "message": "오늘 일정 알려줘",
            "secret": "비밀번호"
        }

    Response JSON:
        {
            "reply": "포저의 응답 텍스트",
            "data_modified": false
        }
    """
    # Rate limit 체크
    ip = request.remote or "unknown"
    if not _check_rate_limit(ip):
        return web.json_response(
            {"error": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."},
            status=429,
        )

    # 요청 파싱
    try:
        body = await request.json()
    except (json.JSONDecodeError, Exception):
        return web.json_response({"error": "잘못된 요청 형식"}, status=400)

    message = body.get("message", "").strip()
    secret = body.get("secret", "")

    if not message:
        return web.json_response({"error": "메시지가 비어있습니다"}, status=400)

    # 인증 확인
    if CHAT_SECRET and not secrets.compare_digest(secret, CHAT_SECRET):
        return web.json_response({"error": "인증 실패"}, status=401)

    logger.info("웹 챗 요청: %s (IP: %s)", message[:100], ip)

    # 데이터 조회
    try:
        json_data = jsonbin.get_data()
    except Exception as e:
        logger.error("jsonbin 데이터 조회 실패: %s", e)
        cached = jsonbin.get_cached()
        if cached:
            json_data = cached
        else:
            return web.json_response(
                {"error": "데이터를 가져올 수 없습니다"},
                status=503,
            )

    # AI 처리
    try:
        response = await process_message_api(json_data, message)
    except Exception as e:
        logger.error("AI 처리 중 에러: %s", e, exc_info=True)
        return web.json_response(
            {"error": "처리 중 문제가 발생했습니다"},
            status=500,
        )

    # 데이터 변경이 있으면 jsonbin에 저장
    if response.data_modified and response.updated_data:
        try:
            success = jsonbin.put_data(response.updated_data)
            if not success:
                logger.error("jsonbin PUT 실패 (웹 챗)")
        except Exception as e:
            logger.error("jsonbin PUT 실패 (웹 챗): %s", e)

    return web.json_response({
        "reply": response.text or "처리 중 문제가 발생했어요.",
        "data_modified": response.data_modified,
    })


# ── 앱 설정 ──────────────────────────────────────────────────

def create_app() -> web.Application:
    """aiohttp 앱을 생성한다."""
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/health", health_handler)
    app.router.add_post("/chat", chat_handler)
    return app


def main():
    """서버를 시작한다."""
    if not JSONBIN_BIN_ID or not JSONBIN_API_KEY:
        logger.error("JSONBIN_BIN_ID / JSONBIN_API_KEY가 설정되지 않았습니다")
        return

    if not CHAT_SECRET:
        logger.warning("CHAT_SECRET이 설정되지 않았습니다. 인증 없이 모든 요청을 허용합니다.")

    app = create_app()
    logger.info("웹 API 서버 시작 (포트: %d)", WEB_API_PORT)
    web.run_app(app, host="0.0.0.0", port=WEB_API_PORT)


if __name__ == "__main__":
    main()
