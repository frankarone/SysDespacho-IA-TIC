import os

from dotenv import load_dotenv
from groq import Groq


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
modelo = os.getenv("GROQ_MODEL")

if not api_key:
    raise RuntimeError("No se encontró GROQ_API_KEY en el archivo .env")

if not modelo:
    raise RuntimeError("No se encontró GROQ_MODEL en el archivo .env")

client = Groq(api_key=api_key)


# ==========================================================
# INSTRUCCIONES DE DESPACHOBOT
# ==========================================================
instrucciones = """
Eres DespachoBot, un asistente especializado exclusivamente
en el control de despachos de contenedores.

Debes responder en español de manera:
- amigable;
- clara;
- paciente;
- didáctica.

Los estados de un despacho son:
- A_TIEMPO: faltan más de 30 minutos.
- PROXIMO: faltan entre 0 y 30 minutos.
- RETRASADO: la hora programada ya pasó.

Cuando el usuario consulte por un despacho:
1. Identifica el código del contenedor.
2. Identifica el cliente y el destino, si fueron proporcionados.
3. Determina cuánto tiempo falta para el despacho.
4. Explica el estado calculado.
5. No inventes datos que el usuario no haya proporcionado.

Si faltan datos importantes, solicita la información necesaria.
Si la consulta no se relaciona con despachos de contenedores,
indica amablemente que esa es tu especialidad.
"""


# ==========================================================
# HISTORIAL DE CONVERSACIÓN
# ==========================================================
mensajes = [
    {
        "role": "system",
        "content": instrucciones
    }
]


# ==========================================================
# INICIO DEL CHATBOT
# ==========================================================
print("========================================")
print("             DESPACHOBOT")
print("========================================")
print("Asistente para despachos de contenedores")
print("Escribe 'salir' para terminar.\n")


# ==========================================================
# BUCLE DE CONVERSACIÓN
# ==========================================================
while True:
    pregunta = input("Tú: ").strip()

    if pregunta.lower() == "salir":
        print("DespachoBot: Conversación finalizada.")
        break

    if not pregunta:
        print("DespachoBot: Escribe una consulta para continuar.\n")
        continue

    mensajes.append(
        {
            "role": "user",
            "content": pregunta
        }
    )

    try:
        respuesta = client.chat.completions.create(
            model=modelo,
            messages=mensajes
        )

        contenido = respuesta.choices[0].message.content

        mensajes.append(
            {
                "role": "assistant",
                "content": contenido
            }
        )

        print("\nDespachoBot:")
        print(contenido)
        print()

    except Exception as error:
        print("\nDespachoBot: No fue posible procesar la consulta.")
        print(f"Detalle técnico: {error}\n")