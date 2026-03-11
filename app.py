import streamlit as st
import os
import pandas as pd
import plotly.express as px  # Librería para gráficos automáticos
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. DISEÑO CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    button p, .stDownloadButton button p, .stButton button p { 
        color: #000000 !important; 
        font-weight: 900 !important; 
    }
    button, .stDownloadButton button, .stButton button { 
        background-color: #ffffff !important; 
        border: 2px solid #d2ff00 !important; 
    }
    .block-header {
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ (Tarifas)
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,163/0,096/0,072", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DASHBOARD", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- LÓGICA DE DASHBOARD AUTOMÁTICO CON PYTHON ---
if menu == "📈 DASHBOARD":
    st.header("🏆 Dashboard Automático de Ventas")
    st.markdown('<div class="block-header">📊 ANÁLISIS GENERADO POR PYTHON</div>', unsafe_allow_html=True)

    # URL de tu Google Sheets en formato CSV para que Python lo lea directo
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        df = pd.read_csv(sheet_url)
        
        # 1. MÉTRICAS RÁPIDAS
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Ventas", len(df))
        if 'ESTADO' in df.columns:
            c2.metric("Ventas Firmadas", len(df[df['ESTADO'] == 'FIRMADA']))
        
        # 2. GRÁFICO DE BARRAS (Ventas por Agente) - AUTOMÁTICO
        st.subheader("Ventas por Agente")
        col_agente = 'AGENTE' if 'AGENTE' in df.columns else df.columns[0] # Detecta columna
        fig_bar = px.bar(df, x=col_agente, title="Rendimiento del Equipo", color=col_agente, template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

        # 3. GRÁFICO CIRCULAR (Distribución)
        st.subheader("Distribución de Estados")
        col_estado = 'ESTADO' if 'ESTADO' in df.columns else df.columns[-1]
        fig_pie = px.pie(df, names=col_estado, hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.success("✅ Datos actualizados desde Google Sheets correctamente.")

    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        st.info("Asegúrate de que el Google Sheets tenga el acceso compartido para 'Cualquier persona con el enlace'.")

# --- CRM (Resto del código igual) ---
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    # ... (Aquí va el resto de tu código CRM que ya tenías)

# (Añade aquí las secciones de PRECIOS, COMPARADOR y REPOSITORIO que ya tenías)