import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Función para convertir imagen a base64 y que se vea en el HTML
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Preparamos la imagen de Rosco
img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD (GENERAL)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    button p, .stDownloadButton button p { color: black !important; font-weight: bold !important; }
    .stDownloadButton button {
        background-color: #d2ff00 !important;
        color: black !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        width: 100%;
    }
    .stTable { background-color: white !important; border-radius: 10px; overflow: hidden; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header {
        background-color: #d2ff00;
        color: black;
        padding: 8px 20px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 20px;
        margin-top: 25px;
        display: inline-block;
        font-size: 1.1rem;
    }
    .status-box {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    .status-label { font-size: 0.8rem; color: #8b949e; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }
    .status-value { font-size: 1.8rem; font-weight: 900; color: white; }
    div[data-testid="stExpander"] { background-color: #161b22 !important; border: 1px solid #30363d !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA DE DATOS (GOOGLE SHEETS)
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    def process_df(url, type_label):
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()
            df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha Creación', 'Comercial'])
            df['Año'] = df['Fecha Creación'].dt.year.astype(str)
            df['Mes'] = df['Fecha Creación'].dt.strftime('%m - %B')
            
            # Solo añadir lógica de detección de BAJA
            df['V_Baja'] = 0
            if 'Estado' in df.columns:
                df['V_Baja'] = df['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0)

            if type_label == 'ENE':
                df['V_Luz'] = df['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
                df['V_Gas'] = df['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
            elif type_label == 'TEL':
                df['V_Fibra'] = df['Tipo Tarifa'].apply(lambda x: 1 if 'fibra' in str(x).lower() else 0)
                df['V_Movil'] = df['Tipo Tarifa'].apply(lambda x: 1 if 'movil' in str(x).lower() or 'móvil' in str(x).lower() else 0)
            elif type_label == 'ALA':
                df['V_Alarma'] = 1
            return df
        except: return pd.DataFrame()
    return process_df(URL_ENE, 'ENE'), process_df(URL_TEL, 'TEL'), process_df(URL_ALA, 'ALA')

# --- AUTENTICACIÓN ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists("1000233813.jpg"): st.image("1000233813.jpg")
        st.markdown("<h3 style='text-align:center; color:#d2ff00;'>HUB COMERCIAL</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Introduce la clave de acceso:", type="password")
        if st.button("ACCEDER AL SISTEMA"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("1000233813.jpg"): st.image("1000233813.jpg")
    st.markdown("---")
    menu = st.radio("MENÚ PRINCIPAL:", ["🚀 CRM Y GESTIÓN", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])
    st.markdown("---")
    st.caption("v2.5 | Basette Group Systems")

# --- LÓGICA DE NAVEGACIÓN ---

if menu == "🚀 CRM Y GESTIÓN":
    st.markdown('<div class="block-header">ACCESOS DIRECTOS</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.link_button("🔥 MARCADOR VOZ CENTER", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    with c2: st.link_button("💎 CRM BASETTE (CLIENTES)", "https://crm.grupobasette.eu/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.markdown('<div class="block-header">TABLAS DE PRECIOS ACTUALIZADAS</div>', unsafe_allow_html=True)
    st.info("Consulte la sección 'REPOSITORIO' para descargar los PDFs de precios vigentes.")

elif menu == "⚖️ COMPARADOR":
    st.markdown('<div class="block-header">ESTUDIO DE AHORRO</div>', unsafe_allow_html=True)
    st.warning("Módulo en mantenimiento - Contacte con soporte para estudios manuales.")

elif menu == "📢 ANUNCIOS":
    st.markdown('<div class="block-header">MATERIAL DE MARKETING</div>', unsafe_allow_html=True)
    if os.path.exists("anunciosbasette/qr-plan amigo.png"):
        st.image("anunciosbasette/qr-plan amigo.png", caption="QR Plan Amigo")

elif menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        all_anos = sorted(list(set(de['Año']) | set(dt['Año']) | set(da['Año'])))
        all_meses = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
        all_coms = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: f_ano = st.selectbox("📅 Año", all_anos, index=len(all_anos)-1 if all_anos else 0)
        with c2: f_meses = st.multiselect("📆 Meses", all_meses, default=[all_meses[-1]] if all_meses else [])
        with c3: f_coms = st.multiselect("👤 Filtrar Comerciales", all_coms, default=all_coms)

        f_de = de[(de['Año']==f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_coms))]
        f_dt = dt[(dt['Año']==f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_coms))]
        f_da = da[(da['Año']==f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_coms))]

        t_rank, t_ene, t_tel, t_ala = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_rank:
            st.markdown('<div class="block-header">RANKING DE PRODUCTIVIDAD</div>', unsafe_allow_html=True)
            r1 = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'V_Baja']].sum() if not f_de.empty else pd.DataFrame()
            r2 = f_dt.groupby('Comercial')[['V_Fibra', 'V_Movil', 'V_Baja']].sum() if not f_dt.empty else pd.DataFrame()
            r3 = f_da.groupby('Comercial')[['V_Alarma', 'V_Baja']].sum() if not f_da.empty else pd.DataFrame()
            
            rank = pd.concat([r1, r2, r3], axis=1).fillna(0).astype(int)
            
            # Consolidar Bajas
            if 'V_Baja' in rank.columns:
                rank['Baja'] = rank['V_Baja'].sum(axis=1) if isinstance(rank['V_Baja'], pd.DataFrame) else rank['V_Baja']
            
            rank = rank.rename(columns={'V_Luz': 'Luz', 'V_Gas': 'Gas', 'V_Fibra': 'Fibra', 'V_Movil': 'Móvil', 'V_Alarma': 'Alarma'})
            
            cols_finales = ['Luz', 'Gas', 'Fibra', 'Móvil', 'Alarma', 'Baja']
            rank_display = rank[[c for c in cols_finales if c in rank.columns]]
            rank_display['TOTAL'] = rank_display.sum(axis=1) - rank_display.get('Baja', 0)
            
            st.table(rank_display.sort_values('TOTAL', ascending=False))

        with t_ene:
            if not f_de.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(f_de, names='Comercial', values='V_Luz', title="Luz")
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = px.bar(f_de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum().reset_index(), x='Comercial', y=['V_Luz', 'V_Gas'], title="Energía")
                    st.plotly_chart(fig2, use_container_width=True)

        with t_tel:
            if not f_dt.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(f_dt, names='Comercial', values='V_Fibra', title="Fibra")
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = px.bar(f_dt.groupby('Comercial')[['V_Fibra', 'V_Movil']].sum().reset_index(), x='Comercial', y=['V_Fibra', 'V_Movil'], title="Telco")
                    st.plotly_chart(fig2, use_container_width=True)

        with t_ala:
            if not f_da.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(f_da, names='Comercial', values='V_Alarma', title="Alarmas")
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = px.bar(f_da.groupby('Comercial')['V_Alarma'].sum().reset_index(), x='V_Alarma', y='Comercial', orientation='h', title="Alarmas")
                    st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 MANUAL DEL MARCADOR"):
        manual_path = "manuales/Manual_Premiumnumber_Agente.pdf"
        if os.path.exists(manual_path):
            with open(manual_path, "rb") as f:
                st.download_button("📖 DESCARGAR MANUAL", f, file_name="Manual_Marcador.pdf")
    st.markdown("---")
    with st.expander("📁 DOCUMENTACIÓN LOWI"):
        archivo_lowi = "manuales/TARIFAS_LOWI_MARZO2026.pdf"
        if os.path.exists(archivo_lowi):
            with open(archivo_lowi, "rb") as f:
                st.download_button("📄 DESCARGAR TARIFAS LOWI", f, file_name="Tarifas_Lowi.pdf")