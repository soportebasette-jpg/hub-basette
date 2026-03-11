import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Basette Group | Hub", layout="wide", initial_sidebar_state="expanded")

# 2. CSS - ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* Filtros con fondo oscuro y borde flúor */
    div[data-testid="stSelectbox"] > div { background-color: #1c2128 !important; border: 1px solid #d2ff00 !important; }
    label[data-testid="stWidgetLabel"] p { color: black !important; background-color: #d2ff00; padding: 5px 10px; border-radius: 5px; font-weight: bold; }

    /* MÉTRICAS: FONDO BLANCO Y TEXTO NEGRO PARA MÁXIMA LECTURA */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 3px solid #d2ff00 !important;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(210, 255, 0, 0.3);
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 3rem !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #333333 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }

    /* Botones */
    .stButton button, .stDownloadButton button {
        background-color: #ffffff !important;
        color: black !important;
        border: 2px solid #d2ff00 !important;
        font-weight: 800 !important;
        width: 100%;
        margin-bottom: 10px;
    }

    .block-header {
        background-color: #d2ff00; color: black; padding: 12px; border-radius: 8px;
        font-weight: 900; margin: 25px 0; text-align: center; text-transform: uppercase;
    }

    .price-card {
        background-color: #161b22; border: 2px solid #30363d; border-radius: 15px;
        padding: 15px; text-align: center; margin-bottom: 15px;
    }
    .price-title { color: #d2ff00; font-size: 1.1rem; font-weight: bold; }
    .price-val { color: white; font-size: 1.9rem; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS
tarifas_luz = [
    {"COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "ENERGIA": 0.129},
    {"COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "ENERGIA": "0.09/0.114/0.181"},
    {"COMPAÑÍA": "NATURGY", "TARIFA": "24H", "P1": 0.123, "ENERGIA": 0.109},
    {"COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H", "P1": 0.081, "ENERGIA": 0.114}
]

# 4. NAVEGACIÓN
with st.sidebar:
    st.image("1000233813.jpg")
    st.markdown("---")
    menu = st.radio("MENÚ PRINCIPAL", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DASHBOARD", "📂 REPOSITORIO"])

# --- SECCIÓN CRM ---
if menu == "🚀 CRM":
    st.markdown('<div class="block-header">ACCESOS DIRECTOS</div>', unsafe_allow_html=True)
    links = [("MARCADOR VOZ", "https://grupobasette.vozipcenter.com/"), ("CRM BASETTE", "https://crm.grupobasette.eu/login"),
             ("GANA ENERGÍA", "https://colaboradores.ganaenergia.com/"), ("NATURGY", "https://checkout.naturgy.es/backoffice"),
             ("TOTAL ENERGIES", "https://agentes.totalenergies.es/"), ("SEGURMA", "https://partners.segurma.com/")]
    c1, c2 = st.columns(2)
    for i, (name, url) in enumerate(links):
        with (c1 if i % 2 == 0 else c2):
            st.link_button(name, url, use_container_width=True)

# --- SECCIÓN PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifas Actualizadas")
    t_luz, t_gas, t_fibra = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 FIBRA O2"])
    with t_luz:
        st.dataframe(pd.DataFrame(tarifas_luz), use_container_width=True, hide_index=True)
    with t_fibra:
        st.markdown('<div class="block-header">OFERTAS O2</div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: st.markdown('<div class="price-card"><div class="price-title">FIBRA 300Mb</div><div class="price-val">23€</div></div>', unsafe_allow_html=True)
        with f2: st.markdown('<div class="price-card"><div class="price-title">300Mb + 40GB</div><div class="price-val">30€</div></div>', unsafe_allow_html=True)
        with f3: st.markdown('<div class="price-card"><div class="price-title">1Gb + 120GB</div><div class="price-val">38€</div></div>', unsafe_allow_html=True)

# --- SECCIÓN COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Calculadora de Ahorro")
    cx1, cx2 = st.columns(2)
    with cx1:
        f_act = st.number_input("Factura Actual (€)", value=80.0)
        kwh = st.number_input("Consumo Mensual (kWh)", value=250.0)
    with cx2:
        prop = st.selectbox("Tarifa Propuesta", ["GANA 24H", "GANA 3T", "NATURGY 24H"])
        precio = 0.129 if "GANA 24H" in prop else 0.11
    
    total_prop = (kwh * precio * 1.21) + 15
    ahorro = f_act - total_prop
    st.markdown(f'<div style="background:#d2ff00; color:black; padding:25px; border-radius:15px; text-align:center;"><h1>AHORRO: {ahorro:.2f} €/mes</h1></div>', unsafe_allow_html=True)

# --- SECCIÓN DASHBOARD ---
elif menu == "📈 DASHBOARD":
    st.header("Panel de Control de Ventas")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    try:
        df = pd.read_csv(sheet_url)
        df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
        
        # MÉTRICAS CON FONDO BLANCO (DEFINIDO EN CSS)
        m1, m2, m3 = st.columns(3)
        luz_count = df['CUPS Luz'].notna().sum()
        gas_count = df['CUPS Gas'].notna().sum()
        m1.metric("VENTAS LUZ", f"{luz_count}")
        m2.metric("VENTAS GAS", f"{gas_count}")
        m3.metric("TOTAL", f"{luz_count + gas_count}")

        # GRÁFICO BARRA
        st.markdown('<div class="block-header">RANKING COMERCIALES</div>', unsafe_allow_html=True)
        df_com = df.groupby('Comercial').size().reset_index(name='Ventas')
        st.plotly_chart(px.bar(df_com, x='Comercial', y='Ventas', color_discrete_sequence=['#d2ff00'], template="plotly_dark"), use_container_width=True)
    except:
        st.warning("Cargando datos del CRM...")

# --- SECCIÓN REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Repositorio de Documentos")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="block-header">MATERIAL DE VENTA</div>', unsafe_allow_html=True)
        st.button("📄 Argumentario Energía")
        st.button("📄 Dossier Telecomunicaciones")
        st.button("📄 Tabla de Comisiones")
    with col_b:
        st.markdown('<div class="block-header">MANUALES</div>', unsafe_allow_html=True)
        st.button("📂 Manual CRM")
        st.button("📂 Manual Marcador")
        st.button("⚖️ Normativa Calidad")