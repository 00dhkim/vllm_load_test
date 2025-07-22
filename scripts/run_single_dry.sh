#!/usr/bin/env bash
set -euo pipefail
EXP_ID=$1

echo "--- DRY RUN for experiment: ${EXP_ID} ---"
echo "VLLM_MODEL: $VLLM_MODEL"
echo "TENSOR_PARALLEL_SIZE: $TP"
echo "DATA_PARALLEL_SIZE: $DP"
echo "MAX_NUM_BATCHED_TOKENS: $MBT"
echo "MAX_NUM_SEQS: $BATCH_SIZE"
echo "USERS: $USERS"
echo "SPAWN: $SPAWN"
echo "RUN_TIME: $RUN_TIME"
echo "PROMPTS_FILE: $PROMPTS_FILE"
echo "MAX_TOKENS: $MAX_TOKENS"
