import os
import asyncio

async def run_aider_with_custom_llm(instruction: str, project_path: str):
    # 1. Config Env
    base_url = os.environ.get("LLM_BASE_URL", "http://localhost:8000")
    if not base_url.endswith("/v1"): base_url += "/v1"
    
    env_vars = os.environ.copy()
    env_vars["OPENAI_API_BASE"] = base_url
    env_vars["OPENAI_API_KEY"] = os.environ.get("LLM_API_KEY", "EMPTY")
    env_vars["AIDER_AUTO_COMMITS"] = "1"

    model_name = "openai/mistralai/Mistral-Small-3.2-24B-Instruct-2506"

    # 2. Lancement du processus
    process = await asyncio.create_subprocess_exec(
        "aider",
        "--yes",
        "--message", instruction,
        "--model", model_name,
        cwd=project_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env_vars
    )

    # 3. Attendre la fin et capturer la sortie
    stdout, stderr = await process.communicate()
    
    # 4. Retourner les données utiles
    return {
        "returncode": process.returncode,
        "stdout": stdout.decode() if stdout else "",
        "stderr": stderr.decode() if stderr else ""
    }