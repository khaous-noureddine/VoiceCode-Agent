import asyncio
import websockets
import json

# Liste des instructions séquentielles
INSTRUCTIONS = [
    # 1. Le Header (Base)
    "Commence par repartir de 0 sur la page enleve tout le code de Next.js. Crée un header pour une boulangerie artisanale nommée 'Le Fournil Doré'. Utilise un titre centré et une brève description.",
    
    # 2. Modification A (Le CTA)
    "Ajoute un bouton d'action (CTA) bien visible au centre sous la description qui dit 'Commander en Click & Collect'. Utilise une couleur dorée/orange pour qu'il ressorte bien sur le fond sombre.",
    
    # 3. Modification B (La structure)
    "Juste en dessous du header, ajoute une section 'Nos Spécialités' avec une grille de 3 cartes simples (Baguette Tradition, Croissant au Beurre, Tarte aux Fraises). Affiche juste le nom et un prix fictif pour chaque carte."
]

async def process_instruction(websocket, instruction, step_num):
    """Envoie une instruction et attend qu'elle soit terminée"""
    print(f"\n🔹 ÉTAPE {step_num}/3 : {instruction[:50]}...")
    print(f"📤 Envoi de l'instruction...")
    
    await websocket.send(json.dumps({
        "instruction": instruction
    }))
    
    # Boucle d'attente pour CETTE instruction spécifique
    while True:
        response = await websocket.recv()
        data = json.loads(response)
        
        status = data.get("status")
        message = data.get("message")
        details = data.get("details", "") # Si ton backend renvoie 'details' ou 'log'
        
        if status == "thinking":
            print(f"   🧠 {message}")
        elif status == "working":
            # Si tu as ajouté des logs de streaming
            pass 
        elif status == "completed":
            print(f"   ✅ {message}")
            if details:
                print(f"   📄 Logs: {details[:100]}...") # Affiche un extrait
            return True # On sort de la boucle pour passer à l'instruction suivante
        elif status == "error":
            print(f"   ❌ ERREUR : {message}")
            if details:
                print(f"   Details: {details}")
            return False

async def test_agent_iterative():
    uri = "ws://localhost:8000/ws/agent"
    
    print("🔌 Connecting to AI agent...")
    async with websockets.connect(uri, ping_timeout=600) as websocket: # Timeout augmenté car 3 tâches
        
        # 1. Message de bienvenue
        welcome = await websocket.recv()
        print(f"👋 {json.loads(welcome).get('message')}")
        
        # 2. Itération sur les instructions
        for i, instruction in enumerate(INSTRUCTIONS, 1):
            success = await process_instruction(websocket, instruction, i)
            
            if not success:
                print("\n⛔ Arrêt du test suite à une erreur.")
                break
            
            # Petite pause pour laisser le temps de respirer (optionnel)
            print("   (Pause de 2s avant la suite...)")
            await asyncio.sleep(2)

        print("\n🎉 Test complet terminé ! Vérifie ton localhost:3000")

if __name__ == "__main__":
    asyncio.run(test_agent_iterative())