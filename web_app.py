import streamlit as st

st.set_page_config(
    page_title="Sistema",
    layout="wide"
)

# =====================================
# LOGIN SIMPLE
# =====================================

USUARIOS = {
    "azael": "azael123"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login")

    usuario = st.text_input("Usuario")

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Entrar"):

        if usuario in USUARIOS and USUARIOS[usuario] == password:

            st.session_state.logged_in = True

            st.rerun()

        else:

            st.error("Credenciales incorrectas")

    st.stop()

# =====================================
# SISTEMA
# =====================================

st.success("✅ LOGIN CORRECTO")

st.title("🚗 Sistema funcionando")