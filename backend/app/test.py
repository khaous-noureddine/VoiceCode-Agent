import asyncio
import numpy as np
import sounddevice as sd

from gradium_stt import GradiumStreamTranscriber

# =====================
# CONFIG
# =====================
API_KEY = "gsk_6d8ce7bdf0d9f20f12b1a30e7081a63a18e81d021300265d104162c75a659089"
SAMPLE_RATE = 24000
CHANNELS = 1
CHUNK_DURATION = 0.02  # 20 ms
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)


async def main():
    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()

    # ---------------------
    # Audio callback (micro)
    # ---------------------
    def audio_callback(indata, frames, time, status):
        if status:
            print("⚠️", status)

        pcm16 = (indata[:, 0] * 32767).astype(np.int16)
        loop.call_soon_threadsafe(audio_queue.put_nowait, pcm16)

    # ---------------------
    # Audio generator
    # ---------------------
    async def audio_generator():
        while True:
            chunk = await audio_queue.get()
            yield chunk

    # ---------------------
    # Event handler
    # ---------------------
    async def on_event(event_type, payload):
        print(f"[{event_type}] {payload}")

    # ---------------------
    # Start microphone
    # ---------------------
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=CHUNK_SIZE,
        callback=audio_callback,
    ):
        print("🎤 Micro ouvert — parle maintenant (Ctrl+C pour arrêter)")

        transcriber = GradiumStreamTranscriber(api_key=API_KEY)
        await transcriber.run(audio_generator(), on_event)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du test micro")