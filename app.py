import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="Basette Group | Hub", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p { color: #d2ff00 !important; font-weight: 900 !important; font-size: 1.25rem !important; }
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
        pwd = st.text_input("Introduce Clave Comercial:", type="password")
        if st.button("ACCEDER AL HUB"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📂 REPOSITORIO", "📈 DASHBOARD"], label_visibility="collapsed")

# --- REPOSITORIO (Arregla el UnicodeDecodeError) ---
if menu == "📂 REPOSITORIO":
    st.header("Documentación")
    docs = ["ARGUMENTARIO_ENERGÍA (Venta Fría) + Venta Cruzada Teleco.docx", 
            "ARGUMENTARIO_TELECO (Clientes Movistar a O2) + Venta Cruzada Energía.docx"]
    for d in docs:
        path = f"manuales/{d}"
        if os.path.exists(path):
            with open(path, "rb") as f: # "rb" arregla el error de tu captura
                st.download_button(f"📘 {d}", f, file_name=d, key=path)

# --- DASHBOARD (Arregla el error de conexión y el error de Localhost) ---
elif menu == "📈 DASHBOARD":
    st.header("🏆 Análisis de Ventas")
    try:
        # ttl=0 evita que Streamlit use caché vieja que rompe la conexión en local
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0) 
        if df is not None:
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No se pudo leer la hoja. Revisa el nombre de la pestaña.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# (Mantén el resto de tus secciones CRM, PRECIOS y COMPARADOR igual)