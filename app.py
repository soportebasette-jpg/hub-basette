import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime, time, date
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

# Rutas de imágenes solicitadas
RUTA_LOGO_BASSETTE = r"C:\Users\Propietario\Desktop\MI_INTRANET\LOGO BASETTE GRUO EUROPA SL.jpg"
RUTA_LOGO_TECOMPAROTODO = r"C:\Users\Propietario\Desktop\MI_INTRANET\tecomparotodo_logo.jpg"

# Función para convertir imagen a base64 (Mantenida de tu original)
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

def normalizar(texto):
    if not isinstance(texto, str): return ""
    texto = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto if unicodedata.category(c) != 'Mn']).strip().upper()

# --- DATOS CONTROL LABORAL (AÑADIDO) ---
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
    </style>
    """, unsafe_allow_html=True)

# 3. SISTEMA DE ACCESO (LOGOTIPO BASSETTE Y CLAVE Ventas2024*)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(RUTA_LOGO_BASSETTE):
            st.image(Image.open(RUTA_LOGO_BASSETTE), use_container_width=True)
        st.title("🔒 Acceso Basette Hub")
        pwd = st.text_input("Introduce la contraseña", type="password")
        if st.button("ENTRAR"):
            if pwd == "Ventas2024*":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    st.stop()

# --- SIDEBAR (TU MENÚ ORIGINAL + CONTROL LABORAL) ---
with st.sidebar:
    if os.path.exists(RUTA_LOGO_BASSETTE):
        st.image(Image.open(RUTA_LOGO_BASSETTE))
    st.markdown("---")
    menu = st.radio(
        "NAVEGACIÓN",
        ["📊 DASHBOARD VENTAS", "📢 ANUNCIOS", "🔗 CRM", "💰 PRECIOS", "⚖️ COMPARADOR", "📂 REPOSITORIO", "🕒 CONTROL LABORAL"],
        index=0
    )
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

# --- LÓGICA DE LAS PESTAÑAS (TODO TU CÓDIGO ORIGINAL) ---

if menu == "📊 DASHBOARD VENTAS":
    st.title("🚀 Panel de Control de Ventas")
    try:
        sheet_id = "1nC_rA571-R5_x6S7Ube33W89pE3N3q9L2p5N7H-Yc8Q"
        url_v = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        dv = pd.read_csv(url_v)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL VENTAS", len(dv))
        c2.metric("FIBRA/MOVIL", len(dv[dv['Producto'].isin(['FIBRA', 'MOVIL', 'CONVERGENTE'])]))
        if 'V_Alarma' in dv.columns:
            c3.metric("ALARMAS", int(dv['V_Alarma'].sum()))
        c4.metric("ENERGÍA", len(dv[dv['Producto'] == 'LUZ/GAS']))

        t1, t2 = st.tabs(["Análisis por Comercial", "Ventas Alarmas"])
        with t1:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.plotly_chart(px.pie(dv, names='Comercial', title="Reparto de Ventas", hole=0.4), use_container_width=True)
            with col_v2:
                st.plotly_chart(px.bar(dv, x='Producto', color='Comercial', title="Productos", barmode='group'), use_container_width=True)
        with t2:
            if 'V_Alarma' in dv.columns:
                da = dv[dv['V_Alarma'] > 0]
                st.plotly_chart(px.pie(da, names='Comercial', values='V_Alarma', title="% Alarmas", hole=0.4), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

elif menu == "📢 ANUNCIOS":
    st.title("📢 Tablón de Anuncios")
    st.info("No hay anuncios nuevos hoy.")

elif menu == "🔗 CRM":
    st.title("🔗 Acceso Directo a CRM")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("[![CRM 1](https://img.shields.io/badge/ACCESO-CRM_PRO-blue?style=for-the-badge)](https://www.google.com)") # Cambia por tus links
    with col_c2:
        st.markdown("[![CRM 2](https://img.shields.io/badge/ACCESO-CRM_VENTAS-green?style=for-the-badge)](https://www.google.com)")

elif menu == "💰 PRECIOS":
    st.title("💰 Consulta de Precios")
    st.info("Sección de tarifas originales.")

elif menu == "⚖️ COMPARADOR":
    st.title("⚖️ Comparador de Servicios")
    st.info("Sección de comparativa original.")

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 MANUALES"):
        st.write("Contenido del repositorio original.")

# --- NUEVA PESTAÑA: CONTROL LABORAL ---
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
    else:
        st.warning("No hay datos en el Google Sheet de laboral.")