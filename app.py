import streamlit as st
import os
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Función para imagen a base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p { color: #d2ff00 !important; font-weight: 900 !important; font-size: 1.25rem !important; }
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    .status-box { padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid #30363d; }
    .status-label { font-size: 0.8rem; color: #8b949e; margin-bottom: 2px; text-transform: uppercase; }
    .status-value { font-size: 1.5rem; font-weight: 900; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    # ENERGÍA
    df_e = pd.read_csv(URL_ENE)
    df_e.columns = df_e.columns.str.strip()
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['REF_Ene'] = df_e['Canal'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip().upper() == "REF" else 0) if 'Canal' in df_e.columns else 0
    df_e['Baja_Ene'] = df_e['Estado'].apply(lambda x: 1 if pd.notnull(x) and "BAJA" in str(x).upper() else 0)
    df_e['Canc_Ene'] = df_e['Estado'].apply(lambda x: 1 if pd.notnull(x) and "CANCELADO" in str(x).upper() else 0)
    
    # TELCO
    df_t = pd.read_csv(URL_TEL)
    df_t.columns = df_t.columns.str.strip()
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    
    def get_telco_metrics(row):
        f, m = 0, 0
        t = str(row.get('Tipo Tarifa', '')).lower()
        if 'fibramovil' in t or ('fibra' in t and 'movil' in t): f, m = 1, 1
        elif 'fibra' in t: f = 1
        elif 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return f, m
    res = df_t.apply(get_telco_metrics, axis=1)
    df_t['V_Fibra'] = res.apply(lambda x: x[0])
    df_t['V_Móvil'] = res.apply(lambda x: x[1])
    df_t['REF_Tel'] = df_t['Canal'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip().upper() == "REF" else 0) if 'Canal' in df_t.columns else 0
    df_t['Baja_Tel'] = df_t['Estado'].apply(lambda x: 1 if pd.notnull(x) and "BAJA" in str(x).upper() else 0)
    df_t['Canc_Tel'] = df_t['Estado'].apply(lambda x: 1 if pd.notnull(x) and "CANCELADO" in str(x).upper() else 0)

    # ALARMAS
    df_a = pd.read_csv(URL_ALA)
    df_a.columns = df_a.columns.str.strip()
    df_a['Fecha Creación'] = pd.to_datetime(df_a['Fecha Creación'], dayfirst=True, errors='coerce')
    df_a = df_a.dropna(subset=['Comercial', 'Fecha Creación'])
    df_a['Año'] = df_a['Fecha Creación'].dt.year.astype(str)
    df_a['Mes'] = df_a['Fecha Creación'].dt.strftime('%m - %B')
    df_a['V_Alarma'] = 1 
    df_a['REF_Ala'] = df_a['Canal'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip().upper() == "REF" else 0) if 'Canal' in df_a.columns else 0
    df_a['Baja_Ala'] = df_a['Estado'].apply(lambda x: 1 if pd.notnull(x) and "BAJA" in str(x).upper() else 0)
    df_a['Canc_Ala'] = df_a['Estado'].apply(lambda x: 1 if pd.notnull(x) and "CANCELADO" in str(x).upper() else 0)
    
    return df_e, df_t, df_a

# --- LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
        pwd = st.text_input("Introduce Clave Comercial:", type="password")
        if st.button("ACCEDER AL HUB"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# --- NAVEGACIÓN ---
with st.sidebar:
    st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- LÓGICA DE DASHBOARD (REVISADA) ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        
        # Filtros Superiores
        c_filt_1, c_filt_2, c_filt_3 = st.columns([1, 2, 2])
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año']) | set(df_a['Año'])))
        meses_disp = sorted(list(set(df_e['Mes']) | set(df_t['Mes']) | set(df_a['Mes'])))
        comerciales_lista = sorted(list(set(df_e['Comercial']) | set(df_t['Comercial']) | set(df_a['Comercial'])))
        
        with c_filt_1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_filt_2: f_meses = st.multiselect("📆 Meses (Selección Múltiple)", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
        with c_filt_3: f_com = st.multiselect("👤 Comerciales", options=comerciales_lista, default=comerciales_lista)

        # Aplicar Filtros
        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'].isin(f_meses)) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'].isin(f_meses)) & (df_t['Comercial'].isin(f_com))]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'].isin(f_meses)) & (df_a['Comercial'].isin(f_com))]

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING GLOBAL", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            # Agrupar por comercial
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'REF_Ene', 'Baja_Ene', 'Canc_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'REF_Tel', 'Baja_Tel', 'Canc_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'REF_Ala', 'Baja_Ala', 'Canc_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['T+M'] = rank['TOTAL'] + rank['V_Móvil']
            rank['REF'] = rank.get('REF_Ene',0) + rank.get('REF_Tel',0) + rank.get('REF_Ala',0)
            rank['BAJAS'] = rank.get('Baja_Ene',0) + rank.get('Baja_Tel',0) + rank.get('Baja_Ala',0)
            rank['CANC'] = rank.get('Canc_Ene',0) + rank.get('Canc_Tel',0) + rank.get('Canc_Ala',0)
            rank = rank.sort_values('TOTAL', ascending=False).reset_index()

            # Estilos del Ranking
            def style_cols(s):
                return ['background-color: #ffcccc; color: #cc0000; font-weight: bold' if s.name in ['BAJAS', 'CANC'] 
                        else 'background-color: #d2ff00; color: black; font-weight: bold' if s.name == 'TOTAL' 
                        else '' for _ in s]

            st.write(rank[['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'TOTAL', 'T+M', 'REF', 'BAJAS', 'CANC']].style.apply(style_cols).to_html(), unsafe_allow_html=True)

        # Pestañas individuales corregidas
        for tab, d_f, tit in zip([tab_e, tab_t, tab_a], [de, dt, da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_f.empty:
                    st.markdown(f'<div class="block-header">ESTADO GLOBAL {tit}</div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    act = d_f[d_f['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    baj = d_f[d_f['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    can = d_f[d_f['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    
                    c1.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{act}</div></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{baj}</div></div>', unsafe_allow_html=True)
                    c3.markdown(f'<div class="status-box" style="background: #333333;"><div class="status-label">CANCELADOS</div><div class="status-value">{can}</div></div>', unsafe_allow_html=True)

                    # Gráfico Barras Comparativo
                    d_f['Estado_Graf'] = d_f['Estado'].str.upper().apply(lambda x: 'ACTIVO' if 'ACTIVO' in str(x) else ('BAJA' if 'BAJA' in str(x) else 'CANCELADO'))
                    fig = px.bar(d_f.groupby(['Comercial', 'Estado_Graf']).size().reset_index(name='Cant'), 
                                 x='Comercial', y='Cant', color='Estado_Graf', barmode='group',
                                 color_discrete_map={'ACTIVO': '#d2ff00', 'BAJA': '#ff0000', 'CANCELADO': '#000000'})
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error crítico en datos: {e}. Verifica que las columnas de los Excels no hayan cambiado de nombre.")

# --- RESTO DE SECCIONES (PARA COPIAR Y PEGAR) ---
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.link_button("ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.link_button("CRM BASETTE", "https://crm.grupobasette.eu/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifario")
    st.info("Consulta aquí los precios vigentes de Energía y Telco.")

elif menu == "⚖️ COMPARADOR":
    st.header("Generador de Ahorro")
    st.write("Complete los datos para generar el PDF comparativo.")

elif menu == "📢 ANUNCIOS":
    st.header("Material Publicitario")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"): st.image("anunciosbasette/qr-plan amigo.png", width=300)

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    st.write("Descarga aquí manuales y normativas.")