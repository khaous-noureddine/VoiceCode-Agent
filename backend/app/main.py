import asyncio
import os
from dotenv import load_dotenv

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


# =====================
# MAIN
# =====================
async def main():
    # --- LLM + AGENT 1 (planner) ---
    llm = LLMClient()
    agent = AnalysisAgent(llm)

    # --- callback STT ---
    async def on_event(event_type, payload):
        if event_type != "speech_end":
            return

        user_text = payload.get("text", "").strip()
        if len(user_text) < 4:
            return

        print("\n🧠 USER:", user_text)

        try:
            # --------
            # AGENT 1
            # --------
            result = await agent.handle(user_text)

            # result = {
            #   execute: bool,
            #   instruction: str | None,
            #   reply: str
            # }

            # --------
            # RÉPONSE UTILISATEUR (à dire / TTS plus tard)
            # --------
            reply = result["reply"]
            if reply:
                print("🤖 ASSISTANT:", reply)

            # --------
            # AGENT 2 (EXECUTION)
            # --------
            if result["execute"]:
                instruction = result["instruction"]

                print("⚙️ EXECUTOR INSTRUCTION:")
                print(instruction)

                execution_result = execute_code(instruction)

                print("🧠 EXECUTION RESULT:")
                print(execution_result)

        except Exception as e:
            print("❌ ERROR:", e)

    # --- STT ---
    transcriber = GradiumStreamTranscriber(
        api_key=GRADIUM_API_KEY,
        language="fr",
    )

    print("🚀 Assistant vocal prêt")
    print("🎤 Parle dans le micro (Ctrl+C pour arrêter)")

    await transcriber.run(audio_generator(), on_event)


# =====================
# ENTRYPOINT
# =====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt utilisateur")