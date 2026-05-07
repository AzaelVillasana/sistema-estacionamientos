import streamlit as st
import pandas as pd
from datetime import datetime
import re

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Sistema de Estacionamientos",
    layout="wide"
)

# =====================================
# LOGIN SIMPLE
# =====================================

USUARIOS = {
    "azael": "azael123",
    "admin": "admin123"
}

# =====================================
# SESIÓN
# =====================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =====================================
# LOGIN
# =====================================

if not st.session_state.logged_in:

    st.title("🔐 Login")

    usuario = st.text_input(
        "Usuario"
    )

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Entrar"):

        if usuario in USUARIOS and USUARIOS[usuario] == password:

            st.session_state.logged_in = True
            st.session_state.usuario = usuario

            st.rerun()

        else:

            st.error(
                "❌ Usuario o contraseña incorrectos"
            )

    st.stop()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.success(
    f"Bienvenido {st.session_state.usuario}"
)

if st.sidebar.button("Cerrar sesión"):

    st.session_state.logged_in = False

    st.rerun()

# =====================================
# TÍTULO
# =====================================

st.title("🚗 Sistema de Estacionamientos")

st.caption("Monitoreo operativo de cajones para eventos")

# =====================================
# GOOGLE SHEETS
# =====================================

URL = "https://docs.google.com/spreadsheets/d/18INzmZCOKZ4z_ZmVHZ0ELVjua3MX7g3c5alOWwRl3u4/edit?gid=0#gid=0"

# =====================================
# EXTRAER NÚMEROS
# =====================================


def extraer_numero(valor):

    if pd.isna(valor):
        return 0

    numeros = re.findall(r'\d+', str(valor))

    return int(numeros[0]) if numeros else 0


# =====================================
# NORMALIZAR FECHA
# =====================================


def normalizar_fecha(fecha):

    if pd.isna(fecha):
        return ""

    fecha = str(fecha).strip()

    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y"
    ]

    for formato in formatos:

        try:

            return datetime.strptime(
                fecha,
                formato
            ).strftime("%Y-%m-%d")

        except:
            continue

    return ""


# =====================================
# NORMALIZAR HORA
# =====================================


def normalizar_hora(hora):

    if pd.isna(hora):
        return ""

    hora = str(hora).strip().upper()

    formatos = [
        "%I:%M %p",
        "%H:%M",
        "%I:%M:%S %p",
        "%H:%M:%S"
    ]

    for formato in formatos:

        try:

            return datetime.strptime(
                hora,
                formato
            ).strftime("%H:%M")

        except:
            continue

    return ""


# =====================================
# CARGAR EVENTOS
# =====================================

@st.cache_data(ttl=300)
def cargar_eventos():

    df = pd.read_csv(URL)

    df.columns = df.columns.str.strip()

    eventos = []

    for _, row in df.iterrows():

        fecha_inicio = normalizar_fecha(
            row["Fecha inicio"]
        )

        hora_inicio = normalizar_hora(
            row["Hora inicio"]
        )

        hora_fin = normalizar_hora(
            row["Hora fin"]
        )

        if fecha_inicio == "":
            continue

        if hora_inicio == "":
            continue

        if hora_fin == "":
            continue

        eventos.append({
            "fecha": fecha_inicio,
            "inicio": hora_inicio,
            "fin": hora_fin,
            "estacionamiento": str(
                row["Estacionamiento"]
            ).strip().upper(),
            "cajones": extraer_numero(
                row["Cajones"]
            ),
            "evento": str(
                row["Nombre del Evento"]
            ).strip()
        })

    return eventos


# =====================================
# CARGAR DATA
# =====================================

with st.spinner("Cargando información..."):
    eventos = cargar_eventos()

# =====================================
# FECHA
# =====================================

fecha_obj = st.date_input(
    "📅 Selecciona fecha"
)

fecha = fecha_obj.strftime("%Y-%m-%d")

# =====================================
# FILTRAR EVENTOS DEL DÍA
# =====================================


eventos_dia = []

for e in eventos:

    if e["fecha"] == fecha:
        eventos_dia.append(e)

# =====================================
# KPIs
# =====================================


total_cajones = sum(
    e["cajones"] for e in eventos_dia
)

total_eventos = len(eventos_dia)

# =====================================
# HORA PICO
# =====================================

horas = {}

for h in range(24):

    hora_texto = f"{h:02d}:00"

    horas[hora_texto] = 0

