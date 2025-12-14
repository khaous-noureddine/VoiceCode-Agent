"""
Gradium streaming transcription helper.

- Input: async generator yielding PCM int16 chunks (24kHz, mono)
- Output events:
    - speech_start
    - partial_text
    - speech_end (with final text)
"""

from gradium import client as gradium_client


# =====================
# VAD CONFIG
# =====================
STEP_DURATION = 0.08
INACTIVITY_THRESHOLD = 0.6
INACTIVITY_DURATION = 0.8


class GradiumStreamTranscriber:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://eu.api.gradium.ai/api",
        model_name: str = "default",
        language: str | None = None,
        temp: float | None = None,
    ):
        self.client = gradium_client.GradiumClient(
            base_url=base_url,
            api_key=api_key,
        )

        self.setup = {
            "model_name": model_name,
            "input_format": "pcm",
        }

        json_config = {}
        if language is not None:
            json_config["language"] = language
        if temp is not None:
            json_config["temp"] = temp
        if json_config:
            self.setup["json_config"] = json_config

        # VAD state
        self.is_speaking = False
        self.silence_time = 0.0

        # Text state
        self.tokens: list[str] = []
        self.current_text = ""

    # =====================
    # MAIN ENTRY POINT
    # =====================
    async def run(self, audio_generator, on_event):
        stream = await self.client.stt_stream(self.setup, audio_generator)

        async for msg in stream._stream:
            msg_type = msg.get("type")

            # -------- TEXT --------
            if msg_type == "text":
                text = msg.get("text", "").strip()
                if text:
                    if not self.tokens or self.tokens[-1] != text:
                        self.tokens.append(text)

                    self.current_text = " ".join(self.tokens)
                    await on_event(
                        "partial_text",
                        {"text": self.current_text},
                    )

            # -------- VAD --------
            elif msg_type == "step":
                inactivity_prob = msg["vad"][2]["inactivity_prob"]
                await self._handle_vad(inactivity_prob, on_event)

    # =====================
    # VAD LOGIC
    # =====================
    async def _handle_vad(self, inactivity_prob, on_event):
        # --- Speaking ---
        if inactivity_prob < 0.5:
            if not self.is_speaking:
                self.is_speaking = True
                self.silence_time = 0.0
                await on_event("speech_start", {})
            else:
                self.silence_time = 0.0
            return

        # --- Silence ---
        self.silence_time += STEP_DURATION

        if (
            self.is_speaking
            and inactivity_prob > INACTIVITY_THRESHOLD
            and self.silence_time >= INACTIVITY_DURATION
        ):
            final_text = self.current_text.strip()

            # RESET STATE *AFTER* USING TEXT
            self.is_speaking = False
            self.silence_time = 0.0
            self.tokens = []
            self.current_text = ""

            if not final_text:
                return

            await on_event(
                "speech_end",
                {"text": final_text},
            )