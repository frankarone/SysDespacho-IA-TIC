from correo import enviar_alerta_correo
from funciones import clasificar_despacho
from google_sheets import registrar_despacho
from whatsapp import enviar_alerta_whatsapp


def procesar_despacho_completo(
    contenedor,
    cliente,
    destino,
    minutos_restantes
):
    """
    Clasifica el despacho, lo registra y envía notificaciones.
    """
    estado = clasificar_despacho(minutos_restantes)

    registro = registrar_despacho(
        contenedor=contenedor,
        cliente=cliente,
        destino=destino,
        minutos_restantes=minutos_restantes,
        estado=estado,
        origen="automatizacion_completa"
    )

    correo = enviar_alerta_correo(
        contenedor=contenedor,
        cliente=cliente,
        destino=destino,
        minutos_restantes=minutos_restantes,
        estado=estado
    )

    whatsapp = enviar_alerta_whatsapp(
        contenedor=contenedor,
        cliente=cliente,
        destino=destino,
        minutos_restantes=minutos_restantes,
        estado=estado
    )

    return {
        "procesado": True,
        "contenedor": contenedor,
        "cliente": cliente,
        "destino": destino,
        "minutos_restantes": minutos_restantes,
        "estado": estado,
        "google_sheets": registro["registrado"],
        "correo": correo["enviado"],
        "whatsapp": whatsapp["enviado"]
    }