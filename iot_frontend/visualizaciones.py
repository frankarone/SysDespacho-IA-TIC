def crear_medidor_riesgo(indice_riesgo):
    return {
        "series": [
            {
                "type": "gauge",
                "startAngle": 210,
                "endAngle": -30,
                "min": 0,
                "max": 100,
                "splitNumber": 5,
                "axisLine": {
                    "lineStyle": {
                        "width": 18,
                        "color": [
                            [0.30, "#22C55E"],
                            [0.50, "#F59E0B"],
                            [1.00, "#EF4444"],
                        ],
                    }
                },
                "pointer": {
                    "length": "58%",
                    "width": 7,
                },
                "axisTick": {
                    "distance": -24,
                    "length": 6,
                },
                "splitLine": {
                    "distance": -28,
                    "length": 12,
                },
                "axisLabel": {
                    "distance": 28,
                    "fontSize": 11,
                },
                "detail": {
                    "valueAnimation": True,
                    "formatter": "{value}%",
                    "fontSize": 30,
                    "offsetCenter": [0, "62%"],
                },
                "title": {
                    "offsetCenter": [0, "88%"],
                    "fontSize": 13,
                },
                "data": [
                    {
                        "value": indice_riesgo,
                        "name": "Índice de riesgo",
                    }
                ],
            }
        ]
    }


def crear_radar_sensor(eje_x, eje_y, eje_z):
    limite = max(
        12,
        abs(eje_x) * 1.30,
        abs(eje_y) * 1.30,
        abs(eje_z) * 1.30,
    )

    return {
        "tooltip": {},
        "radar": {
            "indicator": [
                {
                    "name": "Eje X",
                    "min": -limite,
                    "max": limite,
                },
                {
                    "name": "Eje Y",
                    "min": -limite,
                    "max": limite,
                },
                {
                    "name": "Eje Z",
                    "min": -limite,
                    "max": limite,
                },
            ],
            "splitNumber": 4,
            "axisName": {
                "fontSize": 13,
            },
        },
        "series": [
            {
                "type": "radar",
                "areaStyle": {
                    "opacity": 0.28,
                },
                "lineStyle": {
                    "width": 3,
                },
                "symbolSize": 8,
                "data": [
                    {
                        "value": [
                            round(eje_x, 2),
                            round(eje_y, 2),
                            round(eje_z, 2),
                        ],
                        "name": "Lectura actual",
                    }
                ],
            }
        ],
    }


def crear_distribucion_estados(resumen):
    datos = [
        {
            "name": fila["estado"],
            "value": int(fila["cantidad"]),
        }
        for fila in resumen
    ]

    return {
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} ({d}%)",
        },
        "legend": {
            "bottom": 0,
        },
        "series": [
            {
                "name": "Estados",
                "type": "pie",
                "radius": ["48%", "72%"],
                "center": ["50%", "43%"],
                "avoidLabelOverlap": True,
                "label": {
                    "show": True,
                    "formatter": "{b}\n{d}%",
                },
                "itemStyle": {
                    "borderRadius": 6,
                    "borderWidth": 2,
                },
                "data": datos,
            }
        ],
    }