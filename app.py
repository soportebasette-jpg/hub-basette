import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime, time, date # Añadido date y time para evitar el error
import calendar
import unicodedata
from fpdf import FPDF
from PIL import Image

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Definición de rutas para que no den error (Asegúrate de que existan)
RUTA_LOGO_BASSETTE = r"C:\Users\Propietario\Desktop\MI_INTRANET\LOGO BASETTE GRUO EUROPA SL.jpg"
RUTA_LOGO_TECOMPAROTODO = r"C:\Users\Propietario\Desktop\MI_INTRANET\tecomparotodo_logo.jpg"

# Función para convertir imagen a base64 (Tu original)
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Preparamos la imagen de Rosco (Tu original)
img_base64 = get_base64_of_bin_file("rosco.jpg")

# --- FUNCIONES Y DATOS CONTROL LABORAL ---
def normalizar(texto):
    if not isinstance(texto, str): return ""
    texto = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto if unicodedata.category(c) != 'Mn']).strip().upper()

festivos_2026 = ["2026-01-01", "2026-01-06", "2026-02-28", "2026-04-02", "2026-04-03", "2026-04-22", "2026-05-01", "2026-06-04", "2026-08-15", "2026-10-12", "2026-11-02", "2026-12-07", "2026-12-08", "2026-12-25"]
fechas_empresa = {
    'LUIS RODRÍGUEZ': {'alta': date(2026, 4, 8), 'baja': None},
    'RAQUEL GUADALUPE': {'alta': date(2026, 3, 19), 'baja': None},
    'LORENA POZO': {'alta': date(2026, 3, 18), 'baja': None},
    'DEBORAH RODRIGUEZ': {'alta': date(2026, 3, 18), 'baja': None},
    'BELÉN TRONCOSO': {'alta': date(2026, 3, 18), 'baja': None},
    'MACARENA BACA': {'alta': date(2026, 3, 18), 'baja': date(2026, 3, 20)}
}

@st.cache_data(ttl=5)
def load_data_laboral():
    url = "https://docs.google.com/spreadsheets/d/175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY/export?format=csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], dayfirst=True, errors='coerce')
        df['Nombre_Norm'] = df['¿Quién eres?'].apply(normalizar)
        df['Accion_Norm'] = df['¿Qué vas a hacer?'].astype(str).str.upper()
        df['Fecha'] = df['Marca temporal'].dt.date
        df['Hora_f'] = df['Marca temporal'].dt.time
        return df.dropna(subset=['Marca temporal'])
    except: return pd.DataFrame()

# 2. CSS DE ALTA VISIBILIDAD (TU ORIGINAL)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. LOGIN (CON TU CONTRASEÑA Ventas2024*)
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists(RUTA_LOGO_BASSETTE): st.image(RUTA_LOGO_BASSETTE)
        pwd = st.text_input("Introduce Clave Comercial:", type="password")
        if st.button("ACCEDER AL HUB"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# 5. NAVEGACIÓN (CON EL MENÚ QUE PEDISTE)
with st.sidebar:
    if os.path.exists(RUTA_LOGO_BASSETTE): st.image(RUTA_LOGO_BASSETTE)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO", "🕒 CONTROL LABORAL"])

# --- AQUÍ VA TODO TU CÓDIGO ORIGINAL DE CADA SECCIÓN ---
if menu == "🚀 CRM":
    # (Aquí iría tu bloque de CRM original...)
    st.header("Portales de Gestión")
    # ... resto de tu código de CRM ...

elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    # ... resto de tu código de Precios ...

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro Personalizado")
    # ... resto de tu código de Comparador ...

elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("Anuncios")
    # ... resto de tu código de Anuncios ...

elif menu == "📈 DASHBOARD Y RANKING":
    st.header("Dashboard")
    # ... resto de tu código de Dashboard ...

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    # ... resto de tu código de Repositorio ...

# --- SECCIÓN NUEVA: CONTROL LABORAL ---
elif menu == "🕒 CONTROL LABORAL":
    df_lab = load_data_laboral()
    comercial_sel = st.sidebar.selectbox("Seleccionar Comercial", sorted(list(fechas_empresa.keys())))
    
    col_l1, col_l2 = st.columns([1, 3])
    with col_l1:
        if os.path.exists(RUTA_LOGO_TECOMPAROTODO):
            st.image(Image.open(RUTA_LOGO_TECOMPAROTODO), width=220)
    with col_l2:
        st.markdown(f"<h1 style='color: #d2ff00;'>{comercial_sel}</h1>", unsafe_allow_html=True)
    
    st.divider()
    if not df_lab.empty:
        df_indiv = df_lab[df_lab['Nombre_Norm'] == normalizar(comercial_sel)]
        st.dataframe(df_indiv, use_container_width=True)