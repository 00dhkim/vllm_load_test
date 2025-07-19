#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["locust>=2.23"]
# ///

import sys
from locust.main import main

DEFAULT_ARGS = ["-f", "locustfile.py",
                "--headless", "-u", "100", "-r", "20", "--run-time", "2m"]

if __name__ == "__main__":
    if len(sys.argv) == 1:          # 인수가 없으면 기본값 사용
        sys.argv += DEFAULT_ARGS
    elif "-f" not in sys.argv and "--locustfile" not in sys.argv:
        # 사용자가 locustfile 위치를 지정하지 않은 경우 자동 추가
        sys.argv += ["-f", "locustfile.py"]
    main()
