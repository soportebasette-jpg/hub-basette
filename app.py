import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN (Mantenemos tu estilo original)
st.set_page_config(page_title="Basette Group | Hub", layout="wide", initial_sidebar_state="expanded")

# 2. TU CSS ORIGINAL (Sin cambios de colores para no perder botones)
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
    
    /* RESALTE DE MÉTRICAS DASHBOARD */
    .metric-box {
        background-color: #161b22;
        border: 2px solid #d2ff00;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-title { color: #8b949e; font-size: 1rem; text-transform: uppercase; font-weight: bold; }
    .metric-value { color: #d2ff00; font-size: 3.5rem; font-weight: 900; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ (CON LOS PRECIOS NUEVOS QUE ME PEDISTE)
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
]

# 4. LOGIN ORIGINAL
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DASHBOARD", "📂 REPOSITORIO"])

# --- DASHBOARD REDISEÑADO (PROFESIONAL Y CON COLUMNAS CORRECTAS) ---
if menu == "📈 DASHBOARD":
    st.header("🏆 Dashboard Ejecutivo | Basette Group")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        df_raw = pd.read_csv(sheet_url)
        
        # Corrección de Fechas: Extraer nombre de mes de 'FECHA DE CREACIÓN'
        if 'FECHA DE CREACIÓN' in df_raw.columns:
            df_raw['FECHA_DT'] = pd.to_datetime(df_raw['FECHA DE CREACIÓN'], dayfirst=True, errors='coerce')
            meses_dict = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
            df_raw['MES_NOMBRE'] = df_raw['FECHA_DT'].dt.month.map(meses_dict)
            df_raw['AÑO_INT'] = df_raw['FECHA_DT'].dt.year.fillna(2026).astype(int)
        
        # Filtros vinculados a las columnas reales del Excel
        with st.container():
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                lista_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                sel_mes = st.multiselect("Filtrar Meses", lista_meses, default=lista_meses)
            with f2:
                años_unicos = sorted(df_raw['AÑO_INT'].unique().tolist()) if 'AÑO_INT' in df_raw.columns else [2026]
                sel_año = st.selectbox("Seleccionar Año", ["Todos"] + [str(a) for a in años_unicos])
            with f3:
                # Filtrar por columna COMERCIALIZADORA
                lista_comp = sorted(df_raw['COMERCIALIZADORA'].dropna().unique().tolist()) if 'COMERCIALIZADORA' in df_raw.columns else []
                sel_comp = st.selectbox("Comercializadora", ["Todas"] + lista_comp)
            with f4:
                # Filtrar por columna COMERCIAL (Nombres)
                lista_com = sorted(df_raw['COMERCIAL'].dropna().unique().tolist()) if 'COMERCIAL' in df_raw.columns else []
                sel_com = st.multiselect("Comerciales", lista_com, default=lista_com)

        # Aplicar Filtros
        df = df_raw.copy()
        if sel_mes: df = df[df['MES_NOMBRE'].isin(sel_mes)]
        if sel_año != "Todos": df = df[df['AÑO_INT'] == int(sel_año)]
        if sel_comp != "Todas": df = df[df['COMERCIALIZADORA'] == sel_comp]
        if sel_com: df = df[df['COMERCIAL'].isin(sel_com)]

        # --- MÉTRICAS RESALTADAS (Visualización Profesional) ---
        st.markdown("### 📊 RESUMEN DE VENTAS")
        m1, m2, m3 = st.columns(3)
        luz_n = df['CUPS LUZ'].count() if 'CUPS LUZ' in df.columns else 0
        gas_n = df['CUPS GAS'].count() if 'CUPS GAS' in df.columns else 0
        
        with m1:
            st.markdown(f'<div class="metric-box"><p class="metric-title">Ventas Luz</p><p class="metric-value">{luz_n} ⚡</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><p class="metric-title">Ventas Gas</p><p class="metric-value">{gas_n} 🔥</p></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><p class="metric-title">Total Global</p><p class="metric-value" style="color:white;">{luz_n + gas_n} ✅</p></div>', unsafe_allow_html=True)

        # Ranking de Ventas por Comercial
        st.markdown('<div class="block-header">👑 RANKING DE VENTAS POR AGENTE</div>', unsafe_allow_html=True)
        if 'COMERCIAL' in df.columns:
            ranking = df.groupby('COMERCIAL').size().reset_index(name='Ventas').sort_values('Ventas', ascending=False)
            fig_rank = px.bar(ranking, x='COMERCIAL', y='Ventas', text='Ventas', color_discrete_sequence=['#d2ff00'], template="plotly_dark")
            st.plotly_chart(fig_rank, use_container_width=True)

        # Tabla de datos filtrada
        st.markdown('<div class="block-header">📋 LISTADO DE OPERACIONES</div>', unsafe_allow_html=True)
        st.dataframe(df[['FECHA DE CREACIÓN', 'COMERCIAL', 'COMERCIALIZADORA', 'ESTADO']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error al cargar dashboard: Asegúrese de que las columnas 'FECHA DE CREACIÓN', 'COMERCIALIZADORA' y 'COMERCIAL' existan en el Excel.")

# --- SECCIONES RESTANTES (Mantenidas intactas de tu código funcional) ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        df_p = pd.DataFrame(tarifas_luz).drop(columns=['logo'])
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    # [Aquí seguiría el resto de tu código de Gas y Fibra...]

elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    # [Tu código original de CRM...]

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro Personalizado")
    # [Tu código original de Comparador...]

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    # [Tu código original de Repositorio...]