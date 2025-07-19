#!/usr/bin/env bash
set -euo pipefail
EXP_ID=$1
OUT_DIR="results/raw/${EXP_ID}"
mkdir -p "$OUT_DIR/locust" "$OUT_DIR/vllm" "$OUT_DIR/gpu"

# 1) vLLM 서버 실행
echo "Starting vLLM server for experiment ${EXP_ID}"
VLLM_METRIC_LOG="$OUT_DIR/vllm/vllm_metrics.jsonl" VLLM_PATCH=1 \
nohup python -m vllm.entrypoints.api_server \
    --model "$VLLM_MODEL" \
    --tensor-parallel-size "$TP" \
    --data-parallel-size "$DP" \
    --max-num-batched-tokens "$MBT" \
    --max-num-seqs "$BATCH_SIZE" \
    > "$OUT_DIR/vllm/server.log" 2>&1 &
SERVER_PID=$!

# 2) 서버 준비 상태 확인 (Health Check)
echo "Waiting for vLLM server to be ready..."
MAX_WAIT=180 # 최대 3분 대기
ELAPSED=0
while ! curl -s -f "${VLLM_HOST}/health"; do
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo "Server failed to start within ${MAX_WAIT} seconds."
        kill $SERVER_PID || true
        exit 1
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo "...waited ${ELAPSED}s"
done
echo "Server is ready!"

# 3) GPU 모니터링
nvidia-smi dmon -s u -d 1 -o DT -f "$OUT_DIR/gpu/dmon.csv" &
DMON_PID=$!

# 4) Locust 실행
uv run locust -f locust/locustfile.py \
  --headless -u $USERS -r $SPAWN --run-time $RUN_TIME \
  --csv $OUT_DIR/locust/locust --csv-full-history

# 5) 종료/정리
kill $DMON_PID || true
kill $SERVER_PID || true
echo "Cleaned up processes for ${EXP_ID}."