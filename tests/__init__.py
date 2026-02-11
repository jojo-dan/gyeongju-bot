"""테스트 패키지 초기화 모듈."""

import sys
import os

# src/ 디렉토리를 모듈 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
