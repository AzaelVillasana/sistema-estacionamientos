import streamlit as st

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Sistema de Estacionamientos",
    layout="wide"
)

# =====================================
# USUARIOS
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
# SISTEMA
# =====================================

st.title("🚗 Sistema de Estacionamientos")

st.success("✅ Login funcionando correctamente")

st.write(
    "Aquí ya iría todo tu dashboard."
)