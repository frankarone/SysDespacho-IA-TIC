import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from herramientas import HERRAMIENTAS, ejecutar_herramienta
from transcripcion import transcribir_audio


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
load_dotenv()

st.set_page_config(
    page_title="SysDespacho-IA",
    page_icon="🚢"
)

api_key = os.getenv("GROQ_API_KEY")
modelo = os.getenv("GROQ_MODEL")

if not api_key:
    st.error("No se encontró GROQ_API_KEY en el archivo .env")
    st.stop()

if not modelo:
    st.error("No se encontró GROQ_MODEL en el archivo .env")
    st.stop()


@st.cache_resource
def obtener_cliente(clave):
    return Groq(api_key=clave)


client = obtener_cliente(api_key)


# ==========================================================
# INSTRUCCIONES
# ==========================================================
instrucciones = """
Eres DespachoBot, un asistente especializado en el control
de despachos de contenedores.

Responde siempre en español, de manera clara, amable y didáctica.

Los estados son:
- A_TIEMPO: faltan más de 30 minutos.
- PROXIMO: faltan entre 0 y 30 minutos.
- RETRASADO: la hora programada ya pasó.

Cuando el usuario solamente solicite una clasificación,
utiliza la herramienta clasificar_despacho.

Cuando el usuario solicite guardar o registrar un despacho,
utiliza la herramienta registrar_despacho.

Cuando el usuario solicite expresamente enviar o notificar
un despacho por WhatsApp, utiliza la herramienta
enviar_alerta_whatsapp.

Antes de enviar por WhatsApp, debes contar con:
- código del contenedor;
- cliente;
- destino;
- minutos restantes.

Nunca envíes una notificación por WhatsApp sin una solicitud
explícita del usuario.

Cuando el usuario solicite expresamente enviar o notificar
un despacho por correo electrónico, utiliza la herramienta
enviar_alerta_correo.

Antes de enviar por correo, debes contar con:
- código del contenedor;
- cliente;
- destino;
- minutos restantes.

Nunca envíes un correo sin una solicitud explícita del usuario.

Cuando el usuario solicite expresamente el proceso completo,
registrar el despacho y notificar por todos los canales,
utiliza la herramienta procesar_despacho_completo.

Esta herramienta registra en Google Sheets y envía correo
y WhatsApp. Antes de utilizarla debes contar con:
- código del contenedor;
- cliente;
- destino;
- minutos restantes.

Nunca ejecutes el proceso completo sin una solicitud explícita.
No ejecutes además las herramientas individuales cuando uses
procesar_despacho_completo, porque duplicaría las notificaciones.

Antes de registrar, debes contar con:
- código del contenedor;
- cliente;
- destino;
- minutos restantes.

Si falta algún dato, solicítalo antes de ejecutar la herramienta.
Nunca registres información sin una solicitud explícita del usuario.
No inventes información.
"""


# ==========================================================
# ESTADO DE LA APLICACIÓN
# ==========================================================
st.session_state.setdefault(
    "mensajes_api",
    [
        {
            "role": "system",
            "content": instrucciones
        }
    ]
)

st.session_state.setdefault("mensajes_ui", [])


# ==========================================================
# PROCESAMIENTO CON HERRAMIENTAS
# ==========================================================
def procesar_consulta():
    respuesta = client.chat.completions.create(
        model=modelo,
        messages=st.session_state.mensajes_api,
        tools=HERRAMIENTAS,
        tool_choice="auto"
    )

    mensaje_modelo = respuesta.choices[0].message

    if not mensaje_modelo.tool_calls:
        contenido = mensaje_modelo.content

        st.session_state.mensajes_api.append(
            {
                "role": "assistant",
                "content": contenido
            }
        )

        return contenido, []

    llamadas_api = []

    for llamada in mensaje_modelo.tool_calls:
        llamadas_api.append(
            {
                "id": llamada.id,
                "type": "function",
                "function": {
                    "name": llamada.function.name,
                    "arguments": llamada.function.arguments
                }
            }
        )

    st.session_state.mensajes_api.append(
        {
            "role": "assistant",
            "content": mensaje_modelo.content,
            "tool_calls": llamadas_api
        }
    )

    ejecuciones = []

    for llamada in mensaje_modelo.tool_calls:
        nombre = llamada.function.name
        argumentos = llamada.function.arguments
        resultado = ejecutar_herramienta(nombre, argumentos)

        ejecuciones.append(
            {
                "nombre": nombre,
                "argumentos": argumentos,
                "resultado": resultado
            }
        )

        st.session_state.mensajes_api.append(
            {
                "role": "tool",
                "tool_call_id": llamada.id,
                "name": nombre,
                "content": resultado
            }
        )

    respuesta_final = client.chat.completions.create(
        model=modelo,
        messages=st.session_state.mensajes_api
    )

    contenido_final = respuesta_final.choices[0].message.content

    st.session_state.mensajes_api.append(
        {
            "role": "assistant",
            "content": contenido_final
        }
    )

    return contenido_final, ejecuciones


