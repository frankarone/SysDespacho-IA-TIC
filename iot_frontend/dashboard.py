import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


RUTA_BASE_DATOS = os.getenv(
    "IOT_DATABASE_PATH",
    "data/lecturas_iot.db",
)


st.set_page_config(
    page_title="Monitoreo IoT de contenedores",
    page_icon="📦",
    layout="wide",
)

st.title("Monitoreo IoT de contenedores")
st.caption(
    "Lecturas del acelerómetro del teléfono transmitidas mediante MQTT."
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
        datos["recibido_en"] = pd.to_datetime(datos["recibido_en"])
        datos = datos.sort_values("id")

    return datos, total


with st.sidebar:
    st.header("Opciones")

    limite = st.select_slider(
        "Cantidad de lecturas",
        options=[50, 100, 250, 500],
        value=100,
    )

    if st.button(
        "Actualizar datos",
        icon=":material/refresh:",
        width="stretch",
    ):
        cargar_lecturas.clear()


lecturas, total_lecturas = cargar_lecturas(limite)

if lecturas.empty:
    st.warning(
        "Todavía no existen lecturas almacenadas. "
        "Inicia el receptor MQTT y Sensor Spot."
    )
    st.stop()


ultima = lecturas.iloc[-1]

with st.container(horizontal=True):
    st.metric(
        "Lecturas almacenadas",
        total_lecturas,
        border=True,
    )
    st.metric(
        "Estado actual",
        ultima["estado"],
        border=True,
    )
    st.metric(
        "Magnitud actual",
        f"{ultima['magnitud']:.2f} m/s²",
        border=True,
    )
    st.metric(
        "Variación",
        f"{ultima['variacion']:.2f} m/s²",
        border=True,
    )


if ultima["estado"] == "IMPACTO":
    st.error("Se detectó un posible impacto en el contenedor.")
elif ultima["estado"] == "MOVIMIENTO":
    st.warning("El contenedor se encuentra en movimiento.")
else:
    st.success("El contenedor se encuentra en condición normal.")


columna_grafico, columna_estados = st.columns([2, 1])

with columna_grafico:
    with st.container(border=True):
        st.subheader("Lecturas de los ejes")
        st.line_chart(
            lecturas,
            x="recibido_en",
            y=["eje_x", "eje_y", "eje_z"],
            x_label="Fecha y hora",
            y_label="Aceleración (m/s²)",
        )

with columna_estados:
    with st.container(border=True):
        st.subheader("Estados detectados")

        resumen = (
            lecturas.groupby("estado")
            .size()
            .reset_index(name="cantidad")
        )

        st.bar_chart(
            resumen,
            x="estado",
            y="cantidad",
            x_label="Estado",
            y_label="Lecturas",
        )


with st.container(border=True):
    st.subheader("Historial reciente")

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
    ].sort_values("recibido_en", ascending=False)

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
            "estado": st.column_config.TextColumn("Estado"),
        },
    )