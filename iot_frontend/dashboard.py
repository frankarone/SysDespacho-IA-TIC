import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from iot_frontend.visualizaciones import (
    crear_distribucion_estados,
    crear_medidor_riesgo,
    crear_radar_sensor,
)


RUTA_BASE_DATOS = os.getenv(
    "IOT_DATABASE_PATH",
    "data/lecturas_iot.db",
)


st.set_page_config(
    page_title="SysDespacho | Centro IoT",
    page_icon=":material/local_shipping:",
    layout="wide",
)

st.title(
    "Centro de monitoreo IoT",
    icon=":material/local_shipping:",
)
st.caption(
    "SysDespacho · Supervisión de movimiento e impactos "
    "en contenedores en tiempo casi real"
)


@st.cache_data(ttl=2)
def cargar_lecturas(limite):
    ruta = Path(RUTA_BASE_DATOS)

    if not ruta.exists():
        return pd.DataFrame(), 0

    with sqlite3.connect(ruta) as conexion:
        total = conexion.execute(
            "SELECT COUNT(*) FROM lecturas"
        ).fetchone()[0]

        datos = pd.read_sql_query(
            """
            SELECT
                id,
                eje_x,
                eje_y,
                eje_z,
                magnitud,
                variacion,
                estado,
                recibido_en
            FROM lecturas
            ORDER BY id DESC
            LIMIT ?
            """,
            conexion,
            params=(limite,),
        )

    if not datos.empty:
        datos["recibido_en"] = pd.to_datetime(
            datos["recibido_en"],
            utc=True,
        )
        datos = datos.sort_values("id")

    return datos, total


with st.sidebar:
    st.header(
        "Panel de control",
        icon=":material/tune:",
    )

    limite = st.select_slider(
        "Ventana de análisis",
        options=[50, 100, 250, 500],
        value=100,
        help="Cantidad de lecturas recientes que se mostrarán.",
    )

    if st.button(
        "Actualizar información",
        icon=":material/refresh:",
        type="primary",
        width="stretch",
    ):
        cargar_lecturas.clear()

    st.space("small")
    st.caption("ORIGEN DE DATOS")
    st.markdown("**Sensor:** acelerómetro Android")
    st.markdown("**Transporte:** MQTT")
    st.markdown("**Almacenamiento:** SQLite")
    st.markdown("**Despliegue:** Docker Compose")

    st.space("small")
    st.caption("SysDespacho IoT · TA3")


lecturas, total_lecturas = cargar_lecturas(limite)

if lecturas.empty:
    st.info(
        "La plataforma está disponible, pero todavía no existen "
        "lecturas almacenadas. Inicia Sensor Spot para enviar datos.",
        icon=":material/sensors_off:",
    )
    st.stop()


ultima = lecturas.iloc[-1]
indice_riesgo = min(
    100,
    round(float(ultima["variacion"]) / 2.50 * 100),
)
ultima_fecha = ultima["recibido_en"]
ahora = pd.Timestamp.now(tz="UTC")
segundos_sin_datos = max(
    0,
    int((ahora - ultima_fecha).total_seconds()),
)

if segundos_sin_datos <= 30:
    st.badge(
        "Datos recientes",
        icon=":material/check_circle:",
        color="green",
    )
else:
    st.badge(
        f"Última lectura hace {segundos_sin_datos} segundos",
        icon=":material/schedule:",
        color="orange",
    )

st.caption(
    "Última recepción: "
    f"{ultima_fecha.strftime('%d/%m/%Y %H:%M:%S')} UTC"
)

tendencia_magnitud = (
    lecturas["magnitud"]
    .tail(30)
    .tolist()
)

with st.container(horizontal=True):
    st.metric(
        "Lecturas almacenadas",
        f"{total_lecturas:,}",
        border=True,
        chart_data=lecturas["magnitud"].tail(20).tolist(),
        chart_type="line",
    )
    st.metric(
        "Condición actual",
        ultima["estado"],
        border=True,
    )
    st.metric(
        "Magnitud",
        f"{ultima['magnitud']:.2f} m/s²",
        border=True,
        chart_data=tendencia_magnitud,
        chart_type="line",
    )
    st.metric(
        "Variación",
        f"{ultima['variacion']:.2f} m/s²",
        border=True,
        chart_data=lecturas["variacion"].tail(30).tolist(),
        chart_type="bar",
    )


if ultima["estado"] == "IMPACTO":
    st.error(
        "Alerta crítica: se detectó un posible impacto "
        "durante el traslado del contenedor.",
        icon=":material/error:",
    )
elif ultima["estado"] == "MOVIMIENTO":
    st.warning(
        "Atención: el contenedor registra movimiento.",
        icon=":material/warning:",
    )
else:
    st.success(
        "Operación estable: el contenedor se encuentra "
        "en condición normal.",
        icon=":material/check_circle:",
    )


