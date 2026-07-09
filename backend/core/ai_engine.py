import httpx
import json
from typing import Optional
from .model_router import ModelRouter, TaskType


class AIEngine:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.router = ModelRouter()
        self.conversation_history: list[dict] = []
        self.system_prompt: str = ""

    async def process_message(
        self,
        message: str,
        task_type: Optional[TaskType] = None,
        personality_prompt: str = "",
    ) -> str:
        if task_type is None:
            task_type = self.router.classify_task(message)

        model = self.router.get_model(task_type)
        system = self._build_system_prompt(personality_prompt, task_type)

        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}]
            + self.conversation_history
            + [{"role": "user", "content": message}],
            "stream": False,
        }

        self.conversation_history.append({"role": "user", "content": message})

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/chat", json=payload
            )
            response.raise_for_status()
            data = response.json()

        reply = data["message"]["content"]
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    async def stream_message(
        self,
        message: str,
        task_type: Optional[TaskType] = None,
        personality_prompt: str = "",
    ):
        if task_type is None:
            task_type = self.router.classify_task(message)

        model = self.router.get_model(task_type)
        system = self._build_system_prompt(personality_prompt, task_type)

        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}]
            + self.conversation_history
            + [{"role": "user", "content": message}],
            "stream": True,
        }

        self.conversation_history.append({"role": "user", "content": message})
        full_reply = ""

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST", f"{self.ollama_url}/api/chat", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        full_reply += chunk
                        yield chunk

        self.conversation_history.append(
            {"role": "assistant", "content": full_reply}
        )

    def _build_system_prompt(
        self, personality_prompt: str, task_type: TaskType
    ) -> str:
        task_context = {
            TaskType.CODING: "You are an expert coding assistant. Focus on clean, efficient code.",
            TaskType.PLANNING: "You are a strategic planning assistant. Think step by step.",
            TaskType.GENERAL: "You are a friendly, knowledgeable assistant.",
        }
        base = task_context.get(task_type, task_context[TaskType.GENERAL])
        if personality_prompt:
            base = f"{personality_prompt}\n\n{base}"
        return base

    async def check_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def clear_history(self):
        self.conversation_history.clear()

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
