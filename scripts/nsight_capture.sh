#!/usr/bin/env bash
# 짧은 20초 구간 캡처
nsys profile -t cuda,nvtx -o results/raw/$1/nsight/trace \
  --force-overwrite=true --capture-range=none --sample=none \
  sleep 20