# ==========================================================
# INTERFAZ
# ==========================================================
st.title("SysDespacho-IA")
st.subheader("DespachoBot")

st.caption(
    "Asistente con Function Calling y transcripción de audio "
    "para clasificar despachos de contenedores."
)

pregunta_audio = None

with st.sidebar:
    st.header("Opciones")

    if st.button("Nueva conversación"):
        st.session_state.mensajes_api = [
            {
                "role": "system",
                "content": instrucciones
            }
        ]
        st.session_state.mensajes_ui = []

        if "audio_despacho" in st.session_state:
            del st.session_state.audio_despacho

        if "microfono_despacho" in st.session_state:
            del st.session_state.microfono_despacho

        st.rerun()

        st.success("Conectado con Groq")
    st.info(
        "Herramientas disponibles: clasificar_despacho, "
        "registrar_despacho, enviar_alerta_whatsapp, "
        "enviar_alerta_correo y procesar_despacho_completo"
    )
    
    st.divider()
    st.subheader("Cargar archivo de audio")

    archivo_audio = st.file_uploader(
        "Carga un audio",
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        key="audio_despacho"
    )

    if archivo_audio:
        st.audio(archivo_audio)

        if st.button(
            "Transcribir archivo y enviar",
            type="primary"
        ):
            tamanio_maximo = 25 * 1024 * 1024

            if archivo_audio.size > tamanio_maximo:
                st.error(
                    "El archivo supera el límite de 25 MB."
                )

            else:
                try:
                    with st.spinner(
                        "Transcribiendo archivo con Whisper..."
                    ):
                        pregunta_audio = transcribir_audio(
                            client,
                            archivo_audio
                        )

                    st.success("Archivo transcrito.")

                    st.text_area(
                        "Transcripción del archivo",
                        value=pregunta_audio,
                        height=120
                    )

                except Exception as error:
                    st.error(
                        "No fue posible transcribir el archivo."
                    )
                    st.code(str(error))

    st.divider()
    st.subheader("Grabar con micrófono")

    audio_grabado = st.audio_input(
        "Pulsa para comenzar a grabar",
        sample_rate=16000,
        key="microfono_despacho"
    )

    if audio_grabado:
        if st.button(
            "Transcribir grabación y enviar",
            type="primary"
        ):
            try:
                with st.spinner(
                    "Transcribiendo grabación con Whisper..."
                ):
                    pregunta_audio = transcribir_audio(
                        client,
                        audio_grabado
                    )

                st.success("Grabación transcrita.")

                st.text_area(
                    "Transcripción del micrófono",
                    value=pregunta_audio,
                    height=120
                )

            except Exception as error:
                st.error(
                    "No fue posible transcribir la grabación."
                )
                st.code(str(error))

# ==========================================================
# HISTORIAL VISIBLE
# ==========================================================
for mensaje in st.session_state.mensajes_ui:
    with st.chat_message(mensaje["role"]):
        if mensaje.get("herramientas"):
            for herramienta in mensaje["herramientas"]:
                with st.expander(
                    f"Herramienta ejecutada: {herramienta['nombre']}"
                ):
                    st.caption("Argumentos JSON")
                    st.code(
                        herramienta["argumentos"],
                        language="json"
                    )

                    st.caption("Resultado")
                    st.code(
                        herramienta["resultado"],
                        language="json"
                    )

        st.markdown(mensaje["content"])


# ==========================================================
# NUEVO MENSAJE
# ==========================================================
pregunta_escrita = st.chat_input(
    "Escribe una consulta sobre un despacho",
    submit_mode="disable"
)

pregunta = pregunta_audio or pregunta_escrita

if pregunta:
    mensaje_api = {
        "role": "user",
        "content": pregunta
    }

    if pregunta_audio:
        contenido_visible = (
            "**Audio transcrito:**\n\n"
            f"{pregunta_audio}"
        )
    else:
        contenido_visible = pregunta

    mensaje_ui = {
        "role": "user",
        "content": contenido_visible
    }

    st.session_state.mensajes_api.append(mensaje_api)
    st.session_state.mensajes_ui.append(mensaje_ui)

    with st.chat_message("user"):
        st.markdown(contenido_visible)

    with st.chat_message("assistant"):
        try:
            with st.status(
                "Procesando consulta...",
                type="compact"
            ) as estado:
                contenido, ejecuciones = procesar_consulta()

                estado.update(
                    label="Consulta procesada",
                    state="complete"
                )

            for herramienta in ejecuciones:
                with st.expander(
                    f"Herramienta ejecutada: {herramienta['nombre']}"
                ):
                    st.caption("Argumentos JSON")
                    st.code(
                        herramienta["argumentos"],
                        language="json"
                    )

                    st.caption("Resultado")
                    st.code(
                        herramienta["resultado"],
                        language="json"
                    )

            st.markdown(contenido)

            st.session_state.mensajes_ui.append(
                {
                    "role": "assistant",
                    "content": contenido,
                    "herramientas": ejecuciones
                }
            )

        except Exception as error:
            st.error("No fue posible procesar la consulta.")
            st.code(str(error))