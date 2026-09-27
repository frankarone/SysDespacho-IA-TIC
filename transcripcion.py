import os


def transcribir_audio(client, archivo_audio):
    """
    Transcribe un archivo de audio en español utilizando Whisper.
    """
    modelo_audio = os.getenv("GROQ_AUDIO_MODEL")

    if not modelo_audio:
        raise RuntimeError(
            "No se encontró GROQ_AUDIO_MODEL en el archivo .env"
        )

    nombre_archivo = getattr(
        archivo_audio,
        "name",
        "audio.wav"
    )

    if hasattr(archivo_audio, "getvalue"):
        contenido = archivo_audio.getvalue()
    else:
        contenido = archivo_audio.read()

    transcripcion = client.audio.transcriptions.create(
        file=(nombre_archivo, contenido),
        model=modelo_audio,
        prompt=(
            "El audio trata sobre despachos de contenedores. "
            "Los códigos utilizan el formato CONT-000. "
            "Ejemplos: CONT-001, CONT-050 y CONT-100."
        ),
        language="es",
        response_format="json",
        temperature=0.0
    )

    return transcripcion.text.strip()