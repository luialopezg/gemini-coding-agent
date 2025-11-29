import json
import os
from google import genai
from google.genai import types

class CodingAgent:
    """
    Agente de Codificación capaz de interactuar con el sistema de archivos.
    Utiliza el modelo Gemini para razonamiento y Function Calling.
    """
    def __init__(self, client: genai.Client):
        self.client = client
        
        # 1. Instrucción del Sistema (System Instruction)
        self.system_instruction = (
            "Eres un experto asistente de codificación que opera en un sistema Linux Mint. "
            "Tu tarea es ayudar al usuario a gestionar, leer y editar archivos. "
            "DEBES usar tus herramientas (list_files_in_dir, read_file, edit_file) para interactuar con el ambiente. "
            "Razona sobre los pasos necesarios antes de responder. Sé conciso."
        )

        # 2. Inicialización de la Memoria (Historial de Mensajes)
        self.messages = []
        
        # 3. Inicialización de Herramientas
        # El SDK de Gemini las infiere automáticamente de los docstrings
        self.tools = self.setup_tools() 

    # --- Herramientas (Functions/Tools) del Agente ---

    def list_files_in_dir(self, directory: str = ".") -> str:
        """
        Lista los archivos y directorios dentro de la ruta especificada. 
        Útil para explorar el ambiente de trabajo del agente.
        :param directory: La ruta del directorio a listar. Por defecto es el directorio actual (.).
        :return: Una cadena JSON que contiene la lista de archivos o un mensaje de error.
        """
        print(f"🛠️ Ejecutando: list_files_in_dir en {directory}")
        try:
            files = os.listdir(directory)
            return json.dumps({"status": "success", "files": files})
        except FileNotFoundError:
            return json.dumps({"status": "error", "message": f"Directorio no encontrado: {directory}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Error al listar archivos: {e}"})

    def read_file(self, path: str) -> str:
        """
        Lee el contenido completo de un archivo en la ruta especificada. 
        Útil para entender el código o texto actual de un archivo antes de modificarlo.
        :param path: La ruta completa del archivo a leer.
        :return: Una cadena JSON que contiene el contenido del archivo o un mensaje de error.
        """
        print(f"🛠️ Ejecutando: read_file en {path}")
        try:
            with open(path, 'r') as f:
                content = f.read()
            return json.dumps({"status": "success", "content": content})
        except FileNotFoundError:
            return json.dumps({"status": "error", "message": f"Archivo no encontrado: {path}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Error al leer archivo: {e}"})
            
    def edit_file(self, path: str, new_text: str, old_text: str = None) -> str:
        """
        Edita o crea un archivo. Si 'old_text' se proporciona, reemplaza esa ocurrencia con 'new_text' 
        (útil para reemplazar funciones específicas). Si 'old_text' es None, reemplaza el contenido 
        completo (o crea el archivo si no existe).
        :param path: La ruta del archivo a editar/crear.
        :param new_text: El texto que se usará para reemplazar el 'old_text' o el contenido completo.
        :param old_text: (Opcional) El texto a ser reemplazado.
        :return: Una cadena JSON que indica el resultado de la operación.
        """
        print(f"🛠️ Ejecutando: edit_file en {path}. ¿Reemplazo? {bool(old_text)}")
        try:
            # 1. Manejo de reemplazo vs. creación/sobreescritura
            if os.path.exists(path) and old_text:
                with open(path, 'r') as f:
                    content = f.read()
                
                if old_text not in content:
                    return json.dumps({"status": "error", "message": "El texto a reemplazar (old_text) no fue encontrado."})
                
                content = content.replace(old_text, new_text, 1) # Reemplaza solo la primera ocurrencia
                action = "editado (reemplazo)"
            elif new_text:
                # 2. Creación o sobreescritura total
                content = new_text
                action = "creado/sobreescrito"
            else:
                return json.dumps({"status": "error", "message": "Se requiere new_text para crear o editar."})

            # 3. Escritura del archivo
            # Asegurar que el directorio exista (útil si el agente intenta crear en subcarpetas)
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True) 
            with open(path, 'w') as f:
                f.write(content)
                
            return json.dumps({"status": "success", "message": f"Archivo {path} {action} correctamente."})
            
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Error al editar/crear archivo: {e}"})

    def setup_tools(self):
        """
        Devuelve la lista de funciones de Python que el modelo puede llamar.
        """
        return [
            self.list_files_in_dir, 
            self.read_file, 
            self.edit_file
        ]
        
    def process_response(self, user_input: str):
        """
        Bucle de razonamiento iterativo: gestiona la comunicación con Gemini, la 
        ejecución de herramientas y la memoria del historial.
        """
        # 1. Añadir la entrada del usuario al historial
        self.messages.append(user_input)

        # Bucle interno: permite al agente ejecutar múltiples herramientas en una sola interacción
        while True:
            # 2. Llamada al Modelo con Historial, Instrucción del Sistema y Herramientas
            response = self.client.models.generate_content(
                model='gemini-2.5-flash', # Un modelo rápido y capaz de Function Calling
                contents=self.messages,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=self.tools
                )
            )

            # 3. Procesamiento de la Respuesta del Modelo
            if not response.function_calls:
                # Si no hay llamadas a función, la respuesta es texto final
                
                # 3a. Añadir la respuesta final del modelo al historial (Memoria)
                self.messages.append(response.text)
                
                print(f"\n🤖 Asistente:\n{response.text}\n")
                return # Salir del bucle, la conversación continúa en main.py

            # 4. Manejo de Llamadas a Función (Function Calling)
            tool_results = []
            
            for function_call in response.function_calls:
                function_name = function_call.name
                args = dict(function_call.args) # Argumentos dict
                
                print(f"--- Llamada del Modelo ---")
                print(f"🛠️ Función solicitada: {function_name}")
                print(f"📦 Argumentos: {args}")

                # Búsqueda y Ejecución de la Herramienta de Python
                if hasattr(self, function_name):
                    tool_function = getattr(self, function_name)
                    
                    # 5. Ejecución real de la función
                    result = tool_function(**args)
                    
                    # 6. Preparar el Resultado para Devolverlo al Modelo
                    tool_results.append(
                        types.Content(
                            role='tool',
                            parts=[types.Part.from_function_response(name=function_name, response={'result': result})]
                        )
                    )
                else:
                    error_msg = f"Error: Función {function_name} no implementada."
                    tool_results.append(
                        types.Content(
                            role='tool',
                            parts=[types.Part.from_function_response(name=function_name, response={'error': error_msg})]
                        )
                    )
            
            # 7. Re-Llamada al Modelo
            # Se adjunta la respuesta original (que incluye la solicitud de función) y el 
            # resultado de la herramienta (role='tool') para el razonamiento en la siguiente llamada.
            self.messages.append(response)  # La solicitud del modelo (qué quiere hacer)
            self.messages.extend(tool_results) # El resultado de la ejecución (qué pasó realmente)
            
            # El bucle 'while True' continúa, llamando de nuevo a Gemini con el historial extendido.