import math


GRAVEDAD = 9.81
LIMITE_MOVIMIENTO = 0.75
LIMITE_IMPACTO = 2.50


def clasificar_movimiento(x, y, z):
    magnitud = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    variacion = abs(magnitud - GRAVEDAD)

    if variacion >= LIMITE_IMPACTO:
        estado = "IMPACTO"
    elif variacion >= LIMITE_MOVIMIENTO:
        estado = "MOVIMIENTO"
    else:
        estado = "NORMAL"

    return {
        "magnitud": round(magnitud, 4),
        "variacion": round(variacion, 4),
        "estado": estado,
    }