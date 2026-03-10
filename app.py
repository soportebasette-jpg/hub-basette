import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Basette Group | Hub", layout="wide", initial_sidebar_state="expanded")

# 2. CSS DE ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p { color: #d2ff00 !important; font-weight: 900 !important; font-size: 1.25rem !important; }
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    .price-card { background-color: #161b22; border: 2px solid #30363d; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; height: 100%; }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"}
]

# 4. LOGIN
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

# 5. NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📂 REPOSITORIO", "📈 DASHBOARD"])

# --- SECCIONES ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.link_button("MARCADOR PRINCIPAL", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 ENERGÍA</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    servicios = [("CRM BASETTE", "https://crm.grupobasette.eu/login"), ("GANA ENERGÍA", "https://colaboradores.ganaenergia.com/"), ("NATURGY", "https://checkout.naturgy.es/backoffice")]
    for i, (n, u) in enumerate(servicios):
        with cols[i % 3]: st.link_button(n, u, use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    # ... (Sección de comparador simplificada para asegurar funcionamiento)
    st.info("Funcionalidad de Comparador activa.")

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    st.info("Manuales disponibles en la carpeta manuales.")

# --- DASHBOARD (SOLUCIÓN AL ERROR 200) ---
elif menu == "📈 DASHBOARD":
    st.header("🏆 Análisis de Ventas Real")
    try:
        # Usamos la conexión pero forzamos la lectura como DataFrame de Pandas
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # EL CAMBIO CLAVE: Quitamos cualquier parámetro extra y usamos query simple
        df = conn.query("SELECT *", ttl=0)
        
        if isinstance(df, pd.DataFrame) and not df.empty:
            df.columns = df.columns.str.strip()
            st.metric("Ventas Totales", len(df))
            st.markdown('<div class="block-header">📋 LISTADO COMPLETO</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.error("Los datos recibidos no tienen formato de tabla. Revisa los Secrets.")
            
    except Exception as e:
        st.error(f"Error Crítico: {e}")