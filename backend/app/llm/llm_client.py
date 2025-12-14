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