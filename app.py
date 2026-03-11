import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD (MEJORADO)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* Resaltado de etiquetas de los filtros */
    label[data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        background-color: #d2ff00 !important;
        padding: 5px 15px !important;
        border-radius: 5px !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
    }
    
    /* Estilo de métricas Premium */
    [data-testid="stMetricValue"] { 
        font-size: 3rem !important; 
        font-weight: 900 !important; 
        color: black !important;
    }
    [data-testid="stMetricLabel"] p { 
        color: #333333 !important; 
        font-size: 1.1rem !important; 
        font-weight: bold !important; 
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #d2ff00 0%, #afff00 100%);
        border-radius: 15px;
        padding: 20px;
        border: None;
        box-shadow: 0px 8px 20px rgba(210, 255, 0, 0.4);
        text-align: center;
    }

    /* Botones y otros */
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    .block-header {
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATOS LUZ (IGUAL)
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,163/0,096/0,072", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"}
]

# 4. LOGIN (IGUAL)
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

# --- DASHBOARD SECCIÓN ---
if menu == "📈 DASHBOARD":
    st.header("🏆 Dashboard Ejecutivo | Basette Group")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        df_raw = pd.read_csv(sheet_url)
        df_raw['Fecha Creación'] = pd.to_datetime(df_raw['Fecha Creación'], errors='coerce')
        
        meses_traduccion = {
            "Enero": "January", "Febrero": "February", "Marzo": "March", "Abril": "April",
            "Mayo": "May", "Junio": "June", "Julio": "July", "Agosto": "August",
            "Septiembre": "September", "Octubre": "October", "Noviembre": "November", "Diciembre": "December"
        }
        
        df_raw['MES_NOMBRE'] = df_raw['Fecha Creación'].dt.month_name()
        df_raw['AÑO'] = df_raw['Fecha Creación'].dt.year
        df_raw['Venta_Luz'] = df_raw['CUPS Luz'].notna().astype(int)
        df_raw['Venta_Gas'] = df_raw['CUPS Gas'].notna().astype(int)
        df_raw['TOTAL_VENTAS'] = df_raw['Venta_Luz'] + df_raw['Venta_Gas']

        # FILTROS
        f1, f2, f3, f4 = st.columns(4)
        with f1: sel_mes_esp = st.selectbox("Mes", ["Todos"] + list(meses_traduccion.keys()))
        with f2:
            años_disponibles = sorted(list(df_raw['AÑO'].dropna().unique().astype(int)), reverse=True)
            sel_año = st.selectbox("Año", ["Todos"] + [str(a) for a in años_disponibles])
        with f3:
            comercializadoras = ["Todas"] + sorted(list(df_raw['Comercializadora'].dropna().unique()))
            sel_comp = st.selectbox("Compañía", comercializadoras)
        with f4:
            comerciales = ["Todos"] + sorted(list(df_raw['Comercial'].dropna().unique()))
            sel_com = st.selectbox("Comercial", comerciales)

        df = df_raw.copy()
        if sel_mes_esp != "Todos": df = df[df['MES_NOMBRE'] == meses_traduccion[sel_mes_esp]]
        if sel_año != "Todos": df = df[df['AÑO'] == int(sel_año)]
        if sel_comp != "Todas": df = df[df['Comercializadora'] == sel_comp]
        if sel_com != "Todos": df = df[df['Comercial'] == sel_com]

        # --- MÉTRICAS RESALTADAS ---
        st.markdown('<div class="block-header">📊 RESUMEN DE CIFRAS</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        total_luz = df['Venta_Luz'].sum()
        total_gas = df['Venta_Gas'].sum()
        total_global = df['TOTAL_VENTAS'].sum()
        m1.metric("VENTAS LUZ", f"{total_luz} ⚡")
        m2.metric("VENTAS GAS", f"{total_gas} 🔥")
        m3.metric("TOTAL GLOBAL", f"{total_global} ✅")

        # --- GRÁFICOS ---
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown('<div class="block-header">👑 RANKING POR COMERCIAL</div>', unsafe_allow_html=True)
            if not df.empty:
                ranking = df.groupby('Comercial').agg(Luz=('Venta_Luz', 'sum'), Gas=('Venta_Gas', 'sum'), Total=('TOTAL_VENTAS', 'sum')).reset_index().sort_values(by='Total', ascending=False)
                fig_ranking = px.bar(ranking, x='Comercial', y=['Luz', 'Gas'], color_discrete_map={'Luz': '#d2ff00', 'Gas': '#ffffff'}, template="plotly_dark", barmode='stack')
                st.plotly_chart(fig_ranking, use_container_width=True)
            else: st.warning("No hay datos")

        with col_g2:
            st.markdown('<div class="block-header">🏢 VENTAS POR COMPAÑÍA (%)</div>', unsafe_allow_html=True)
            if not df.empty:
                df_comp = df.groupby('Comercializadora')['TOTAL_VENTAS'].sum().reset_index()
                fig_pie = px.pie(df_comp, values='TOTAL_VENTAS', names='Comercializadora', 
                                 hole=0.4, color_discrete_sequence=['#d2ff00', '#ffffff', '#555555', '#333333'],
                                 template="plotly_dark")
                fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
                st.plotly_chart(fig_pie, use_container_width=True)
            else: st.warning("Sin datos de compañías")

        # --- TABLA ---
        st.markdown('<div class="block-header">📋 DETALLE DE OPERACIONES</div>', unsafe_allow_html=True)
        st.dataframe(df[['Fecha Creación', 'Estado', 'Comercial', 'Comercializadora', 'Cliente', 'CUPS Luz', 'CUPS Gas']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error: {e}")

# --- RESTO DE SECCIONES (IGUAL) ---
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    # (Resto de tu código CRM...)
elif menu == "📊 PRECIOS":
    st.header("Tarifario")
    # (Resto de tu código Precios...)
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    # (Resto de tu código Comparador...)
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    # (Resto de tu código Repositorio...)