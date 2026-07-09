import re
from enum import Enum
from typing import Optional


class TaskType(Enum):
    CODING = "coding"
    PLANNING = "planning"
    GENERAL = "general"


class ModelRouter:
    CODING_KEYWORDS = [
        "code", "code", "programm", "debug", "bug", "function",
        "class", "api", "database", "sql", "git", "deploy",
        "compile", "build", "refactor", "test", "unit test",
        "frontend", "backend", "algorithm", "variable", "loop",
        "python", "javascript", "typescript", "rust", "java", "c++",
        "html", "css", "react", "vue", "angular", "flask", "django",
        "minecraft mod", "plugin", "script", "syntax", "error",
    ]

    PLANNING_KEYWORDS = [
        "plan", "strateg", "architect", "design", "roadmap",
        "feature", "sprint", "milestone", "goal", "decision",
        "brainstorm", "ide", "concept", "workflow", "process",
        "project", "timeline", "budget", "resource", "priority",
        "analyze", "evaluation", "comparison", "pros", "cons",
    ]

    def __init__(self):
        self.model_map: dict[TaskType, str] = {
            TaskType.CODING: "deepseek-coder:6.7b",
            TaskType.PLANNING: "qwen2.5:7b",
            TaskType.GENERAL: "qwen2.5:7b",
        }
        self.override: Optional[TaskType] = None

    def classify_task(self, message: str) -> TaskType:
        if self.override:
            return self.override

        text = message.lower()
        coding_score = sum(
            1 for kw in self.CODING_KEYWORDS if kw in text
        )
        planning_score = sum(
            1 for kw in self.PLANNING_KEYWORDS if kw in text
        )

        if coding_score > planning_score and coding_score >= 2:
            return TaskType.CODING
        if planning_score > coding_score and planning_score >= 2:
            return TaskType.PLANNING
        if coding_score >= 1 and planning_score == 0:
            return TaskType.CODING
        return TaskType.GENERAL

    def get_model(self, task_type: TaskType) -> str:
        return self.model_map.get(task_type, self.model_map[TaskType.GENERAL])

    def set_model(self, task_type: TaskType, model: str):
        self.model_map[task_type] = model

    def set_override(self, task_type: Optional[TaskType]):
        self.override = task_type

    def get_all_models(self) -> dict[str, str]:
        return {t.value: m for t, m in self.model_map.items()}

    def detect_mode(self, message: str) -> TaskType:
        patterns = {
            TaskType.CODING: r"\[coding\]|\[code\]|/code|/coding",
            TaskType.PLANNING: r"\[plan\]|\[planning\]|/plan|/planning",
            TaskType.GENERAL: r"\[general\]|\[chat\]|/chat|/general",
        }
        text = message.lower()
        for task_type, pattern in patterns.items():
            if re.search(pattern, text):
                return task_type
        return self.classify_task(message)
