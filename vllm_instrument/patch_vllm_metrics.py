"""런타임 시작 전에 PYTHONPATH 앞에 두고, VLLM_PATCH=1 설정 시 import hook으로
prefill/decode 단계 시간 & 토큰 수를 JSONL로 기록.

사용: VLLM_PATCH=1 python -m vllm.entrypoints.api_server ...
"""
import os, time, json, atexit, threading
from pathlib import Path

LOG_PATH = Path(os.getenv("VLLM_METRIC_LOG", "vllm_metrics.jsonl"))
lock = threading.Lock()

def log_event(ev):
    with lock:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

# Monkey patch 예시 (실제 vLLM 내부 구조에 따라 조정 필요)
try:
    import vllm.sequence as seq_mod
    _orig_prefill = seq_mod.Sequence.prefill
    _orig_decode = seq_mod.Sequence.decode

    def wrapped_prefill(self, *args, **kwargs):
        t0 = time.time()
        r = _orig_prefill(self, *args, **kwargs)
        dt = time.time() - t0
        log_event({"phase": "prefill", "seq_id": self.id, "tokens": len(self.prompt_token_ids), "time": dt, "ts": t0})
        return r

    def wrapped_decode(self, *args, **kwargs):
        t0 = time.time()
        r = _orig_decode(self, *args, **kwargs)
        dt = time.time() - t0
        # 한 step 당 1토큰 가정; r 반환 형태에 따라 수정
        log_event({"phase": "decode", "seq_id": self.id, "tokens": 1, "time": dt, "ts": t0})
        return r

    seq_mod.Sequence.prefill = wrapped_prefill
    seq_mod.Sequence.decode = wrapped_decode
except Exception as e:
    log_event({"phase": "patch_error", "error": str(e)})

@atexit.register
def _done():
    log_event({"phase": "exit"})
