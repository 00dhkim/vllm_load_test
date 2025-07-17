#!/bin/bash

export VLLM_HOST="http://localhost:18802"
export VLLM_MODEl="qwen3"
export VLLM_API_KEY="dummy"

# 단일 머신, 헤드리스 모드로 100유저/초당 20명씩 증가, 2분 동안 테스트
locust -f locustfile.py \
       --headless \
       -u 100 -r 20 \
       --run-time 2m \
       --csv run1
