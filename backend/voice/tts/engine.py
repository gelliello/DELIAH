from abc import ABC, abstractmethod
from typing import Optional
import httpx


class TextToSpeech(ABC):
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        pass

    @abstractmethod
    async def speak(self, text: str):
        pass


class ElevenLabsTTS(TextToSpeech):
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = "eleven_monolingual_v1",
    ):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        self.voice_id = voice_id
        self.model_id = model_id
        self.base_url = "https://api.elevenlabs.io/v1"

    async def synthesize(self, text: str) -> bytes:
        if not self.api_key:
            return b""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/text-to-speech/{self.voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={"text": text, "model_id": self.model_id},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.content

    async def speak(self, text: str):
        audio = await self.synthesize(text)
        if audio:
            await self._play_audio(audio)

    async def _play_audio(self, audio_data: bytes):
        pass


class PiperTTS(TextToSpeech):
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path

    async def synthesize(self, text: str) -> bytes:
        return b""

    async def speak(self, text: str):
        pass


class TTSFactory:
    @staticmethod
    def create(engine: str = "elevenlabs", **kwargs) -> TextToSpeech:
        engines = {
            "elevenlabs": ElevenLabsTTS,
            "piper": PiperTTS,
        }
        cls = engines.get(engine)
        if cls is None:
            raise ValueError(f"Unknown TTS engine: {engine}")
        return cls(**kwargs)
