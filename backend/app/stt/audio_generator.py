import asyncio
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 24000
CHANNELS = 1
CHUNK_SIZE = 1920  # 80 ms, recommandé par Gradium


async def audio_generator():
    """
    Async generator yielding PCM int16 chunks from the microphone.
    """
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()

    def callback(indata, frames, time, status):
        if status:
            print("⚠️", status)

        pcm16 = (indata[:, 0] * 32767).astype(np.int16)
        loop.call_soon_threadsafe(queue.put_nowait, pcm16)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=CHUNK_SIZE,
        callback=callback,
    ):
        print("🎤 Micro ouvert — parle maintenant (Ctrl+C pour arrêter)")
        while True:
            chunk = await queue.get()
            yield chunk
