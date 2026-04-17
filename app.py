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

# Función para convertir imagen a base64
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
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    .winner-card { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 25px; border-radius: 15px; color: white !important; text-align: center; font-weight: bold; font-size: 28px; margin-bottom: 25px; }
    .price-card { background-color: #161b22; border: 2px solid #30363d; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; transition: transform 0.3s; height: 100%; }
    .price-card:hover { border-color: #d2ff00; transform: translateY(-5px); }
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
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    df_e['REF_Ene'] = df_e['Canal'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip().upper() == "REF" else 0)
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
        return f, m, (f + m)
    res = df_t.apply(get_telco_metrics, axis=1)
    df_t['V_Fibra'] = res.apply(lambda x: x[0])
    df_t['V_Móvil'] = res.apply(lambda x: x[1])
    df_t['Total_Tel'] = res.apply(lambda x: x[2])
    df_t['REF_Tel'] = df_t['Canal'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip().upper() == "REF" else 0)
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
    df_a['REF_Ala'] = df_a['Canal'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip().upper() == "REF" else 0)
    df_a['Baja_Ala'] = df_a['Estado'].apply(lambda x: 1 if pd.notnull(x) and "BAJA" in str(x).upper() else 0)
    df_a['Canc_Ala'] = df_a['Estado'].apply(lambda x: 1 if pd.notnull(x) and "CANCELADO" in str(x).upper() else 0)
    
    return df_e, df_t, df_a

# --- TARIFAS ---
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.119, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,171/0,104/0,08", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"}
]

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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- SECCIÓN CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA Y TELCO</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.link_button("CRM BASETTE", "https://crm.grupobasette.eu/login", use_container_width=True)
    c2.link_button("GANA ENERGÍA", "https://colaboradores.ganaenergia.com/", use_container_width=True)
    c3.link_button("O2", "https://o2online.es/auth/login/", use_container_width=True)

# --- SECCIÓN PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)

# --- SECCIÓN COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    st.info("Formulario para generación de PDFs de ahorro.")
    # (Aquí va tu lógica de FPDF del archivo original)

# --- SECCIÓN ANUNCIOS ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("Material Publicitario")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"):
        st.image("anunciosbasette/qr-plan amigo.png", width=250)
    st.link_button("Formulario Plan Amigo", "https://forms.gle/mU6XzRvywDoBQ5Q47", use_container_width=True)

# --- SECCIÓN DASHBOARD (DONDE ESTABA EL ERROR) ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        
        # FILTROS
        c_filt_1, c_filt_2, c_filt_3 = st.columns([1, 2, 2])
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año']) | set(df_a['Año'])))
        meses_disp = sorted(list(set(df_e['Mes']) | set(df_t['Mes']) | set(df_a['Mes'])))
        comerciales_lista = sorted(list(set(df_e['Comercial']) | set(df_t['Comercial']) | set(df_a['Comercial'])))
        
        with c_filt_1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_filt_2: f_meses = st.multiselect("📆 Meses (Selecciona varios para GLOBAL)", meses_disp, default=[meses_disp[-1]])
        with c_filt_3: f_com = st.multiselect("👤 Comerciales", options=comerciales_lista, default=comerciales_lista)

        # APLICAR FILTROS
        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'].isin(f_meses)) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'].isin(f_meses)) & (df_t['Comercial'].isin(f_com))]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'].isin(f_meses)) & (df_a['Comercial'].isin(f_com))]

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'REF_Ene', 'Baja_Ene', 'Canc_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'REF_Tel', 'Baja_Tel', 'Canc_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'REF_Ala', 'Baja_Ala', 'Canc_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['T+M'] = rank['TOTAL'] + rank['V_Móvil']
            rank['REF'] = rank['REF_Ene'] + rank['REF_Tel'] + rank['REF_Ala']
            rank['BAJAS'] = rank['Baja_Ene'] + rank['Baja_Tel'] + rank['Baja_Ala']
            rank['CANC'] = rank['Canc_Ene'] + rank['Canc_Tel'] + rank['Canc_Ala']
            rank = rank.sort_values('TOTAL', ascending=False).reset_index()

            def style_rojo(val): return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
            def style_verde(val): return 'background-color: #d2ff00; color: black; font-weight: bold;'

            st.write(
                rank[['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'TOTAL', 'T+M', 'REF', 'BAJAS', 'CANC']]
                .style.map(style_rojo, subset=['BAJAS', 'CANC'])
                .map(style_verde, subset=['TOTAL'])
                .to_html(escape=False, index=False), unsafe_allow_html=True
            )

        # Lógica para pestañas de Energía, Telco y Alarma
        for tab, d_filtrado, titulo in zip([tab_e, tab_t, tab_a], [de, dt, da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_filtrado.empty:
                    st.markdown(f'<div class="block-header">ESTADÍSTICAS {titulo}</div>', unsafe_allow_html=True)
                    e_act = d_filtrado[d_filtrado['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    e_baj = d_filtrado[d_filtrado['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    e_can = d_filtrado[d_filtrado['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{e_act}</div></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{e_baj}</div></div>', unsafe_allow_html=True)
                    c3.markdown(f'<div class="status-box" style="background: #000000;"><div class="status-label">CANCELADOS</div><div class="status-value">{e_can}</div></div>', unsafe_allow_html=True)

                    # GRÁFICO DE BARRAS POR COMERCIAL
                    d_filtrado['Es_Activo'] = d_filtrado['Estado'].str.upper().str.contains("ACTIVO", na=False).astype(int)
                    d_filtrado['Es_Baja'] = d_filtrado['Estado'].str.upper().str.contains("BAJA", na=False).astype(int)
                    d_filtrado['Es_Cancelado'] = d_filtrado['Estado'].str.upper().str.contains("CANCELADO", na=False).astype(int)
                    
                    res_bar = d_filtrado.groupby('Comercial')[['Es_Activo', 'Es_Baja', 'Es_Cancelado']].sum().reset_index()
                    fig = px.bar(res_bar, x='Comercial', y=['Es_Activo', 'Es_Baja', 'Es_Cancelado'], 
                                 title=f"Desglose por Comercial - {titulo}", barmode='group',
                                 color_discrete_map={'Es_Activo': '#d2ff00', 'Es_Baja': '#ff0000', 'Es_Cancelado': '#000000'})
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    if os.path.exists("manuales/Manual_Premiumnumber_Agente.pdf"):
        with open("manuales/Manual_Premiumnumber_Agente.pdf", "rb") as f:
            st.download_button("📖 DESCARGAR MANUAL MARCADOR", f, file_name="Manual_Marcador.pdf")