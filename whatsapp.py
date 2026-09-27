import os

import requests
from dotenv import load_dotenv


load_dotenv()


def enviar_alerta_whatsapp(
    contenedor,
    cliente,
    destino,
    minutos_restantes,
    estado
):
    url = os.getenv("WAHA_URL")
    api_key = os.getenv("WAHA_API_KEY")
    sesion = os.getenv("WAHA_SESSION", "default")
    destinatario = os.getenv("WHATSAPP_TO")

    if not url or not api_key or not destinatario:
        raise ValueError(
            "Falta configurar WAHA_URL, WAHA_API_KEY o WHATSAPP_TO."
        )

    numero = "".join(
        caracter for caracter in destinatario if caracter.isdigit()
    )

    mensaje = (
        "Alerta de SysDespacho-IA\n"
        f"Contenedor: {contenedor}\n"
        f"Cliente: {cliente}\n"
        f"Destino: {destino}\n"
        f"Minutos restantes: {minutos_restantes}\n"
        f"Estado: {estado}"
    )

    respuesta = requests.post(
        f"{url.rstrip('/')}/api/sendText",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        },
        json={
            "chatId": f"{numero}@c.us",
            "text": mensaje,
            "session": sesion
        },
        timeout=30
    )

    respuesta.raise_for_status()

    return {
        "enviado": True,
        "contenedor": contenedor,
        "estado": estado,
        "codigo_http": respuesta.status_code
    }