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

# 1. CONFIGURACIÓN ORIGINAL
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- FUNCIONES DE APOYO CRM ---
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

# --- DATOS CONTROL LABORAL ---
festivos_2026 = ["2026-01-01", "2026-01-06", "2026-02-28", "2026-04-02", "2026-04-03", "2026-04-22", "2026-05-01", "2026-06-04", "2026-08-15", "2026-10-12", "2026-11-02", "2026-12-07", "2026-12-08", "2026-12-25"]
fechas_empresa = {
    'LUIS RODRÍGUEZ': {'alta': date(2026, 4, 8), 'baja': None},
    'RAQUEL GUADALUPE': {'alta': date(2026, 3, 19), 'baja': None},
    'LORENA POZO': {'alta': date(2026, 3, 18), 'baja': None},
    'DEBORAH RODRIGUEZ': {'alta': date(2026, 3, 18), 'baja': None},
    'BELÉN TRONCOSO': {'alta': date(2026, 3, 18), 'baja': None},
    'MACARENA BACA': {'alta': date(2026, 3, 18), 'baja': date(2026, 3, 20)}
}
excepciones_laboral = {'LORENA POZO': {date(2026, 4, 17): "Día libre por objetivo conseguido"}}
recuperadas_manual = {'LORENA POZO': 2.0, 'BELÉN TRONCOSO': 3.33, 'DEBORAH RODRIGUEZ': 0.5}

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

# 2. CSS ORIGINAL
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p { color: #d2ff00 !important; font-weight: 900 !important; font-size: 1.25rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN ORIGINAL (REPARADO)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists("rosco.jpg"):
            st.image("rosco.jpg", use_container_width=True)
        st.title("🔒 Acceso Basette Hub")
        pwd = st.text_input("Introduce la contraseña", type="password")
        if st.button("ENTRAR"):
            if pwd == "Basette2025":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    st.stop()

# --- SI ESTÁ AUTENTICADO ---
with st.sidebar:
    if os.path.exists("rosco.jpg"):
        st.image("rosco.jpg")
    st.markdown("---")
    menu = st.radio("NAVEGACIÓN", ["📊 DASHBOARD VENTAS", "🕒 CONTROL LABORAL", "📂 REPOSITORIO"])
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

# PESTAÑA 1: VENTAS
if menu == "📊 DASHBOARD VENTAS":
    st.title("🚀 Panel de Control de Ventas")
    try:
        sheet_id = "1nC_rA571-R5_x6S7Ube33W89pE3N3q9L2p5N7H-Yc8Q"
        url_v = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        dv = pd.read_csv(url_v)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL VENTAS", len(dv))
        c2.metric("FIBRA/MOVIL", len(dv[dv['Producto'].isin(['FIBRA', 'MOVIL', 'CONVERGENTE'])]))
        if 'V_Alarma' in dv.columns: c3.metric("ALARMAS", int(dv['V_Alarma'].sum()))
        c4.metric("ENERGÍA", len(dv[dv['Producto'] == 'LUZ/GAS']))
        
        t1, t2 = st.tabs(["Análisis Comercial", "Ventas Alarmas"])
        with t1:
            col_a, col_b = st.columns(2)
            with col_a: st.plotly_chart(px.pie(dv, names='Comercial', hole=0.4), use_container_width=True)
            with col_b: st.plotly_chart(px.bar(dv, x='Producto', color='Comercial', barmode='group'), use_container_width=True)
    except Exception as e: st.error(f"Error: {e}")

# PESTAÑA 2: LABORAL (CON LOGO INDEPENDIENTE)
elif menu == "🕒 CONTROL LABORAL":
    df_raw_lab = load_data_laboral()
    comercial_lab = st.sidebar.selectbox("Seleccionar Comercial", sorted(list(fechas_empresa.keys())))
    meses_lab = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_lab = st.sidebar.selectbox("Mes", meses_lab, index=datetime.now().month - 1)
    
    # Cálculo de horas...
    dias_mes = [date(2026, (meses_lab.index(mes_lab)+1), d) for d in range(1, calendar.monthrange(2026, (meses_lab.index(mes_lab)+1))[1] + 1) 
                if date(2026, (meses_lab.index(mes_lab)+1), d).weekday() < 5 and date(2026, (meses_lab.index(mes_lab)+1), d).strftime("%Y-%m-%d") not in festivos_2026]
    df_lab_f = pd.DataFrame({'Fecha': dias_mes})
    
    def calc_lab(row):
        f = row['Fecha']; info = fechas_empresa[comercial_lab]; excep = excepciones_laboral.get(comercial_lab, {})
        dia_data = df_raw_lab[(df_raw_lab['Nombre_Norm'] == normalizar(comercial_lab)) & (df_raw_lab['Fecha'] == f)] if not df_raw_lab.empty else pd.DataFrame()
        v_h = 4.5 if (date(2026, 4, 20) <= f <= date(2026, 4, 26)) else (8.0 if comercial_lab == 'RAQUEL GUADALUPE' else 5.0)
        e, s = "-", "-"
        for _, r in dia_data.iterrows():
            if "ENTRADA" in r['Accion_Norm']: e = r['Hora_f']
            if "SALIDA" in r['Accion_Norm']: s = r['Hora_f']
        ausencia = excep[f] if f in excep else ("SI pendiente recuperar" if e == "-" and f <= date.today() else "-")
        return pd.Series([e.strftime("%H:%M") if isinstance(e, time) else "-", s.strftime("%H:%M") if isinstance(s, time) else "-", ausencia, v_h])

    df_lab_f[['ENTRADA', 'SALIDA', 'AUSENCIA', 'Jornada_h']] = df_lab_f.apply(calc_lab, axis=1)
    
    # CABECERA LABORAL
    cl1, cl2, cl3 = st.columns([2, 3, 2.5])
    with cl1:
        # LOGO ESPECÍFICO DE LABORAL
        ruta_logo_lab = r"C:\Users\Propietario\Desktop\MI_INTRANET\tecomparotodo_logo.jpg"
        if os.path.exists(ruta_logo_lab): st.image(Image.open(ruta_logo_lab), width=220)
    with cl2: st.markdown(f"<h1 style='text-align: center; color: #d2ff00;'>{comercial_lab}</h1>", unsafe_allow_html=True)
    with cl3: st.metric("HORAS A RECUPERAR", "Calculando...")
    
    st.divider()
    st.dataframe(df_lab_f, use_container_width=True)

# PESTAÑA 3: REPOSITORIO
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("MANUALES"):
        st.write("Archivos disponibles en /manuales")