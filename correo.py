import os
import smtplib
import ssl
from email.message import EmailMessage


def enviar_alerta_correo(
    contenedor,
    cliente,
    destino,
    minutos_restantes,
    estado
):
    """
    Envía una alerta de despacho mediante Gmail SMTP.
    """
    servidor_smtp = os.getenv("SMTP_HOST")
    puerto_smtp = int(os.getenv("SMTP_PORT", "587"))
    correo_remitente = os.getenv("SMTP_USER")
    clave_aplicacion = os.getenv("SMTP_APP_PASSWORD")
    correo_destino = os.getenv("ALERT_EMAIL_TO")

    if not servidor_smtp:
        raise RuntimeError("No se encontró SMTP_HOST")

    if not correo_remitente:
        raise RuntimeError("No se encontró SMTP_USER")

    if not clave_aplicacion:
        raise RuntimeError(
            "No se encontró SMTP_APP_PASSWORD"
        )

    if not correo_destino:
        raise RuntimeError("No se encontró ALERT_EMAIL_TO")

    mensaje = EmailMessage()

    mensaje["From"] = correo_remitente
    mensaje["To"] = correo_destino
    mensaje["Subject"] = (
        f"Alerta de despacho: {contenedor} - {estado}"
    )

    mensaje.set_content(
        f"""
SYS DESPACHO IA - ALERTA DE CONTENEDOR

Contenedor: {contenedor}
Cliente: {cliente}
Destino: {destino}
Minutos restantes: {minutos_restantes}
Estado: {estado}

Mensaje generado automáticamente por DespachoBot.
        """.strip()
    )

    contexto_seguro = ssl.create_default_context()

    with smtplib.SMTP(
        servidor_smtp,
        puerto_smtp,
        timeout=30
    ) as servidor:
        servidor.starttls(context=contexto_seguro)
        servidor.login(
            correo_remitente,
            clave_aplicacion
        )
        servidor.send_message(mensaje)

    return {
        "enviado": True,
        "contenedor": contenedor,
        "estado": estado
    }