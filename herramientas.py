import json

from funciones import clasificar_despacho
from google_sheets import registrar_despacho
from whatsapp import enviar_alerta_whatsapp
from correo import enviar_alerta_correo
from automatizacion import procesar_despacho_completo

HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "clasificar_despacho",
            "description": (
                "Clasifica un despacho según los minutos restantes. "
                "No registra información."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "minutos_restantes": {
                        "type": "integer",
                        "description": (
                            "Minutos antes de la hora programada. "
                            "Usar un número negativo si la hora ya pasó."
                        )
                    }
                },
                "required": ["minutos_restantes"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_despacho",
            "description": (
                "Clasifica y registra un despacho completo en "
                "Google Sheets. Usar solamente cuando el usuario "
                "solicite guardar o registrar la información."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "contenedor": {
                        "type": "string",
                        "description": (
                            "Código del contenedor, por ejemplo CONT-001."
                        )
                    },
                    "cliente": {
                        "type": "string",
                        "description": "Nombre del cliente."
                    },
                    "destino": {
                        "type": "string",
                        "description": "Destino del despacho."
                    },
                    "minutos_restantes": {
                        "type": "integer",
                        "description": (
                            "Minutos antes de la hora programada. "
                            "Usar un número negativo si ya pasó."
                        )
                    }
                },
                "required": [
                    "contenedor",
                    "cliente",
                    "destino",
                    "minutos_restantes"
                ],
                "additionalProperties": False
            }
                }
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_alerta_whatsapp",
            "description": (
                "Clasifica un despacho y envía una alerta por WhatsApp. "
                "Usar solamente cuando el usuario solicite expresamente "
                "enviar o notificar por WhatsApp."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "contenedor": {
                        "type": "string",
                        "description": (
                            "Código del contenedor, por ejemplo CONT-001."
                        )
                    },
                    "cliente": {
                        "type": "string",
                        "description": "Nombre del cliente."
                    },
                    "destino": {
                        "type": "string",
                        "description": "Destino del despacho."
                    },
                    "minutos_restantes": {
                        "type": "integer",
                        "description": (
                            "Minutos antes de la hora programada. "
                            "Usar un número negativo si ya pasó."
                        )
                    }
                },
                "required": [
                    "contenedor",
                    "cliente",
                    "destino",
                    "minutos_restantes"
                ],
                "additionalProperties": False
            }
                }
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_alerta_correo",
            "description": (
                "Clasifica un despacho y envía una alerta por correo. "
                "Usar solamente cuando el usuario solicite expresamente "
                "enviar o notificar por correo electrónico."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "contenedor": {
                        "type": "string",
                        "description": (
                            "Código del contenedor, por ejemplo CONT-001."
                        )
                    },
                    "cliente": {
                        "type": "string",
                        "description": "Nombre del cliente."
                    },
                    "destino": {
                        "type": "string",
                        "description": "Destino del despacho."
                    },
                    "minutos_restantes": {
                        "type": "integer",
                        "description": (
                            "Minutos antes de la hora programada. "
                            "Usar un número negativo si ya pasó."
                        )
                    }
                },
                "required": [
                    "contenedor",
                    "cliente",
                    "destino",
                    "minutos_restantes"
                ],
                "additionalProperties": False
            }
               }
    },
    {
        "type": "function",
        "function": {
            "name": "procesar_despacho_completo",
            "description": (
                "Clasifica un despacho, lo registra en Google Sheets "
                "y envía notificaciones por correo y WhatsApp. "
                "Usar solamente cuando el usuario solicite expresamente "
                "el proceso completo, registrar y notificar por todos "
                "los canales."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "contenedor": {
                        "type": "string",
                        "description": (
                            "Código del contenedor, por ejemplo CONT-001."
                        )
                    },
                    "cliente": {
                        "type": "string",
                        "description": "Nombre del cliente."
                    },
                    "destino": {
                        "type": "string",
                        "description": "Destino del despacho."
                    },
                    "minutos_restantes": {
                        "type": "integer",
                        "description": (
                            "Minutos antes de la hora programada. "
                            "Usar un número negativo si ya pasó."
                        )
                    }
                },
                "required": [
                    "contenedor",
                    "cliente",
                    "destino",
                    "minutos_restantes"
                ],
                "additionalProperties": False
            }
        }
    }
]

def ejecutar_herramienta(nombre, argumentos_json):
    """
    Ejecuta una herramienta solicitada por el modelo.
    """
    argumentos = json.loads(argumentos_json)

    if nombre == "clasificar_despacho":
        minutos = argumentos["minutos_restantes"]
        estado = clasificar_despacho(minutos)

        resultado = {
            "minutos_restantes": minutos,
            "estado": estado
        }

        return json.dumps(
            resultado,
            ensure_ascii=False
        )

    if nombre == "registrar_despacho":
        contenedor = argumentos["contenedor"]
        cliente = argumentos["cliente"]
        destino = argumentos["destino"]
        minutos = argumentos["minutos_restantes"]

        estado = clasificar_despacho(minutos)

        registro = registrar_despacho(
            contenedor=contenedor,
            cliente=cliente,
            destino=destino,
            minutos_restantes=minutos,
            estado=estado,
            origen="asistente_ia"
        )

        resultado = {
            "registrado": registro["registrado"],
            "contenedor": contenedor,
            "cliente": cliente,
            "destino": destino,
            "minutos_restantes": minutos,
            "estado": estado
        }

        return json.dumps(
            resultado,
            ensure_ascii=False
        )

    if nombre == "enviar_alerta_whatsapp":
        contenedor = argumentos["contenedor"]
        cliente = argumentos["cliente"]
        destino = argumentos["destino"]
        minutos = argumentos["minutos_restantes"]

        estado = clasificar_despacho(minutos)

        notificacion = enviar_alerta_whatsapp(
            contenedor=contenedor,
            cliente=cliente,
            destino=destino,
            minutos_restantes=minutos,
            estado=estado
        )

        resultado = {
            "enviado": notificacion["enviado"],
            "canal": "WhatsApp",
            "contenedor": contenedor,
            "cliente": cliente,
            "destino": destino,
            "minutos_restantes": minutos,
            "estado": estado
        }

        return json.dumps(
            resultado,
            ensure_ascii=False
        )

    if nombre == "enviar_alerta_correo":
        contenedor = argumentos["contenedor"]
        cliente = argumentos["cliente"]
        destino = argumentos["destino"]
        minutos = argumentos["minutos_restantes"]

        estado = clasificar_despacho(minutos)

        notificacion = enviar_alerta_correo(
            contenedor=contenedor,
            cliente=cliente,
            destino=destino,
            minutos_restantes=minutos,
            estado=estado
        )

        resultado = {
            "enviado": notificacion["enviado"],
            "canal": "Correo electrónico",
            "contenedor": contenedor,
            "cliente": cliente,
            "destino": destino,
            "minutos_restantes": minutos,
            "estado": estado
        }

        return json.dumps(
            resultado,
            ensure_ascii=False
        )
    
    if nombre == "procesar_despacho_completo":
        resultado = procesar_despacho_completo(
            contenedor=argumentos["contenedor"],
            cliente=argumentos["cliente"],
            destino=argumentos["destino"],
            minutos_restantes=argumentos["minutos_restantes"]
        )

        return json.dumps(
            resultado,
            ensure_ascii=False
        )
        
    raise ValueError(
        f"Herramienta desconocida: {nombre}"
    )