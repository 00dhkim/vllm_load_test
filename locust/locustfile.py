import os, random, json, time
from locust import HttpUser, task, between, events

# --- 런타임 설정 로드 ---
PROMPTS = []
PROMPTS_FILE = os.getenv("PROMPTS_FILE")
if PROMPTS_FILE and os.path.exists(PROMPTS_FILE):
    with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
        PROMPTS = [l.strip() for l in f if l.strip()]
else:
    PROMPTS = [
        "서울의 오늘 날씨를 한 줄로 요약해 줘",
        "Explain quantum computing in simple terms.",
        "JSON 형식으로 하루 운동 루틴 만들어줘",
        "Write a haiku about sunrise.",
    ]

WAIT_MIN = float(os.getenv("WAIT_MIN", 0.05))
WAIT_MAX = float(os.getenv("WAIT_MAX", 0.2))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 128))
STREAM = os.getenv("STREAM", "0") == "1"  # streaming vs non-stream test

class VllmChatUser(HttpUser):
    host = os.getenv("VLLM_HOST", "http://localhost:8000")
    wait_time = between(WAIT_MIN, WAIT_MAX)

    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('VLLM_API_KEY', 'token-abc123')}"
        }
        self.prompts = PROMPTS
        self.model = os.getenv("VLLM_MODEL", "NousResearch/Meta-Llama-3-8B-Instruct")

    @task
    def chat_completion(self):
        prompt = random.choice(self.prompts)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "/no_think"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0.7,
            "stream": STREAM
        }
        start = time.time()
        with self.client.post(
            "/v1/chat/completions",
            headers=self.headers,
            json=payload,
            name="/v1/chat/completions",
            timeout=int(os.getenv("REQUEST_TIMEOUT", 120)),
            catch_response=True
        ) as res:
            elapsed = time.time() - start
            if res.status_code != 200:
                res.failure(f"{res.status_code} {res.text[:120]}")
            else:
                try:
                    j = res.json()
                    # 간단한 토큰 길이 추정 (후속 정확 계산은 서버 로그)
                    out = j.get("choices", [{}])[0].get("message", {}).get("content", "")
                    output_tokens = len(out.split())
                    res.success()
                    events.request.fire(
                        request_type="CHAT_EXTRA",
                        name="tokens",
                        response_time=int(elapsed*1000),
                        response_length=output_tokens,
                        exception=None,
                        context={"prompt_len": len(prompt), "out_tokens": output_tokens}
                    )
                except Exception as e:
                    res.failure(f"parse error {e}")