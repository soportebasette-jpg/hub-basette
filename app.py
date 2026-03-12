import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. ESTILOS CSS PERSONALIZADOS (Integrando tus ideas)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* Etiquetas del Dashboard en Amarillo */
    .metric-label {
        color: #FFD700 !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    .metric-value {
        color: #FFD700 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    
    /* Estilo para los bloques de cabecera */
    .block-header {
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block;
    }

    /* Cards de Precios */
    .price-card {
        background-color: #161b22; border: 2px solid #30363d; border-radius: 15px;
        padding: 20px; text-align: center; margin-bottom: 15px; height: 100%;
    }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    
    /* Selectores */
    .stSelectbox div[data-baseweb="select"] { background-color: #161b22 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATOS DE TARIFAS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "logo": "manuales/logo_endesa.png"}
]

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
QR_PLAN_AMIGO = "anunciosbasette/qr-plan amigo.png"

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
        pwd = st.text_input("Clave Comercial:", type="password")
        if st.button("ACCEDER"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Incorrecta")
    st.stop()

# 5. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    menu = st.radio("MENÚ", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR LUZ", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD", "📂 REPOSITORIO"])

# --- SECCIÓN CRM ---
if menu == "🚀 CRM":
    st.header("🚀 Portales de Gestión")
    
    st.markdown('<div class="block-header">⭐ GESTIÓN PRINCIPAL</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.info("MARCADOR VOZ")
        st.link_button("ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    with c2:
        st.info("CRM BASETTE")
        st.link_button("ENTRAR AL CRM", "https://crm.grupobasette.eu/login", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 ENERGÍA</div>', unsafe_allow_html=True)
    en_links = [("GANA", "https://colaboradores.ganaenergia.com/"), ("NATURGY", "https://checkout.naturgy.es/backoffice"), ("TOTAL", "https://agentes.totalenergies.es/"), ("ENDESA", "https://inergia.app")]
    cols = st.columns(4)
    for i, (name, url) in enumerate(en_links):
        cols[i].link_button(name, url, use_container_width=True)

    st.markdown('<div class="block-header">🛡️ ALARMAS</div>', unsafe_allow_html=True)
    st.link_button("SEGURMA PARTNERS", "https://partners.segurma.com/", use_container_width=True)

    st.markdown('<div class="block-header">📶 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
    st.link_button("O2 ONLINE PORTAL", "https://o2online.es/auth/login/", use_container_width=True)

# --- SECCIÓN PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("📊 Tarifas Actualizadas")
    t1, t2, t3 = st.tabs(["LUZ", "GAS", "FIBRA/TV"])
    with t1:
        st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=["logo"]), use_container_width=True)
    with t2:
        df_gas = pd.DataFrame([
            {"COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA": "0,059 €/kWh"},
            {"COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA": "0,084 €/kWh"},
            {"COMPAÑÍA": "GANA ENERGÍA", "FIJO RL1": "3,93 €", "ENERGIA": "VARIABLE (GESTIÓN 0,11€)"}
        ])
        st.table(df_gas)
    with t3:
        st.markdown("### Solo TV: **9,99€**")
        st.markdown("### Fibra 300Mb: **23€** | 600Mb: **27€** | 1Gb: **31€**")

# --- SECCIÓN COMPARADOR LUZ ---
elif menu == "⚖️ COMPARADOR LUZ":
    st.header("⚖️ Comparador de Ahorro")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Cliente", "Nombre")
        f_act = st.number_input("Factura Actual (€)", 0.0)
        consumo = st.number_input("Consumo (kWh)", 0.0)
    with c2:
        compania = st.selectbox("Compañía Propuesta", [t["COMPAÑÍA"] for t in tarifas_luz])
        tar_info = next(t for t in tarifas_luz if t["COMPAÑÍA"] == compania)
        if os.path.exists(tar_info["logo"]): st.image(tar_info["logo"], width=100)
        st.write(f"Energía: {tar_info['ENERGIA']} | P1: {tar_info['P1']} | P2: {tar_info['P2']}")

    # Cálculo simplificado para el ejemplo
    coste_aprox = (consumo * 0.12) * 1.21
    ahorro = f_act - coste_aprox
    st.success(f"Ahorro estimado: {ahorro:.2f} €")

    if st.button("GENERAR PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDIO DE AHORRO BASETTE", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, f"Cliente: {cliente}", ln=True)
        pdf.cell(190, 10, f"Ahorro Mensual: {ahorro:.2f} EUR", ln=True)
        if os.path.exists(QR_PLAN_AMIGO):
            pdf.image(QR_PLAN_AMIGO, 75, 100, 50)
            pdf.text(75, 155, "ESCANEAME: PLAN AMIGO")
        st.download_button("Descargar PDF", pdf.output(dest='S').encode('latin-1'), "Estudio.pdf")

# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Plan Amigo e Instagram")
    st.link_button("INSTAGRAM BASETTE", "https://www.instagram.com/basette.eu/")
    if os.path.exists(QR_PLAN_AMIGO):
        st.image(QR_PLAN_AMIGO, caption="QR PLAN AMIGO", width=300)
        with open(QR_PLAN_AMIGO, "rb") as f:
            st.download_button("Descargar QR para enviar", f, "PlanAmigo.png")

# --- DASHBOARD (CON TUS ESTILOS) ---
elif menu == "📈 DASHBOARD":
    st.header("📈 Rendimiento en Tiempo Real")
    
    # Simulación de datos para que veas el estilo que pediste
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<p class="metric-label">Ventas Totales</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-value">124</p>', unsafe_allow_html=True)
    with col2:
        # ROJO PARA GANA ENERGÍA
        st.markdown('<p class="metric-label">Gana Energía</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-value" style="color:#FF0000 !important;">45</p>', unsafe_allow_html=True)
    with col3:
        # ROJO PARA GAS
        st.markdown('<p class="metric-label">Contratos Gas</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-value" style="color:#FF0000 !important;">28</p>', unsafe_allow_html=True)

    # Lógica de carga de Google Sheets (Corregida para fechas)
    try:
        url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
        df = pd.read_csv(url)
        df['FECHA_DT'] = pd.to_datetime(df['FECHA DE CREACIÓN'], dayfirst=True, errors='coerce')
        df['MES'] = df['FECHA_DT'].dt.month_name()
        
        sel_mes = st.selectbox("Seleccionar Mes", df['MES'].dropna().unique())
        df_mes = df[df['MES'] == sel_mes]
        st.dataframe(df_mes)
    except:
        st.warning("Conectando con base de datos de Google Sheets...")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("📂 Repositorio de Documentos")
    manuales = {
        "ARGUMENTARIOS": ["Venta_Energia.pdf", "Script_Telecom.pdf"],
        "GANA ENERGÍA": ["Manual_Gana.pdf"],
        "NATURGY": ["Ficha_Naturgy.pdf"],
        "O2": ["Tarifas_O2.pdf"]
    }
    for carp, archivos in manuales.items():
        with st.expander(f"📁 {carp}"):
            for arc in archivos:
                st.write(f"📄 {arc}")
                # Aquí podrías poner botones de descarga reales si los archivos existen en /manuales/