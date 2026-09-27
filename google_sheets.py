import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


ALCANCES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def obtener_hoja():
    """
    Conecta con la pestaña configurada en Google Sheets.
    """
    archivo_credenciales = os.getenv(
        "GOOGLE_CREDENTIALS_FILE"
    )
    id_hoja = os.getenv("GOOGLE_SHEET_ID")
    nombre_pestana = os.getenv("GOOGLE_WORKSHEET")

    if not archivo_credenciales:
        raise RuntimeError(
            "No se encontró GOOGLE_CREDENTIALS_FILE"
        )

    if not id_hoja:
        raise RuntimeError(
            "No se encontró GOOGLE_SHEET_ID"
        )

    if not nombre_pestana:
        raise RuntimeError(
            "No se encontró GOOGLE_WORKSHEET"
        )

    credenciales = Credentials.from_service_account_file(
        archivo_credenciales,
        scopes=ALCANCES
    )

    cliente = gspread.authorize(credenciales)
    libro = cliente.open_by_key(id_hoja)

    return libro.worksheet(nombre_pestana)


def registrar_despacho(
    contenedor,
    cliente,
    destino,
    minutos_restantes,
    estado,
    origen="chat"
):
    """
    Registra un despacho en Google Sheets.
    """
    hoja = obtener_hoja()

    fecha = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    fila = [
        fecha,
        contenedor,
        cliente,
        destino,
        minutos_restantes,
        estado,
        origen
    ]

    hoja.append_row(
        fila,
        value_input_option="USER_ENTERED"
    )

    return {
        "registrado": True,
        "contenedor": contenedor,
        "estado": estado
    }