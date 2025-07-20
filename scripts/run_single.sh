#!/usr/bin/env bash
set -euo pipefail
EXP_ID=$1
OUT_DIR="results/raw/${EXP_ID}"
mkdir -p "$OUT_DIR/locust" "$OUT_DIR/vllm" "$OUT_DIR/gpu"

# 1) vLLM 서버 (이미 외부 실행 중이라고 가정)
echo "Assuming vLLM server is already running at ${VLLM_HOST}"
echo "Experiment ID: ${EXP_ID}"

# 2) GPU 모니터링
nvidia-smi dmon -s u -d 1 -o DT -f "$OUT_DIR/gpu/dmon.csv" &
DMON_PID=$!

# 3) Locust 실행
uv run locust -f locust/locustfile.py \
  --headless -u $USERS -r $SPAWN --run-time $RUN_TIME \
  --csv $OUT_DIR/locust/locust --csv-full-history

# 4) 종료/정리
kill $DMON_PID || true
echo "Cleaned up processes for ${EXP_ID}."