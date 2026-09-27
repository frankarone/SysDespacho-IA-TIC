import json

import pytest

from herramientas import ejecutar_herramienta


def test_herramienta_clasifica_con_json():
    argumentos = json.dumps(
        {
            "minutos_restantes": 15
        }
    )

    resultado_json = ejecutar_herramienta(
        "clasificar_despacho",
        argumentos
    )

    resultado = json.loads(resultado_json)

    assert resultado["minutos_restantes"] == 15
    assert resultado["estado"] == "PROXIMO"


def test_herramienta_desconocida_genera_error():
    argumentos = json.dumps({})

    with pytest.raises(ValueError):
        ejecutar_herramienta(
            "herramienta_inexistente",
            argumentos
        )