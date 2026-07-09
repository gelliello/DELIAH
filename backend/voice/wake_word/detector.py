import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Callable


class WakeWordDetector(ABC):
    @abstractmethod
    async def start(self, callback: Callable):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    def is_listening(self) -> bool:
        pass


class OpenWakeWordDetector(WakeWordDetector):
    def __init__(self, wake_words: Optional[list[str]] = None):
        self.wake_words = wake_words or ["hey deliah"]
        self._listening = False
        self._callback: Optional[Callable] = None

    async def start(self, callback: Callable):
        self._callback = callback
        self._listening = True

    async def stop(self):
        self._listening = False
        self._callback = None

    def is_listening(self) -> bool:
        return self._listening


class PorcupineDetector(WakeWordDetector):
    def __init__(self, access_key: Optional[str] = None):
        self.access_key = access_key
        self._listening = False
        self._callback: Optional[Callable] = None

    async def start(self, callback: Callable):
        self._callback = callback
        self._listening = True

    async def stop(self):
        self._listening = False

    def is_listening(self) -> bool:
        return self._listening


class WakeWordFactory:
    @staticmethod
    def create(engine: str = "openwakeword", **kwargs) -> WakeWordDetector:
        engines = {
            "openwakeword": OpenWakeWordDetector,
            "porcupine": PorcupineDetector,
        }
        cls = engines.get(engine)
        if cls is None:
            raise ValueError(f"Unknown wake word engine: {engine}")
        return cls(**kwargs)
