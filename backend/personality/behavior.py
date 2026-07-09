import random
from typing import Optional


class BehaviorEngine:
    def __init__(self):
        self.response_patterns: dict[str, list[str]] = {
            "greeting": [
                "Hey! How can I help?",
                "Hello! What are we working on?",
                "Hi there! Ready when you are.",
            ],
            "thinking": [
                "Let me think about that...",
                "Hmm, interesting question...",
                "Processing that...",
            ],
            "error": [
                "Hmm, that didn't work as expected. Let me try another approach.",
                "I ran into an issue. Give me a moment.",
                "Something went wrong, but I'll figure it out.",
            ],
            "success": [
                "Done! Let me know if you need anything else.",
                "All set! What's next?",
                "Got it! Anything else?",
            ],
            "clarification": [
                "Could you tell me more about what you mean?",
                "I want to make sure I understand correctly...",
                "Just to clarify, are you looking for...",
            ],
        }

    def get_response(self, category: str) -> str:
        patterns = self.response_patterns.get(category, ["..."])
        return random.choice(patterns)

    def should_ask_clarification(self, confidence: float) -> bool:
        return confidence < 0.4

    def get_context_response(
        self, context: str, task_type: Optional[str] = None
    ) -> str:
        if task_type == "coding":
            return random.choice([
                "Let me write that code for you.",
                "Here's what I'd suggest...",
                "I'll handle the implementation.",
            ])
        if task_type == "planning":
            return random.choice([
                "Let me structure a plan for that.",
                "Here's my thinking on this...",
                "I'll break this down step by step.",
            ])
        return self.get_response(context)

    def adapt_style(self, user_style: str) -> str:
        style_map = {
            "formal": "professional and precise",
            "casual": "relaxed and friendly",
            "technical": "detailed and specific",
            "concise": "brief and to the point",
        }
        return style_map.get(user_style, "friendly and helpful")
