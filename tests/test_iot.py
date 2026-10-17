import sqlite3

import iot_backend.almacenamiento as almacenamiento
from iot_backend.clasificacion import clasificar_movimiento


def test_clasifica_estado_normal():
    resultado = clasificar_movimiento(0, 0, 9.81)

    assert resultado["estado"] == "NORMAL"
    assert resultado["variacion"] == 0.0


def test_clasifica_movimiento():
    resultado = clasificar_movimiento(0, 0, 11)

    assert resultado["estado"] == "MOVIMIENTO"


def test_clasifica_impacto():
    resultado = clasificar_movimiento(0, 0, 15)

    assert resultado["estado"] == "IMPACTO"


def test_guarda_lectura_en_sqlite(tmp_path):
    ruta_temporal = tmp_path / "prueba_iot.db"
    almacenamiento.RUTA_BASE_DATOS = str(ruta_temporal)

    almacenamiento.crear_tabla()
    almacenamiento.guardar_lectura(
        tipo_sensor="android.sensor.accelerometer",
        eje_x=0.1,
        eje_y=0.2,
        eje_z=9.8,
        magnitud=9.8,
        variacion=0.01,
        estado="NORMAL",
        timestamp_sensor=123456,
    )

    with sqlite3.connect(ruta_temporal) as conexion:
        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM lecturas"
        ).fetchone()[0]

    assert cantidad == 1