import asyncio
import numpy as np
import sounddevice as sd

from main import run_stt   # 👈 IMPORTANT

# =====================
# CONFIG
# =====================
SAMPLE_RATE = 24000
CHANNELS = 1
CHUNK_DURATION = 0.08  # 80 ms (plus stable)
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)


async def main():
    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print("⚠️", status)

        pcm16 = (indata[:, 0] * 32767).astype(np.int16)
        loop.call_soon_threadsafe(audio_queue.put_nowait, pcm16)

    async def audio_generator():
        while True:
            chunk = await audio_queue.get()
            yield chunk

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=CHUNK_SIZE,
        callback=audio_callback,
    ):
        print("🎤 Micro ouvert — parle maintenant (Ctrl+C pour arrêter)")
        await run_stt(audio_generator())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du test micro")
