import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


RUTA_BASE_DATOS = os.getenv(
    "IOT_DATABASE_PATH",
    "data/lecturas_iot.db",
)


def obtener_conexion():
    ruta = Path(RUTA_BASE_DATOS)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(ruta)


def crear_tabla():
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS lecturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_sensor TEXT NOT NULL,
                eje_x REAL NOT NULL,
                eje_y REAL NOT NULL,
                eje_z REAL NOT NULL,
                magnitud REAL NOT NULL,
                variacion REAL NOT NULL,
                estado TEXT NOT NULL,
                timestamp_sensor INTEGER,
                recibido_en TEXT NOT NULL
            )
            """
        )


def guardar_lectura(
    tipo_sensor,
    eje_x,
    eje_y,
    eje_z,
    magnitud,
    variacion,
    estado,
    timestamp_sensor,
):
    recibido_en = datetime.now(timezone.utc).isoformat()

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            INSERT INTO lecturas (
                tipo_sensor,
                eje_x,
                eje_y,
                eje_z,
                magnitud,
                variacion,
                estado,
                timestamp_sensor,
                recibido_en
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tipo_sensor,
                eje_x,
                eje_y,
                eje_z,
                magnitud,
                variacion,
                estado,
                timestamp_sensor,
                recibido_en,
            ),
        )