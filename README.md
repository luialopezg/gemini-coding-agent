# 🤖 Gemini Coding Agent: Agente de Codificación Autónomo con Function Calling

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![Gemini SDK](https://img.shields.io/badge/Google-GenAI%20SDK-FF0000)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

Este proyecto implementa un **Agente de Codificación** conversacional utilizando la familia de modelos **Gemini de Google** y el SDK oficial `google-genai`. El agente está diseñado para interactuar y modificar su propio entorno de desarrollo (un sistema Linux Mint/similar) mediante la invocación de funciones (Function Calling) específicas para el manejo de archivos.

## 🌟 Características Principales

El agente se centra en el **razonamiento multi-paso** y la interacción con el sistema operativo a través de tres herramientas fundamentales:

1.  **Exploración del Entorno (`list_files_in_dir`):** Permite al agente inspeccionar su directorio de trabajo.
2.  **Lectura y Análisis (`read_file`):** Capacita al agente para leer el contenido de archivos y analizar código existente.
3.  **Modificación Autónoma (`edit_file`):** Habilita la creación, sobreescritura o modificación precisa de archivos (reemplazo de texto), permitiendo al agente auto-corregirse o generar código nuevo.

## 🚀 Arquitectura y Funcionamiento

El corazón del agente reside en un **bucle de razonamiento iterativo** implementado en Python.

El flujo de interacción con el modelo Gemini es clave en esta arquitectura:

1.  **Entrada del Usuario:** El usuario proporciona una instrucción (ej: "Edita `main.py`").
2.  **Llamada a Gemini:** El agente envía el historial de la conversación, la **Instrucción del Sistema** y la lista de **herramientas** disponibles.
3.  **Decisión del Modelo:**
    * Si Gemini decide usar una herramienta, devuelve un objeto `function_calls`.
    * El agente ejecuta la función Python localmente (ej: `read_file(...)`).
    * El **resultado de la ejecución** (con el rol `tool`) se añade al historial.
    * El agente vuelve a llamar a Gemini con el historial actualizado, permitiendo al modelo razonar sobre el resultado de la herramienta y generar una respuesta final.

## 🛠️ Configuración del Ambiente (Linux Mint)

### Prerrequisitos

* Python 3.10+
* Git instalado
* Clave API de Gemini

### Instalación y Configuración

1.  **Clonar el Repositorio:**
    ```bash
    git clone git@github.com:luialopezg/gemini-coding-agent.git
    cd gemini-coding-agent
    ```

2.  **Configurar Ambiente Virtual e Instalación de Dependencias:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install google-genai python-dotenv
    ```

3.  **Manejo de la Clave API:**
    Para proteger tu licencia, crea un archivo `.env` en el directorio raíz (listado en `.gitignore`):
    ```
    # .env
    GEMINI_API_KEY=TU_CLAVE_PRIVADA_AQUÍ
    ```

## 🏃 Ejecución del Agente

Asegúrate de que tu ambiente virtual esté activo: `source venv/bin/activate`

```bash
python main.py
```

### Ejemplo de Interacción
Instrucción,Flujo de Razonamiento Esperado
¿Qué archivos hay aquí?,list_files_in_dir
Crea una función en 'utils.py',edit_file (Modo Creación)
Cambia la función de suma en 'calculadora.py' y verifica el código.,read_file -> edit_file -> read_file (Multi-paso)

## 3. 🔍 Identificación de Mejoras (Seniority)

Basado en la estructura actual del proyecto, la principal mejora que se identifica desde un punto de vista de ingeniería de software es la **refactorización** y la **robustez** del código:

### A. Modularización de la Memoria

* **Mejora:** El historial de mensajes (`self.messages`) se está gestionando como una lista simple dentro de la clase `CodingAgent`.
* **Nivel Senior:** Para proyectos más grandes, sería mejor usar el **módulo `Chat`** del SDK de Gemini (`client.chats.create(...)`). El objeto `Chat` de Gemini ya gestiona internamente el historial, simplificando el bucle `process_response` y haciendo que el manejo de la memoria sea más seguro y nativo del SDK.

### B. Manejo de Errores y *Logging*

* **Mejora:** Las funciones de herramienta (`list_files_in_dir`, etc.) devuelven cadenas JSON que incluyen `"status": "error"`.
* **Nivel Senior:** Para un agente de producción, las herramientas deberían devolver estructuras de datos nativas (objetos o diccionarios) en lugar de cadenas JSON, y el *logging* debería usarse para registrar las llamadas y los errores de E/S del sistema (que son comunes en Linux), separando la depuración de la respuesta final del agente.