for e in eventos_dia:

    inicio = datetime.strptime(
        e["inicio"],
        "%H:%M"
    )

    fin = datetime.strptime(
        e["fin"],
        "%H:%M"
    )

    for h in range(24):

        hora_actual = datetime.strptime(
            f"{h:02d}:00",
            "%H:%M"
        )

        if inicio <= hora_actual < fin:

            horas[f"{h:02d}:00"] += e["cajones"]

hora_pico = max(
    horas,
    key=horas.get
)

valor_hora_pico = horas[hora_pico]

# =====================================
# ESTACIONAMIENTO TOP
# =====================================

uso_est = {}

for e in eventos_dia:

    est = e["estacionamiento"]

    uso_est[est] = uso_est.get(
        est,
        0
    ) + e["cajones"]

if len(uso_est) > 0:

    top_est = max(
        uso_est,
        key=uso_est.get
    )

    top_est_valor = uso_est[top_est]

else:

    top_est = "N/A"
    top_est_valor = 0

# =====================================
# KPIs VISUALES
# =====================================

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🚗 Cajones Asignados",
        total_cajones
    )

with col2:
    st.metric(
        "📅 Eventos del Día",
        total_eventos
    )

with col3:
    st.metric(
        "🕐 Hora Pico",
        hora_pico,
        f"{valor_hora_pico} cajones"
    )

with col4:
    st.metric(
        "🏆 Estacionamiento Top",
        top_est,
        f"{top_est_valor} cajones"
    )

st.divider()

# =====================================
# EVENTOS ACTIVOS
# =====================================

st.subheader("🟢 Eventos Activos Ahora")

hora_actual = datetime.now().strftime("%H:%M")

hora_actual_dt = datetime.strptime(
    hora_actual,
    "%H:%M"
)

eventos_activos = []

for e in eventos_dia:

    inicio = datetime.strptime(
        e["inicio"],
        "%H:%M"
    )

    fin = datetime.strptime(
        e["fin"],
        "%H:%M"
    )

    if inicio <= hora_actual_dt < fin:

        eventos_activos.append(e)

if len(eventos_activos) == 0:

    st.info(
        "No hay eventos activos en este momento"
    )

else:

    for e in eventos_activos:

        with st.container(border=True):

            st.markdown(
                f"### 🎫 {e['evento']}"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write(
                    f"📍 {e['estacionamiento']}"
                )

            with col2:
                st.write(
                    f"🕐 Inicio: {e['inicio']}"
                )

            with col3:
                st.write(
                    f"🕐 Fin: {e['fin']}"
                )

            with col4:
                st.write(
                    f"🚗 {e['cajones']} cajones"
                )

st.divider()

# =====================================
# TOTAL DEL DÍA
# =====================================

if st.button("📊 Total del Día"):

    resultado = {}

    for e in eventos_dia:

        est = e["estacionamiento"]

        resultado[est] = resultado.get(
            est,
            0
        ) + e["cajones"]

    st.subheader(
        "📍 Desglose por Estacionamiento"
    )

    for est in sorted(resultado):

        st.markdown(f"## 🚗 {est}")

        st.write(
            f"Total: {resultado[est]}"
        )

        st.write("---")

# =====================================
# OCUPACIÓN POR HORA
# =====================================

if st.button("📈 Ocupación por Hora"):

    estacionamientos = set()

    for e in eventos_dia:
        estacionamientos.add(
            e["estacionamiento"]
        )

    estacionamientos = sorted(
        estacionamientos
    )

    tabla = []

    for h in range(24):

        hora_texto = f"{h:02d}:00"

        fila = {
            "Hora": hora_texto
        }

        for est in estacionamientos:
            fila[est] = 0

        hora_actual = datetime.strptime(
            hora_texto,
            "%H:%M"
        )

        for e in eventos_dia:

            inicio = datetime.strptime(
                e["inicio"],
                "%H:%M"
            )

            fin = datetime.strptime(
                e["fin"],
                "%H:%M"
            )

            if inicio <= hora_actual < fin:

                fila[
                    e["estacionamiento"]
                ] += e["cajones"]

        tabla.append(fila)

    df_horas = pd.DataFrame(tabla)

    st.subheader(
        "📊 Cajones Ocupados por Hora"
    )

    st.dataframe(
        df_horas,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "📈 Gráfica por Estacionamiento"
    )

    df_chart = df_horas.set_index(
        "Hora"
    )

    st.line_chart(df_chart)