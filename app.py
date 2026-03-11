import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Basette Group | Hub Profesional", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. ESTILOS CSS PROFESIONALES
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    
    /* Tarjetas de Métricas Dashboard */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(210, 255, 0, 0.3);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #d2ff00;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b949e;
    }

    /* Estilos Generales */
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: bold !important;
    }
    .block-header {
        background: linear-gradient(90deg, #d2ff00 0%, #161b22 100%);
        color: black;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        margin: 20px 0;
    }
    .stDataFrame { background-color: #161b22; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ (CON PRECIOS ACTUALIZADOS GANA ENERGÍA)
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"}
]

# 4. SISTEMA DE ACCESO
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

# 5. NAVEGACIÓN LATERAL
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("MENÚ PRINCIPAL", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DASHBOARD", "📂 REPOSITORIO"])

# --- SECCIÓN DASHBOARD (RECONSTRUIDA) ---
if menu == "📈 DASHBOARD":
    st.title("🏆 Panel de Control de Ventas | Basette Group")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        df_raw = pd.read_csv(sheet_url)
        
        # Procesamiento de Fechas y Nombres
        if 'FECHA DE CREACIÓN' in df_raw.columns:
            df_raw['FECHA_DT'] = pd.to_datetime(df_raw['FECHA DE CREACIÓN'], dayfirst=True, errors='coerce')
            meses_es = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 
                        7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
            df_raw['MES_NOMBRE'] = df_raw['FECHA_DT'].dt.month.map(meses_es)
            df_raw['AÑO'] = df_raw['FECHA_DT'].dt.year

        # --- FILTROS SUPERIORES ---
        with st.expander("🔍 FILTROS AVANZADOS", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                meses_disponibles = sorted(df_raw['MES_NOMBRE'].dropna().unique().tolist())
                sel_mes = st.multiselect("Mes", meses_disponibles, default=meses_disponibles)
            with c2:
                años_disp = sorted(df_raw['AÑO'].dropna().unique().astype(int).tolist())
                sel_año = st.selectbox("Año", ["Todos"] + años_disp)
            with c3:
                lista_comp = sorted(df_raw['COMERCIALIZADORA'].dropna().unique().tolist())
                sel_comp = st.selectbox("Comercializadora", ["Todas"] + lista_comp)
            with c4:
                lista_com = sorted(df_raw['COMERCIAL'].dropna().unique().tolist())
                sel_com = st.multiselect("Comercial (Agente)", lista_com, default=lista_com)

        # Aplicar Filtros
        df = df_raw.copy()
        if sel_mes: df = df[df['MES_NOMBRE'].isin(sel_mes)]
        if sel_año != "Todos": df = df[df['AÑO'] == int(sel_año)]
        if sel_comp != "Todas": df = df[df['COMERCIALIZADORA'] == sel_comp]
        if sel_com: df = df[df['COMERCIAL'].isin(sel_com)]

        # --- SECCIÓN DE MÉTRICAS RESALTADAS ---
        st.markdown('<div class="block-header">📊 RENDIMIENTO GLOBAL</div>', unsafe_allow_html=True)
        kpi1, kpi2, kpi3 = st.columns(3)
        
        luz_total = df['CUPS LUZ'].count()
        gas_total = df['CUPS GAS'].count()
        total_global = luz_total + gas_total

        with kpi1:
            st.markdown(f'<div class="metric-card"><p class="metric-label">Ventas Luz</p><p class="metric-value">{luz_total} ⚡</p></div>', unsafe_allow_html=True)
        with kpi2:
            st.markdown(f'<div class="metric-card"><p class="metric-label">Ventas Gas</p><p class="metric-value">{gas_total} 🔥</p></div>', unsafe_allow_html=True)
        with kpi3:
            st.markdown(f'<div class="metric-card"><p class="metric-label">Total Operaciones</p><p class="metric-value" style="color:#ffffff;">{total_global} ✅</p></div>', unsafe_allow_html=True)

        # --- GRÁFICO DE RANKING ---
        st.markdown('<div class="block-header">👑 RANKING POR AGENTE</div>', unsafe_allow_html=True)
        ranking = df.groupby('COMERCIAL').size().reset_index(name='Ventas').sort_values('Ventas', ascending=False)
        fig = px.bar(ranking, x='COMERCIAL', y='Ventas', text='Ventas', 
                     color_discrete_sequence=['#d2ff00'], template="plotly_dark")
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_title="Agente Comercial", yaxis_title="Contratos")
        st.plotly_chart(fig, use_container_width=True)

        # --- TABLA DE DATOS ---
        st.markdown('<div class="block-header">📋 DETALLE DE OPERACIONES</div>', unsafe_allow_html=True)
        st.dataframe(df[['FECHA DE CREACIÓN', 'COMERCIAL', 'COMERCIALIZADORA', 'ESTADO']], use_container_width=True)

    except Exception as e:
        st.error(f"Error de configuración: Asegúrese de que el Excel tiene las columnas 'FECHA DE CREACIÓN', 'COMERCIALIZADORA' y 'COMERCIAL'.")

# --- RESTO DE SECCIONES (IGUAL QUE EL CÓDIGO ANTERIOR) ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True)
    # ... (Resto del código de precios, CRM y comparador igual al anterior)