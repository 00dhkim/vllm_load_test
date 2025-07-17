#!/bin/bash

export VLLM_HOST="http://localhost:18802"
export VLLM_MODEL="qwen3"
export VLLM_API_KEY="dummy"


uv run locust -f locustfile.py \
       -u 100 -r 20 \
       --run-time 2m \
       --csv run2

# uv run locust -f locustfile.py \
#        --headless \
#        -u 100 -r 20 \
#        --run-time 2m \
#        --csv run1