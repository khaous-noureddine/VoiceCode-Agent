import os
from openai import AsyncOpenAI


class LLMClient:
    def __init__(self):
        base_url = os.getenv("LLM_BASE_URL")
        if not base_url:
            raise RuntimeError("❌ LLM_BASE_URL manquante")

        # Clé optionnelle (vLLM accepte souvent EMPTY)
        api_key = os.getenv("LLM_API_KEY", "EMPTY")

        # ⚠️ vLLM attend /v1
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url + "/v1",
        )

        # modèle par défaut (doit exister sur ton serveur vLLM)
        self.model = os.getenv(
            "LLM_MODEL",
            "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
        )

    async def chat(self, messages, temperature=0.7, max_tokens=512) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content.strip()


# import os
# import asyncio
# from openai import AsyncOpenAI

# async def main():
#     # Création du client OpenAI-compatible (vLLM / unmute)
#     client = AsyncOpenAI(
#         api_key=os.environ.get("LLM_API_KEY", "EMPTY"),
#         base_url=os.environ["LLM_BASE_URL"] + "/v1",
#     )

#     # Appel LLM simple
#     response = await client.chat.completions.create(
#         model="mistralai/Mistral-Small-3.2-24B-Instruct-2506",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Explain FastAPI in one paragraph."},
#         ],
#         temperature=0.7,
#         max_tokens=200,
#     )

#     print("LLM RESPONSE:")
#     print(response.choices[0].message.content)


# if __name__ == "__main__":
#     asyncio.run(main())