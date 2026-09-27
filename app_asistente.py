import os

from dotenv import load_dotenv
from groq import Groq

from herramientas import HERRAMIENTAS, ejecutar_herramienta


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
# INSTRUCCIONES DEL ASISTENTE
# ==========================================================
instrucciones = """
Eres DespachoBot, un asistente especializado en el control
de despachos de contenedores.

Responde siempre en español, de manera clara, amable y didáctica.

Estados disponibles:
- A_TIEMPO: faltan más de 30 minutos.
- PROXIMO: faltan entre 0 y 30 minutos.
- RETRASADO: la hora programada ya pasó.

Cuando el usuario proporcione los minutos restantes o solicite
clasificar un despacho, debes utilizar obligatoriamente la
herramienta clasificar_despacho.

No calcules el estado por tu cuenta cuando puedas utilizar
la herramienta. No inventes información que no haya sido entregada.
"""


mensajes = [
    {
        "role": "system",
        "content": instrucciones
    }
]


# ==========================================================
# PROCESAMIENTO DEL ASISTENTE
# ==========================================================
def procesar_consulta():
    respuesta = client.chat.completions.create(
        model=modelo,
        messages=mensajes,
        tools=HERRAMIENTAS,
        tool_choice="auto"
    )

    mensaje_modelo = respuesta.choices[0].message

    if not mensaje_modelo.tool_calls:
        contenido = mensaje_modelo.content

        mensajes.append(
            {
                "role": "assistant",
                "content": contenido
            }
        )

        return contenido

    llamadas = []

    for llamada in mensaje_modelo.tool_calls:
        llamadas.append(
            {
                "id": llamada.id,
                "type": "function",
                "function": {
                    "name": llamada.function.name,
                    "arguments": llamada.function.arguments
                }
            }
        )

    mensajes.append(
        {
            "role": "assistant",
            "content": mensaje_modelo.content,
            "tool_calls": llamadas
        }
    )

    for llamada in mensaje_modelo.tool_calls:
        nombre = llamada.function.name
        argumentos = llamada.function.arguments

        resultado = ejecutar_herramienta(nombre, argumentos)

        print(f"\n[Herramienta ejecutada: {nombre}]")
        print(f"[Argumentos JSON: {argumentos}]")
        print(f"[Resultado: {resultado}]")

        mensajes.append(
            {
                "role": "tool",
                "tool_call_id": llamada.id,
                "name": nombre,
                "content": resultado
            }
        )

    respuesta_final = client.chat.completions.create(
        model=modelo,
        messages=mensajes
    )

    contenido_final = respuesta_final.choices[0].message.content

    mensajes.append(
        {
            "role": "assistant",
            "content": contenido_final
        }
    )

    return contenido_final


# ==========================================================
# INICIO DEL ASISTENTE
# ==========================================================
print("========================================")
print("       DESPACHOBOT CON HERRAMIENTAS")
print("========================================")
print("Escribe 'salir' para terminar.\n")


while True:
    pregunta = input("Tú: ").strip()

    if pregunta.lower() == "salir":
        print("DespachoBot: Conversación finalizada.")
        break

    if not pregunta:
        print("DespachoBot: Escribe una consulta.\n")
        continue

    mensajes.append(
        {
            "role": "user",
            "content": pregunta
        }
    )

    try:
        respuesta = procesar_consulta()

        print("\nDespachoBot:")
        print(respuesta)
        print()

    except Exception as error:
        print("\nDespachoBot: No fue posible procesar la consulta.")
        print(f"Detalle técnico: {error}\n")