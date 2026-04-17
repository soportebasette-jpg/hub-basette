import streamlit as st
import os
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
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
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    .status-box { padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid #30363d; }
    .status-label { font-size: 0.8rem; color: #8b949e; margin-bottom: 2px; text-transform: uppercase; }
    .status-value { font-size: 1.5rem; font-weight: 900; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA DE DATOS
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
            # Asegurar columnas críticas
            if 'Comercial' not in df.columns: df['Comercial'] = 'Desconocido'
            if 'Estado' not in df.columns: df['Estado'] = 'SIN ESTADO'
            
            df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha Creación'])
            df['Año'] = df['Fecha Creación'].dt.year.astype(str)
            df['Mes'] = df['Fecha Creación'].dt.strftime('%m - %B')
            
            # Flags de estado para el ranking
            df[f'Baja_{type_label}'] = df['Estado'].apply(lambda x: 1 if "BAJA" in str(x).upper() else 0)
            df[f'Canc_{type_label}'] = df['Estado'].apply(lambda x: 1 if "CANCELADO" in str(x).upper() else 0)
            return df
        except:
            return pd.DataFrame(columns=['Comercial', 'Año', 'Mes', 'Estado'])

    df_e = process_df(URL_ENE, "Ene")
    df_t = process_df(URL_TEL, "Tel")
    df_a = process_df(URL_ALA, "Ala")

    # Métricas específicas
    df_e['V_Luz'] = df_e.get('CUPS Luz', pd.Series()).apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e.get('CUPS Gas', pd.Series()).apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    
    df_a['V_Alarma'] = 1
    
    def get_tel_m(row):
        f, m = 0, 0
        t = str(row.get('Tipo Tarifa', '')).lower()
        if 'fibra' in t: f = 1
        if 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return f, m
    
    if not df_t.empty:
        res = df_t.apply(get_tel_m, axis=1)
        df_t['V_Fibra'] = res.apply(lambda x: x[0])
        df_t['V_Móvil'] = res.apply(lambda x: x[1])
    else:
        df_t['V_Fibra'] = 0; df_t['V_Móvil'] = 0

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

# --- SIDEBAR ---
with st.sidebar:
    st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD (CORREGIDO) ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        
        c1, c2, c3 = st.columns([1, 2, 2])
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año']) | set(df_a['Año'])))
        meses = sorted(list(set(df_e['Mes']) | set(df_t['Mes']) | set(df_a['Mes'])))
        coms = sorted(list(set(df_e['Comercial']) | set(df_t['Comercial']) | set(df_a['Comercial'])))
        
        with c1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c2: f_meses = st.multiselect("📆 Meses (Selección Múltiple)", meses, default=[meses[-1]] if meses else [])
        with c3: f_com = st.multiselect("👤 Comerciales", options=coms, default=coms)

        # Filtro de datos
        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'].isin(f_meses)) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'].isin(f_meses)) & (df_t['Comercial'].isin(f_com))]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'].isin(f_meses)) & (df_a['Comercial'].isin(f_com))]

        t_r, t_e, t_t, t_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_r:
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'Baja_Ene', 'Canc_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'Baja_Tel', 'Canc_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'Baja_Ala', 'Canc_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            rank['TOTAL'] = rank.get('V_Luz',0) + rank.get('V_Gas',0) + rank.get('V_Fibra',0) + rank.get('V_Alarma',0)
            rank['BAJAS'] = rank.get('Baja_Ene',0) + rank.get('Baja_Tel',0) + rank.get('Baja_Ala',0)
            rank['CANC'] = rank.get('Canc_Ene',0) + rank.get('Canc_Tel',0) + rank.get('Canc_Ala',0)
            rank = rank.sort_values('TOTAL', ascending=False).reset_index()

            def style_rows(s):
                if s.name in ['BAJAS', 'CANC']: return ['background-color: #ffcccc; color: #cc0000; font-weight: bold']*len(s)
                if s.name == 'TOTAL': return ['background-color: #d2ff00; color: black; font-weight: bold']*len(s)
                return ['']*len(s)

            st.write(rank[['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'TOTAL', 'BAJAS', 'CANC']].style.apply(style_rows).to_html(), unsafe_allow_html=True)

        for tab, d_f, tit in zip([t_e, t_t, t_a], [de, dt, da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_f.empty:
                    st.markdown(f'<div class="block-header">ANÁLISIS GLOBAL {tit}</div>', unsafe_allow_html=True)
                    c_1, c_2, c_3 = st.columns(3)
                    act = d_f[d_f['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    baj = d_f[d_f['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    can = d_f[d_f['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    c_1.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{act}</div></div>', unsafe_allow_html=True)
                    c_2.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{baj}</div></div>', unsafe_allow_html=True)
                    c_3.markdown(f'<div class="status-box" style="background: #333333;"><div class="status-label">CANCELADOS</div><div class="status-value">{can}</div></div>', unsafe_allow_html=True)

                    d_f['Est_Gr'] = d_f['Estado'].str.upper().apply(lambda x: 'ACTIVO' if 'ACTIVO' in str(x) else ('BAJA' if 'BAJA' in str(x) else 'CANCELADO'))
                    fig = px.bar(d_f.groupby(['Comercial', 'Est_Gr']).size().reset_index(name='C'), x='Comercial', y='C', color='Est_Gr', barmode='group',
                                 color_discrete_map={'ACTIVO': '#d2ff00', 'BAJA': '#ff0000', 'CANCELADO': '#000000'})
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# --- RESTO DE SECCIONES ---
elif menu == "🚀 CRM":
    st.header("Portales")
    st.link_button("CRM BASETTE", "https://crm.grupobasette.eu/login", use_container_width=True)
elif menu == "📊 PRECIOS":
    st.header("Tarifas")
    st.info("Consulta las tablas oficiales aquí.")
elif menu == "⚖️ COMPARADOR":
    st.header("Comparador")
    st.write("Genera tu PDF de ahorro.")
elif menu == "📢 ANUNCIOS":
    st.header("Marketing")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"): st.image("anunciosbasette/qr-plan amigo.png")
elif menu == "📂 REPOSITORIO":
    st.header("Documentos")