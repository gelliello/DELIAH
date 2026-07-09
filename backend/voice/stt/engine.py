import os
from abc import ABC, abstractmethod


class SpeechToText(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        pass

    @abstractmethod
    async def start_listening(self):
        pass

    @abstractmethod
    async def stop_listening(self):
        pass


class WhisperSTT(SpeechToText):
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None

    async def transcribe(self, audio_data: bytes) -> str:
        try:
            import whisper
            if self.model is None:
                self.model = whisper.load_model(self.model_size)
            result = self.model.transcribe(audio_data)
            return result["text"]
        except ImportError:
            return "[Whisper not installed]"

    async def start_listening(self):
        pass

    async def stop_listening(self):
        pass


class STTFactory:
    @staticmethod
    def create(engine: str = "whisper", **kwargs) -> SpeechToText:
        engines = {
            "whisper": WhisperSTT,
        }
        cls = engines.get(engine)
        if cls is None:
            raise ValueError(f"Unknown STT engine: {engine}")
        return cls(**kwargs)
