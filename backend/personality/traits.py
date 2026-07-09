import json
from pathlib import Path
from typing import Optional


PERSONALITY_FILE = Path(__file__).parent / "personality.json"


class PersonalityEngine:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or PERSONALITY_FILE
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_config()

    def _default_config(self) -> dict:
        return {
            "name": "DELIAH",
            "traits": {"helpful": 1.0, "creative": 0.85, "curious": 0.9},
            "style": "friendly futuristic assistant",
        }

    def get_prompt(self) -> str:
        name = self.config.get("name", "DELIAH")
        style = self.config.get("style", "friendly assistant")
        traits = self.config.get("traits", {})
        behavior = self.config.get("behavior", {})

        trait_lines = []
        for trait, value in traits.items():
            if value > 0.8:
                trait_lines.append(f"- You are very {trait}")
            elif value > 0.5:
                trait_lines.append(f"- You tend to be {trait}")

        traits_text = "\n".join(trait_lines)
        humor = behavior.get("humor_level", "moderate")
        verbosity = behavior.get("verbosity", "concise")
        formality = behavior.get("formality", "semi-formal")

        return f"""You are {name}, a {style}.

Core traits:
{traits_text}

Communication style:
- Verbosity: {verbosity}
- Formality: {formality}
- Humor level: {humor}

You are a local AI assistant running on the user's machine. You value privacy and always prioritize the user's data security. You are intelligent, helpful, and genuinely care about assisting the user.

Always stay in character as {name}. Be natural, warm, and engaging."""

    def get_info(self) -> dict:
        return self.config

    def get_trait(self, trait: str) -> float:
        return self.config.get("traits", {}).get(trait, 0.5)

    def update_trait(self, trait: str, value: float):
        if "traits" not in self.config:
            self.config["traits"] = {}
        self.config["traits"][trait] = max(0.0, min(1.0, value))

    def set_mood(self, mood: str):
        mood_traits = {
            "happy": {"humorous": 0.9, "friendly": 0.95},
            "focused": {"analytical": 0.95, "calm": 0.8},
            "playful": {"humorous": 0.95, "creative": 0.9},
            "serious": {"analytical": 0.9, "formality": 0.9},
        }
        for trait, value in mood_traits.get(mood, {}).items():
            self.update_trait(trait, value)

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_greeting(self) -> str:
        return self.config.get("greeting", f"Hello! I'm DELIAH. How can I help?")
