import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN DE INTERFAZ
st.set_page_config(page_title="Basette Group | Hub", layout="wide", initial_sidebar_state="expanded")

# 2. ESTILOS CSS (Tu estilo original + Resalte de métricas)
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
    
    /* TARJETAS DE PRECIOS FIBRA */
    .price-card { background-color: #161b22; border: 2px solid #30363d; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; height: 100%; }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.85rem; }

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

# 3. BASE DE DATOS LUZ (PRECIOS ACTUALIZADOS)
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
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

# 5. MENÚ LATERAL
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DASHBOARD", "📂 REPOSITORIO"])

# --- SECCIÓN 🚀 CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button("MARCADOR PRINCIPAL (VOZIP)", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [
        {"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, 
        {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, 
        {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, 
        {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/"},
        {"n": "ENDESA", "u": "https://inergia.app"}
    ]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.link_button(p["n"], p["u"], use_container_width=True)

# --- SECCIÓN 📊 PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([
            {"COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"},
            {"COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        fm_cols = st.columns(3)
        with fm_cols[0]: st.markdown('<div class="price-card"><p class="price-title">300 Mb</p><p class="price-val">30€</p></div>', unsafe_allow_html=True)
        with fm_cols[1]: st.markdown('<div class="price-card"><p class="price-title">600 Mb</p><p class="price-val">35€</p></div>', unsafe_allow_html=True)
        with fm_cols[2]: st.markdown('<div class="price-card"><p class="price-title">1 Gb</p><p class="price-val">38€</p></div>', unsafe_allow_html=True)

# --- SECCIÓN ⚖️ COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    f_act = st.number_input("Factura actual con IVA (EUR)", value=0.0)
    consumo = st.number_input("Consumo (kWh)", value=0.0)
    if st.button("CALCULAR AHORRO"):
        st.success(f"Estudio generado correctamente.")

# --- SECCIÓN 📈 DASHBOARD (CORREGIDO Y PROFESIONAL) ---
elif menu == "📈 DASHBOARD":
    st.header("🏆 Dashboard Ejecutivo")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    try:
        df_raw = pd.read_csv(sheet_url)
        df_raw['FECHA_DT'] = pd.to_datetime(df_raw['FECHA DE CREACIÓN'], dayfirst=True, errors='coerce')
        meses_dict = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
        df_raw['MES_NOMBRE'] = df_raw['FECHA_DT'].dt.month.map(meses_dict)

        f1, f2, f3 = st.columns(3)
        with f1: sel_mes = st.multiselect("Mes", sorted(df_raw['MES_NOMBRE'].dropna().unique()), default=df_raw['MES_NOMBRE'].dropna().unique())
        with f2: sel_comp = st.selectbox("Comercializadora", ["Todas"] + sorted(df_raw['COMERCIALIZADORA'].dropna().unique()))
        with f3: sel_com = st.multiselect("Comercial", sorted(df_raw['COMERCIAL'].dropna().unique()), default=df_raw['COMERCIAL'].dropna().unique())

        df = df_raw[df_raw['MES_NOMBRE'].isin(sel_mes)]
        if sel_comp != "Todas": df = df[df['COMERCIALIZADORA'] == sel_comp]
        df = df[df['COMERCIAL'].isin(sel_com)]

        m1, m2, m3 = st.columns(3)
        luz = df['CUPS LUZ'].count()
        gas = df['CUPS GAS'].count()
        with m1: st.markdown(f'<div class="metric-box"><p class="metric-title">Ventas Luz</p><p class="metric-value">{luz} ⚡</p></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-box"><p class="metric-title">Ventas Gas</p><p class="metric-value">{gas} 🔥</p></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-box"><p class="metric-title">Total</p><p class="metric-value" style="color:white;">{luz+gas} ✅</p></div>', unsafe_allow_html=True)

        fig = px.bar(df.groupby('COMERCIAL').size().reset_index(name='V'), x='COMERCIAL', y='V', color_discrete_sequence=['#d2ff00'], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e: st.error(f"Error en Dashboard: Asegúrate de que las columnas del Excel son correctas.")

# --- SECCIÓN 📂 REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    st.markdown('<div class="block-header">📂 MANUALES</div>', unsafe_allow_html=True)
    st.write("Selecciona una sección en el menú lateral para ver archivos.")