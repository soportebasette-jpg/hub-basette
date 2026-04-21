import streamlit as st
import os
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime, time, date
import calendar
import unicodedata
from PIL import Image  # <--- ESTA ES LA CLAVE

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Basette Group | Hub", layout="wide")

# --- FUNCIONES ---
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

# --- DATOS LABORAL ---
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

# --- CSS ---
st.markdown("<style>.stApp { background-color: #0d1117; color: white; } label p { color: #d2ff00 !important; font-weight: 900; }</style>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("MENU")
    menu = st.radio("NAVEGACIÓN", ["📊 DASHBOARD", "🕒 LABORAL", "📂 REPOS"])

# --- LÓGICA PESTAÑAS ---
if menu == "📊 DASHBOARD":
    st.title("DASHBOARD")
    st.info("Cargando datos de ventas...")

elif menu == "🕒 LABORAL":
    df_raw = load_data_laboral()
    col_l1, col_l2 = st.columns([1, 2])
    
    with col_l1:
        # AQUÍ ESTABA EL ERROR: Aseguramos la ruta
        ruta_logo = r"C:\Users\Propietario\Desktop\MI_INTRANET\tecomparotodo_logo.jpg"
        if os.path.exists(ruta_logo):
            img = Image.open(ruta_logo) # Ya no fallará porque importamos Image arriba
            st.image(img, width=200)
        else:
            st.write("Logo no encontrado")
    
    with col_l2:
        comercial = st.selectbox("Comercial", list(fechas_empresa.keys()))
        st.header(f"Control de {comercial}")

elif menu == "📂 REPOS":
    st.write("Repositorio de archivos")