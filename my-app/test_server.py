import asyncio
import websockets
import json
import sys

async def test():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri, ping_timeout=120) as websocket:
        
        # Lancer le serveur dev
        print("🚀 Starting dev server...")
        await websocket.send(json.dumps({
            "type": "start-dev-server"
        }))
        
        # Attendre que le serveur soit prêt
        server_running = False
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("status") == "starting":
                log = data.get("log", "")
                if log:
                    print(f"  📝 {log}")
            elif data.get("status") == "running":
                print(f"\n✅ Dev server running!")
                print(f"🌐 Open {data.get('url')} in your browser!")
                server_running = True
                break
            elif data.get("status") == "error":
                print(f"  ❌ Error: {data.get('message')}")
                return
        
        if server_running:
            print("\n👉 Type 'STOP' and press Enter to stop the server")
            print("   Or press Ctrl+C to exit\n")
            
            # Créer une tâche pour lire les messages du serveur
            async def read_messages():
                try:
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        if data.get("status") == "stopped":
                            print("\n🛑 Dev server stopped!")
                            return
                        elif data.get("status"):
                            print(f"📩 Server: {data}")
                except:
                    pass
            
            # Créer une tâche pour lire l'input utilisateur
            async def read_input():
                loop = asyncio.get_event_loop()
                while True:
                    # Lire stdin de manière non-bloquante
                    user_input = await loop.run_in_executor(None, sys.stdin.readline)
                    if user_input.strip().upper() == "STOP":
                        print("\n⏳ Stopping dev server...")
                        await websocket.send(json.dumps({
                            "type": "stop-dev-server"
                        }))
                        return
            
            # Exécuter les deux tâches en parallèle
            try:
                await asyncio.gather(
                    read_messages(),
                    read_input()
                )
            except KeyboardInterrupt:
                print("\n\n👋 Exiting without stopping the server...")

asyncio.run(test())