tab_resumen, tab_analitica, tab_historial = st.tabs(
    [
        "Resumen operativo",
        "Analítica del sensor",
        "Historial de lecturas",
    ]
)


with tab_resumen:
    st.subheader(
        "Torre de control del contenedor",
        icon=":material/space_dashboard:",
    )
    st.caption(
        "Vista ejecutiva del riesgo, orientación del sensor "
        "y distribución de condiciones."
    )

    resumen = (
        lecturas.groupby("estado")
        .size()
        .reset_index(name="cantidad")
    )

    columna_riesgo, columna_radar, columna_distribucion = st.columns(
        3,
        vertical_alignment="top",
    )

    with columna_riesgo:
        with st.container(border=True):
            st.markdown("**Nivel operativo de riesgo**")
            st.echarts_chart(
                crear_medidor_riesgo(indice_riesgo),
                height=330,
                key="medidor_riesgo",
            )

    with columna_radar:
        with st.container(border=True):
            st.markdown("**Orientación actual del sensor**")
            st.echarts_chart(
                crear_radar_sensor(
                    float(ultima["eje_x"]),
                    float(ultima["eje_y"]),
                    float(ultima["eje_z"]),
                ),
                height=330,
                key="radar_sensor",
            )

    with columna_distribucion:
        with st.container(border=True):
            st.markdown("**Composición de estados**")
            st.echarts_chart(
                crear_distribucion_estados(
                    resumen.to_dict("records")
                ),
                height=330,
                key="distribucion_estados",
            )

    with st.container(
        horizontal=True,
        horizontal_alignment="distribute",
        border=True,
    ):
        st.badge(
            "CONT-IOT-001",
            icon=":material/inventory_2:",
            color="blue",
        )
        st.badge(
            "Huaral → Puerto del Callao",
            icon=":material/route:",
            color="gray",
        )

        if segundos_sin_datos <= 30:
            st.badge(
                "Telemetría reciente",
                icon=":material/sensors:",
                color="green",
            )
        else:
            st.badge(
                "Telemetría sin actualizar",
                icon=":material/sensors_off:",
                color="orange",
            )


with tab_analitica:
    columna_variacion, columna_resumen = st.columns(
        [2, 1],
        vertical_alignment="top",
    )

    with columna_variacion:
        with st.container(border=True):
            st.subheader(
                "Variación respecto de la gravedad",
                icon=":material/monitoring:",
            )
            st.caption(
                "Valores elevados pueden representar movimientos "
                "bruscos o impactos."
            )
            st.line_chart(
                lecturas,
                x="recibido_en",
                y="variacion",
                x_label="Fecha y hora",
                y_label="Variación (m/s²)",
            )

    with columna_resumen:
        with st.container(border=True):
            st.subheader(
                "Resumen de condiciones",
                icon=":material/analytics:",
            )

            resumen_detallado = (
                lecturas.groupby("estado")
                .size()
                .reset_index(name="Lecturas")
            )
            resumen_detallado["Porcentaje"] = (
                resumen_detallado["Lecturas"]
                / resumen_detallado["Lecturas"].sum()
                * 100
            )

            st.dataframe(
                resumen_detallado,
                hide_index=True,
                column_config={
                    "estado": st.column_config.TextColumn(
                        "Estado"
                    ),
                    "Lecturas": st.column_config.NumberColumn(
                        "Lecturas",
                        format="%d",
                    ),
                    "Porcentaje": st.column_config.NumberColumn(
                        "Participación",
                        format="%.1f%%",
                    ),
                },
            )


with tab_historial:
    with st.container(border=True):
        st.subheader(
            "Registro reciente",
            icon=":material/table_chart:",
        )
        st.caption(
            "Detalle cronológico de las lecturas procesadas "
            "por el receptor IoT."
        )

        historial = lecturas[
            [
                "recibido_en",
                "eje_x",
                "eje_y",
                "eje_z",
                "magnitud",
                "variacion",
                "estado",
            ]
        ].sort_values(
            "recibido_en",
            ascending=False,
        )

        st.dataframe(
            historial,
            hide_index=True,
            column_config={
                "recibido_en": st.column_config.DatetimeColumn(
                    "Fecha y hora",
                    format="DD/MM/YYYY HH:mm:ss",
                ),
                "eje_x": st.column_config.NumberColumn(
                    "Eje X",
                    format="%.2f",
                ),
                "eje_y": st.column_config.NumberColumn(
                    "Eje Y",
                    format="%.2f",
                ),
                "eje_z": st.column_config.NumberColumn(
                    "Eje Z",
                    format="%.2f",
                ),
                "magnitud": st.column_config.NumberColumn(
                    "Magnitud",
                    format="%.2f",
                ),
                "variacion": st.column_config.NumberColumn(
                    "Variación",
                    format="%.2f",
                ),
                "estado": st.column_config.TextColumn(
                    "Estado"
                ),
            },
        )