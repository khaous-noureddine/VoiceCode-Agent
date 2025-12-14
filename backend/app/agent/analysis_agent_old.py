# from tools.tools import TOOLS


# class AnalysisAgent:
#     def __init__(self, llm):
#         self.llm = llm

#     async def handle(self, text: str) -> str:
#         messages = [
#             {
#                 "role": "system",
#                 "content": (
#                     "Tu es un agent intelligent.\n"
#                     "Si la demande nécessite l'exécution de code Python, "
#                     "réponds STRICTEMENT sous la forme:\n\n"
#                     "TOOL: run_python\n"
#                     "CODE:\n"
#                     "<code>\n\n"
#                     "Sinon, réponds normalement.\n"
#                     "Ne fais JAMAIS autre chose."
#                 ),
#             },
#             {"role": "user", "content": text},
#         ]

#         response = await self.llm.chat(messages)

#         # --- TOOL PARSING ---
#         if response.startswith("TOOL:"):
#             return await self._handle_tool(response)

#         return response

#     async def _handle_tool(self, response: str) -> str:
#         lines = response.splitlines()
#         tool_name = lines[0].replace("TOOL:", "").strip()

#         if tool_name not in TOOLS:
#             return f"❌ Tool inconnu: {tool_name}"

#         code_index = response.find("CODE:")
#         if code_index == -1:
#             return "❌ CODE manquant"

#         code = response[code_index + 5 :].strip()

#         tool_fn = TOOLS[tool_name]
#         output = tool_fn(code)

#         return f"🧠 Résultat de l'exécution:\n{output}"




class AnalysisAgent:
    def __init__(self, llm):
        self.llm = llm

    async def handle(self, text: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant vocal intelligent. "
                    "Analyse la demande de l'utilisateur et réponds "
                    "de manière claire, concise et utile. "
                    "Réponds en français."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ]

        return await self.llm.chat(messages)
