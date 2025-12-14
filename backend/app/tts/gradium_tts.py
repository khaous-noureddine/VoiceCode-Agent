"""
Gradium TTS helper.

- Input: payload {"text": "..."}
- Output: audio played live (no file saved)

Designed to be blocking on purpose:
STT must be muted while TTS is playing.
"""

import os
import io
import soundfile as sf
import sounddevice as sd
from gradium import client as gradium_client


class GradiumTTS:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://eu.api.gradium.ai/api",
        model_name: str = "default",
        voice_id: str = "YTpq7expH9539ERJ",
    ):
        """
        api_key: Gradium API key (or GRADIUM_API_KEY env var)
        model_name: TTS model
        voice_id: voice identifier
        """

        self.client = gradium_client.GradiumClient(
            base_url=base_url,
            api_key=api_key or os.getenv("GRADIUM_API_KEY"),
        )

        self.setup = {
            "model_name": model_name,
            "voice_id": voice_id,
            "output_format": "wav",
        }

    # =====================
    # MAIN ENTRY POINT
    # =====================
    async def run(self, payload: dict):
        """
        payload must contain:
        {
            "text": "string"
        }
        """

        text = payload.get("text", "").strip()
        if not text:
            return

        # ---- Call Gradium TTS ----
        result = await self.client.tts(
            setup=self.setup,
            text=text,
        )

        # ---- Decode WAV from memory ----
        audio, sr = sf.read(
            io.BytesIO(result.raw_data),
            dtype="float32",
        )

        # ---- Play audio (blocking) ----
        sd.play(audio, sr)
        sd.wait()  # blocking ON PURPOSE
