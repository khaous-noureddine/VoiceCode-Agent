"""
Gradium TTS helper.

- Input: JSON payload (expects payload["text"])
- Output: audio played live (no file)
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
    async def run(self, payload):
        result = await self.client.tts(
            setup=self.setup,
            text=payload["text"],
        )

        audio, sr = sf.read(
            io.BytesIO(result.raw_data),
            dtype="float32",
        )

        sd.play(audio, sr)
        sd.wait()
