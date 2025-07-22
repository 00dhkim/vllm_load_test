#!/usr/bin/env bash
set -euo pipefail
EXP_ID=$1
OUT_DIR="results/raw/${EXP_ID}"
mkdir -p "$OUT_DIR/benchmark" "$OUT_DIR/gpu"

# Set an initial empty value for DMON_PID
DMON_PID=""
# Trap to ensure all cleanup is handled on exit, even if some commands fail.
# This saves server logs, stops the GPU monitor, shuts down containers, and removes the .env file.
trap 'echo "Cleaning up for experiment ${EXP_ID}..."; [ ! -z "$DMON_PID" ] && kill $DMON_PID || true; echo "Saving server logs..."; docker-compose logs > "$OUT_DIR/server.log" 2>&1; docker-compose down --remove-orphans; rm -f .env' EXIT

# 1) Create .env file for Docker Compose
echo "Creating .env file for experiment: ${EXP_ID}"
cat > .env <<EOF
# Docker-compose environment file for experiment ${EXP_ID}
VLLM_MODEL_PATH=${VLLM_MODEL_PATH}
VLLM_MODEL_NAME=${VLLM_MODEL}
TP=${TP}
DP=${DP}
VLLM_PORT=${VLLM_PORT:-18806}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-32768}
GPU_MEM_UTIL=${GPU_MEM_UTIL:-0.9}
CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-"1,2,3"}
EOF

# 2) Clean up any previous runs and start vLLM server
echo "Ensuring clean state and starting vLLM server..."
docker-compose down --remove-orphans
docker-compose up -d

# 3) Wait for the server to be ready
echo "Waiting for vLLM server to be ready at http://localhost:${VLLM_PORT:-18806}..."
MAX_WAIT=240
ELAPSED=0
while ! curl -s -f "http://localhost:${VLLM_PORT:-18806}/health"; do
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo "Server failed to start within ${MAX_WAIT} seconds."
        # The trap will handle log saving and cleanup
        exit 1
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo "...waited ${ELAPSED}s"
done
echo "Server is ready!"

# 4) Start GPU monitoring
nvidia-smi dmon -s u -d 1 -o DT -f "$OUT_DIR/gpu/dmon.csv" &
DMON_PID=$!

# 5) Run the benchmark
# Force remove and re-clone the specific version to ensure script compatibility
echo "Preparing vllm benchmark scripts..."
rm -rf vllm
git clone --depth 1 --branch v0.9.2 https://github.com/vllm-project/vllm.git

export PYTHONPATH=$(pwd)/vllm${PYTHONPATH:+:$PYTHONPATH}
python vllm/benchmarks/benchmark_serving.py \
    --backend openai-chat \
    --model "$VLLM_MODEL" \
    --tokenizer "$VLLM_MODEL_PATH" \
    --endpoint "/v1/chat/completions" \
    --host "localhost" \
    --port "${VLLM_PORT:-18806}" \
    --dataset-name custom \
    --dataset-path "$PROMPTS_FILE" \
    --request-rate "$REQUEST_RATE" \
    --num-prompts 1000 \
    --save-result \
    --result-dir "$OUT_DIR/benchmark"

# The EXIT trap will handle cleanup.
echo "Benchmark finished for ${EXP_ID}."