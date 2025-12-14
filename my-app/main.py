from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import asyncio
from test import run_aider_with_custom_llm

app = FastAPI(title="Voice AI Hackathon")

NEXTJS_PROJECT_PATH = "/workspace/nextjs-app"
dev_server_process = None

@app.get("/")
async def root():
    return {
        "status": "Agent running", 
        "nextjs_exists": os.path.exists(NEXTJS_PROJECT_PATH),
        "nextjs_path": NEXTJS_PROJECT_PATH
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global dev_server_process
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "start-dev-server":
                if not os.path.exists(NEXTJS_PROJECT_PATH):
                    await websocket.send_json({
                        "status": "error", 
                        "message": "Next.js app not found"
                    })
                    continue
                
                if dev_server_process is None or dev_server_process.returncode is not None:
                    await websocket.send_json({"status": "starting"})
                    
                    dev_server_process = await asyncio.create_subprocess_exec(
                        "npm", "run", "dev", "--", "--hostname", "0.0.0.0",
                        cwd=NEXTJS_PROJECT_PATH,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    # Attendre que le serveur soit prêt
                    async def wait_for_ready():
                        try:
                            async for line in dev_server_process.stdout:
                                line_str = line.decode().strip()
                                print(f"Next.js: {line_str}")
                                
                                await websocket.send_json({
                                    "status": "starting",
                                    "log": line_str
                                })
                                
                                if "local:" in line_str.lower() or "ready" in line_str.lower():
                                    await websocket.send_json({
                                        "status": "running",
                                        "url": "http://localhost:3000",
                                        "pid": dev_server_process.pid
                                    })
                                    break
                        except Exception as e:
                            print(f"Error reading output: {e}")
                    
                    asyncio.create_task(wait_for_ready())
                else:
                    await websocket.send_json({"status": "already_running"})
            
            elif data.get("type") == "stop-dev-server":
                if dev_server_process and dev_server_process.returncode is None:
                    dev_server_process.terminate()
                    await dev_server_process.wait()
                    await websocket.send_json({"status": "stopped"})
                else:
                    await websocket.send_json({"status": "not_running"})
                    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
        except:
            pass

@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        await websocket.send_json({
            "status": "ready",
            "message": "🤖 AI Agent ready! Send me an instruction."
        })
        
        while True:
            data = await websocket.receive_json()
            instruction = data.get("instruction")
            
            if not instruction:
                await websocket.send_json({"status": "error", "message": "No instruction provided"})
                continue
            
            await websocket.send_json({
                "status": "thinking",
                "message": f"🤔 Processing with Mistral: {instruction}"
            })
            
            # --- CORRECTION ICI ---
            # 1. On attend (await) la fin de l'exécution
            # 2. On capture le résultat retourné par la fonction
            result = await run_aider_with_custom_llm(instruction, NEXTJS_PROJECT_PATH)
            
            # 3. On analyse le résultat
            if result["returncode"] == 0:
                # Succès : on renvoie le log standard (stdout) qui contient souvent les fichiers modifiés
                await websocket.send_json({
                    "status": "completed",
                    "message": "✅ Changes applied successfully!",
                    "details": result["stdout"] # Optionnel : afficher les logs aider
                })
            else:
                # Erreur : on renvoie stderr
                await websocket.send_json({
                    "status": "error",
                    "message": f"❌ Error executing aider",
                    "details": result["stderr"] or result["stdout"]
                })
  
    except WebSocketDisconnect:
        print("Agent client disconnected")
    except Exception as e:
        print(f"Agent error: {e}")
        # C'est mieux de vérifier si le socket est encore ouvert avant d'envoyer
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
        except:
            pass