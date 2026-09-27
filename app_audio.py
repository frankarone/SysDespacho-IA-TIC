import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from transcripcion import transcribir_audio


# ==========================================================
# CONFIGURACIÓN
# ==========================================================
load_dotenv()

st.set_page_config(
    page_title="Prueba de audio",
    page_icon="🎙️"
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("No se encontró GROQ_API_KEY en el archivo .env")
    st.stop()


@st.cache_resource
def obtener_cliente(clave):
    return Groq(api_key=clave)


client = obtener_cliente(api_key)


# ==========================================================
# INTERFAZ
# ==========================================================
st.title("Transcripción de audio")
st.caption(
    "Prueba de Whisper para el proyecto SysDespacho-IA."
)

archivo_audio = st.file_uploader(
    "Selecciona un archivo de audio",
    type=["wav", "mp3", "m4a", "ogg", "webm"]
)

if archivo_audio:
    st.audio(archivo_audio)

    tamanio_maximo = 25 * 1024 * 1024

    if archivo_audio.size > tamanio_maximo:
        st.error("El archivo supera el límite de 25 MB.")
        st.stop()

    if st.button(
        "Transcribir audio",
        type="primary"
    ):
        try:
            with st.spinner("Transcribiendo con Whisper..."):
                texto = transcribir_audio(
                    client,
                    archivo_audio
                )

            st.success("Audio transcrito correctamente.")

            st.text_area(
                "Texto transcrito",
                value=texto,
                height=150
            )

        except Exception as error:
            st.error("No fue posible transcribir el audio.")
            st.code(str(error))

else:
    st.info(
        "Carga un archivo WAV, MP3, M4A, OGG o WEBM."
    )