import time
from enum import Enum
from typing import Optional


class MoodState(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    FOCUSED = "focused"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    TIRED = "tired"
    EXCITED = "excited"


class MoodEngine:
    def __init__(self):
        self.current_mood = MoodState.NEUTRAL
        self.mood_history: list[tuple[MoodState, float]] = []
        self.mood_decay_rate = 0.01
        self.last_interaction = time.time()

    def detect_mood_from_input(self, text: str) -> MoodState:
        text_lower = text.lower()

        excited_words = ["amazing", "awesome", "wow", "great", "fantastic", "love"]
        serious_words = ["serious", "important", "critical", "urgent", "problem"]
        playful_words = ["fun", "joke", "funny", "lol", "haha", "play"]
        sad_words = ["sad", "bad", "terrible", "hate", "worst", "angry"]

        excited_score = sum(1 for w in excited_words if w in text_lower)
        serious_score = sum(1 for w in serious_words if w in text_lower)
        playful_score = sum(1 for w in playful_words if w in text_lower)
        sad_score = sum(1 for w in sad_words if w in text_lower)

        scores = {
            MoodState.EXCITED: excited_score,
            MoodState.SERIOUS: serious_score,
            MoodState.PLAYFUL: playful_score,
        }

        if sad_score > 0:
            return MoodState.NEUTRAL

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return MoodState.NEUTRAL

    def update_mood(self, text: str):
        detected = self.detect_mood_from_input(text)
        if detected != self.current_mood:
            self.mood_history.append((self.current_mood, time.time()))
            self.current_mood = detected
        self.last_interaction = time.time()

    def get_mood(self) -> MoodState:
        elapsed = time.time() - self.last_interaction
        if elapsed > 300:
            self.current_mood = MoodState.NEUTRAL
        return self.current_mood

    def get_mood_response(self) -> str:
        mood_responses = {
            MoodState.NEUTRAL: "I'm here and ready to help.",
            MoodState.HAPPY: "I'm feeling great! Let's do this.",
            MoodState.FOCUSED: "I'm focused. Let me think about that.",
            MoodState.PLAYFUL: "Oh, this sounds fun!",
            MoodState.SERIOUS: "Understood. Let me handle this carefully.",
            MoodState.EXCITED: "This is exciting! I'm on it!",
            MoodState.TIRED: "I'm here, just running a bit slower than usual.",
        }
        return mood_responses.get(self.get_mood(), "I'm here.")

    def get_mood_info(self) -> dict:
        return {
            "current": self.current_mood.value,
            "history": [
                {"mood": m.value, "timestamp": t}
                for m, t in self.mood_history[-10:]
            ],
        }
