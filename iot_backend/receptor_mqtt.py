import json
import os
import uuid

import paho.mqtt.client as mqtt

from iot_backend.almacenamiento import crear_tabla, guardar_lectura
from iot_backend.clasificacion import clasificar_movimiento


BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
PUERTO = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv(
    "MQTT_TOPIC",
    "sysdespacho/frankarone/ta3/acelerometro",
)


def al_conectar(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Conectado al broker {BROKER}:{PUERTO}", flush=True)
        print(f"Suscrito al topic: {TOPIC}", flush=True)
        client.subscribe(TOPIC)
    else:
        print(f"No se pudo conectar. Código: {reason_code}", flush=True)


def al_recibir_mensaje(client, userdata, mensaje):
    try:
        datos = json.loads(mensaje.payload.decode("utf-8"))
        valores = datos["values"]

        if len(valores) < 3:
            raise ValueError("La lectura no contiene los tres ejes")

        eje_x = float(valores[0])
        eje_y = float(valores[1])
        eje_z = float(valores[2])

        clasificacion = clasificar_movimiento(eje_x, eje_y, eje_z)

        guardar_lectura(
            tipo_sensor=datos.get("type", "sensor_desconocido"),
            eje_x=eje_x,
            eje_y=eje_y,
            eje_z=eje_z,
            magnitud=clasificacion["magnitud"],
            variacion=clasificacion["variacion"],
            estado=clasificacion["estado"],
            timestamp_sensor=datos.get("timestamp"),
        )

        print(
            f"Lectura recibida: "
            f"x={eje_x:.2f}, y={eje_y:.2f}, z={eje_z:.2f}, "
            f"estado={clasificacion['estado']}",
            flush=True,
        )

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"Mensaje inválido: {error}", flush=True)


def iniciar():
    crear_tabla()

    identificador = f"sysdespacho-receptor-{uuid.uuid4().hex[:8]}"
    cliente = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=identificador,
        protocol=mqtt.MQTTv5,
    )

    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir_mensaje

    print("Iniciando receptor IoT...", flush=True)
    cliente.connect(BROKER, PUERTO, keepalive=60)
    cliente.loop_forever()


if __name__ == "__main__":
    iniciar()