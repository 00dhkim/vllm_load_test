# locustfile.py
import os, random
from locust import HttpUser, task, between

class VllmChatUser(HttpUser):
    host      = os.getenv("VLLM_HOST", "http://localhost:8000")
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('VLLM_API_KEY', 'token-abc123')}"
        }

        self.prompts = [
            "서울의 오늘 날씨를 한 줄로 요약해 줘",
            "Explain quantum computing in simple terms.",
            "JSON 형식으로 하루 운동 루틴 만들어줘",
            "Write a haiku about sunrise.",
        ]
        self.model = os.getenv("VLLM_MODEL", "NousResearch/Meta-Llama-3-8B-Instruct")

    @task
    def chat_completion(self):
        prompt = random.choice(self.prompts)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 128,
            "temperature": 0.7
        }
        with self.client.post(
            "/v1/chat/completions",
            headers=self.headers,
            json=payload,
            name="/v1/chat/completions",
            timeout=120,
            catch_response=True
        ) as res:
            if res.status_code != 200:
                res.failure(f"{res.status_code} {res.text[:120]}")
            else:
                if "choices" not in res.json():
                    res.failure("invalid schema")
                else:
                    res.success()
