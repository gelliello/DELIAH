import asyncio
from typing import Optional, Callable
from .stt.engine import SpeechToText, STTFactory
from .tts.engine import TextToSpeech, TTSFactory
from .wake_word.detector import WakeWordDetector, WakeWordFactory


class VoicePipeline:
    def __init__(
        self,
        stt_engine: str = "whisper",
        tts_engine: str = "elevenlabs",
        wake_word_engine: str = "openwakeword",
    ):
        self.stt: SpeechToText = STTFactory.create(stt_engine)
        self.tts: TextToSpeech = TTSFactory.create(tts_engine)
        self.wake_word: WakeWordDetector = WakeWordFactory.create(wake_word_engine)
        self._processing = False

    async def process_audio(
        self,
        audio_data: bytes,
        processor: Callable[[str], str],
    ) -> str:
        text = await self.stt.transcribe(audio_data)
        if not text:
            return ""

        response = await self._run_processor(text, processor)
        if response:
            await self.tts.speak(response)
        return response

    async def _run_processor(
        self, text: str, processor: Callable[[str], str]
    ) -> str:
        if asyncio.iscoroutinefunction(processor):
            return await processor(text)
        return processor(text)

    async def start_conversation_loop(
        self,
        processor: Callable[[str], str],
        on_wake: Optional[Callable] = None,
    ):
        async def wake_callback():
            if on_wake:
                await on_wake()
            self._processing = True

        await self.wake_word.start(wake_callback)

    async def stop(self):
        self._processing = False
        await self.wake_word.stop()
        await self.stt.stop_listening()

    def is_active(self) -> bool:
        return self._processing
