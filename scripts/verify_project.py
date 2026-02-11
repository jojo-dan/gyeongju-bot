"""
경주 봇 프로젝트 코드 무결성 검증 스크립트

프로젝트 구조, 모듈 임포트, 인터페이스 일관성, 프롬프트 정합성을 검증한다.
"""

import importlib
import os
import sys

# 프로젝트 루트와 src/ 경로 설정
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
sys.path.insert(0, os.path.join(_project_root, "src"))

PASS = "\u2705"
FAIL = "\u274C"

issues = []
checks = 0
passed = 0


def check(desc, cond, detail=""):
    global checks, passed
    checks += 1
    if cond:
        passed += 1
        print(f"  {PASS} {desc}")
    else:
        issues.append(f"{desc}: {detail}")
        print(f"  {FAIL} {desc} — {detail}")


# [1] 파일 구조
print("\n[1/6] 파일 구조 검증")
root = _project_root
for f in [
    "src/bot.py", "src/claude_handler.py", "src/jsonbin_client.py", "src/prompts.py",
    "src/claude_api_handler.py", "src/tool_definitions.py", "src/tool_executor.py",
    "requirements.txt", ".env.example", "gyeongju-bot.service", "README.md",
    "webapp/index.html", "tests/__init__.py", "tests/test_bot.py",
    "tests/test_claude_handler.py", "tests/test_jsonbin_client.py",
]:
    check(f"파일 존재: {f}", os.path.isfile(os.path.join(root, f)), "파일 없음")

# [2] 모듈 임포트
print("\n[2/6] 모듈 임포트 검증")
mod_attrs = {
    "prompts": ["build_prompt", "SYSTEM_PROMPT_TEMPLATE", "KST", "TRIP_START", "TRIP_END"],
    "claude_handler": ["process_message", "ClaudeResponse", "_is_auth_error", "_parse_response"],
    "jsonbin_client": ["JsonBinClient", "JsonBinError", "KST", "REQUEST_TIMEOUT"],
}
for mod_name, attrs in mod_attrs.items():
    try:
        mod = importlib.import_module(mod_name)
        check(f"임포트: {mod_name}", True)
        for a in attrs:
            check(f"  {mod_name}.{a}", hasattr(mod, a), "속성 없음")
    except Exception as e:
        check(f"임포트: {mod_name}", False, str(e))

# [3] ClaudeResponse
print("\n[3/6] ClaudeResponse 데이터클래스 검증")
try:
    from claude_handler import ClaudeResponse
    from dataclasses import fields as dc_fields
    field_names = {f.name for f in dc_fields(ClaudeResponse)}
    expected = {"success", "response_type", "text_response", "updated_json", "error_message"}
    check("필드 완전성", expected.issubset(field_names), f"누락: {expected - field_names}")
    r = ClaudeResponse(True, "update", "ok", {"k": 1})
    check("update 타입 생성", r.response_type == "update" and r.updated_json == {"k": 1})
    r = ClaudeResponse(True, "text", "hi")
    check("text 타입 생성", r.response_type == "text" and r.updated_json is None)
    r = ClaudeResponse(False, "error", "err", error_message="fail")
    check("error 타입 생성", r.error_message == "fail")
except Exception as e:
    check("ClaudeResponse", False, str(e))

# [4] JsonBinClient
print("\n[4/6] JsonBinClient 인터페이스 검증")
try:
    from jsonbin_client import JsonBinClient
    c = JsonBinClient("test_bin", "test_key")
    check("초기화", c.bin_id == "test_bin" and c.api_key == "test_key")
    check("base_url", "api.jsonbin.io" in c.base_url)
    check("캐시 초기값 None", c.get_cached() is None)
    for m in ["get_data", "put_data", "get_cached"]:
        check(f"{m}() 존재", callable(getattr(c, m, None)))
    h = c._headers
    check("헤더 X-Master-Key", "X-Master-Key" in h)
    check("헤더 Content-Type json", "json" in h.get("Content-Type", ""))
except Exception as e:
    check("JsonBinClient", False, str(e))

# [5] 프롬프트 생성
print("\n[5/6] 프롬프트 생성 검증")
try:
    from prompts import build_prompt, SYSTEM_PROMPT_TEMPLATE
    for label, kw in [
        ("가족 정보", "가족 정보"), ("규칙 섹션", "[규칙]"),
        ("당뇨", "당뇨"), ("알러지", "알러지"),
        ("까사멜로우", "까사멜로우"), ("마라톤", "마라톤"),
        ("JSON 코드블록", "```json"),
        ("{today}", "{today}"), ("{day_status}", "{day_status}"),
        ("{json_data}", "{json_data}"), ("{user_message}", "{user_message}"),
    ]:
        check(f"템플릿: {label}", kw in SYSTEM_PROMPT_TEMPLATE)
    p = build_prompt({"meta": {}, "days": []}, "테스트")
    check("build_prompt 실행", isinstance(p, str) and len(p) > 100)
    check("사용자 메시지 포함", "테스트" in p)
except Exception as e:
    check("프롬프트", False, str(e))

# [6] 응답 파싱
print("\n[6/6] 응답 파싱 검증")
try:
    from claude_handler import _parse_response, _is_auth_error
    r = _parse_response('text\n```json\n{"a":1}\n```\nmore')
    check("JSON 코드블록 → update", r.response_type == "update" and r.updated_json == {"a": 1})
    r = _parse_response("오늘 일정은 대릉원입니다.")
    check("텍스트 → text", r.response_type == "text")
    r = _parse_response('```json\n{bad}\n```')
    check("잘못된 JSON → text 폴백", r.response_type == "text")
    check("auth 감지: authentication", _is_auth_error("authentication failed"))
    check("auth 감지: 401", _is_auth_error("HTTP 401"))
    check("정상 stderr → False", not _is_auth_error("some warning"))
except Exception as e:
    check("파싱", False, str(e))

# 결과
print("\n" + "=" * 50)
print(f"검증 결과: {passed}/{checks} 통과")
if issues:
    print(f"\n이슈 {len(issues)}건:")
    for i, iss in enumerate(issues, 1):
        print(f"  {i}. {iss}")
else:
    print("모든 항목 통과! 이슈 0건.")
print("=" * 50)
sys.exit(0 if not issues else 1)
