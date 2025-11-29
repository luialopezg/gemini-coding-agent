import os
from google import genai
from dotenv import load_dotenv

# Importar la clase del agente
from agent import CodingAgent 

# --- Paso 1 (Continuación): Carga de la Clave Gemini ---
load_dotenv() 

try:
    # Si la clave GEMINI_API_KEY no está presente, esto lanzará un error
    # El cliente la busca automáticamente después de load_dotenv()
    client = genai.Client()
    print("✅ Cliente de Gemini inicializado con éxito.")
except Exception as e:
    print(f"❌ Error al inicializar el cliente de Gemini. Asegúrese de que GEMINI_API_KEY esté en su archivo .env.\nDeteniendo ejecución. Error: {e}")
    exit()

# Inicializar el Agente de Codificación
agent = CodingAgent(client)
print("🤖 Agente de Codificación (Gemini) listo. Escriba 'salir' para terminar la conversación.")
print("-" * 50)


# --- Pasos 4 y 5: Bucle Principal de Interacción ---

while True:
    # 1. Obtener la entrada del usuario
    # El agente está esperando la entrada del "Ambiente" (usted, en la terminal)
    user_input = input("👤 Usuario: ")
    
    if user_input.lower() in ('salir', 'exit', 'quit'):
        print("\n👋 Agente: ¡Adiós! No olvide desactivar su ambiente virtual con 'deactivate'.")
        break
    
    if not user_input.strip():
        continue
    
    # 2. Iniciar el proceso de razonamiento del agente
    # El método process_response contiene el bucle interno que maneja las llamadas a funciones
    agent.process_response(user_input)