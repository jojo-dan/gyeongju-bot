"""pytest 설정: src/ 디렉토리를 모듈 경로에 추가."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
