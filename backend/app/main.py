import sys
import asyncio
import os
from dotenv import load_dotenv

# =====================
# WINDOWS FIX (IMPORTANT)
# =====================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# =====================
# ENV
# =====================
load_dotenv()

GRADIUM_API_KEY = os.getenv("GRADIUM_API_KEY")
if not GRADIUM_API_KEY:
    raise RuntimeError("❌ GRADIUM_API_KEY manquante")

# =====================
# IMPORTS
# =====================
from stt.gradium_stt import GradiumStreamTranscriber
from stt.audio_generator import audio_generator

from llm.llm_client import LLMClient
from agent.analysis_agent import AnalysisAgent

from tools.execute_code import execute_code
from tts.gradium_tts import GradiumTTS


# =====================
# MAIN
# =====================
async def main():
    # --- STATE ---
    is_tts_playing = False

    # --- LLM + AGENT ---
    llm = LLMClient()
    agent = AnalysisAgent(llm)

    # --- TTS ---
    tts = GradiumTTS(api_key=GRADIUM_API_KEY)

    # -----------------
    # STT CALLBACK
    # -----------------
    async def on_event(event_type, payload):
        nonlocal is_tts_playing

        # 🚫 ignore STT while TTS is speaking
        if is_tts_playing:
            return

        if event_type != "speech_end":
            return

        user_text = payload.get("text", "").strip()
        if len(user_text) < 4:
            return

        print("\n🧠 USER:", user_text)

        try:
            # --------
            # AGENT 1 (PLANNER)
            # --------
            result = await agent.handle(user_text)

            reply = result["reply"]
            execute = result["execute"]
            instruction = result["instruction"]

            # --------
            # TTS (VOICE OUTPUT)
            # --------
            if reply:
                print("🤖 ASSISTANT:", reply)
                is_tts_playing = True
                await tts.run({"text": reply})
                is_tts_playing = False

            # --------
            # AGENT 2 (EXECUTION)
            # --------
            if execute and instruction:
                print("⚙️ EXECUTOR INSTRUCTION:")
                print(instruction)

                execution_result = execute_code(instruction)
                print("🧠 EXECUTION RESULT:")
                print(execution_result)

        except Exception as e:
            print("❌ ERROR:", e)

    # -----------------
    # STT START
    # -----------------
    transcriber = GradiumStreamTranscriber(
        api_key=GRADIUM_API_KEY,
        language="fr",
    )

    print("🚀 Assistant vocal prêt")
    print("🎤 Parle dans le micro (Ctrl+C pour arrêter)")

    try:
        await transcriber.run(audio_generator(), on_event)
    except ConnectionResetError:
        print("⚠️ Connexion STT réinitialisée (Windows)")
    except KeyboardInterrupt:
        print("\n🛑 Arrêt utilisateur")


# =====================
# ENTRYPOINT
# =====================
if __name__ == "__main__":
    asyncio.run(main())
