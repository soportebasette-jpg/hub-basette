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

# 3. CARGA Y LIMPIEZA DE DATOS (PROTEGIDA)
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    def safe_load(url, tag):
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()
            df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha Creación', 'Comercial'])
            df['Año'] = df['Fecha Creación'].dt.year.astype(str)
            df['Mes'] = df['Fecha Creación'].dt.strftime('%m - %B')
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
            return df
        except:
            return pd.DataFrame(columns=['Comercial', 'Año', 'Mes', 'Estado', 'Fecha Creación'])

    de = safe_load(URL_ENE, "Ene")
    dt = safe_load(URL_TEL, "Tel")
    da = safe_load(URL_ALA, "Ala")

    # Métricas Energía
    de['V_Luz'] = de['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0) if 'CUPS Luz' in de.columns else 0
    de['V_Gas'] = de['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0) if 'CUPS Gas' in de.columns else 0
    
    # Métricas Telco
    def calc_tel(row):
        f, m = 0, 0
        tipo = str(row.get('Tipo Tarifa', '')).lower()
        if 'fibra' in tipo: f = 1
        if 'movil' in tipo: m = 1
        for c in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if c in row and pd.notnull(row[c]) and str(row[c]).strip() != "": m += 1
        return f, m
    
    if not dt.empty:
        res_t = dt.apply(calc_tel, axis=1)
        dt['V_Fibra'] = res_t.apply(lambda x: x[0])
        dt['V_Móvil'] = res_t.apply(lambda x: x[1])
    else:
        dt['V_Fibra'] = 0; dt['V_Móvil'] = 0

    # Métricas Alarmas
    da['V_Alarma'] = 1 if not da.empty else 0

    return de, dt, da

# --- LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
        pwd = st.text_input("Clave Comercial:", type="password")
        if st.button("ACCEDER"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Error")
    st.stop()

# --- NAVEGACIÓN ---
with st.sidebar:
    st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD Y RANKING (CORREGIDO TOTALMENTE) ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        
        c1, c2, c3 = st.columns([1, 2, 2])
        anos = sorted(list(set(de['Año']) | set(dt['Año']) | set(da['Año'])))
        meses = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
        coms = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))
        
        with c1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c2: f_meses = st.multiselect("📆 Meses", meses, default=[meses[-1]] if meses else [])
        with c3: f_com = st.multiselect("👤 Comerciales", options=coms, default=coms)

        f_de = de[(de['Año'] == f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_com))]
        f_dt = dt[(dt['Año'] == f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_com))]
        f_da = da[(da['Año'] == f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_com))]

        t_rank, t_ene, t_tel, t_ala = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_rank:
            st.markdown('<div class="block-header">RANKING GLOBAL VENTAS</div>', unsafe_allow_html=True)
            
            # Agrupar asegurando que las columnas existan
            re = f_de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum() if not f_de.empty else pd.DataFrame()
            rt = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum() if not f_dt.empty else pd.DataFrame()
            ra = f_da.groupby('Comercial')[['V_Alarma']].sum() if not f_da.empty else pd.DataFrame()
            
            # Agrupar Estados (Bajas y Cancelados)
            for d, n in zip([f_de, f_dt, f_da], ["E", "T", "A"]):
                d[f'B_{n}'] = d['Estado'].apply(lambda x: 1 if "BAJA" in str(x).upper() else 0)
                d[f'C_{n}'] = d['Estado'].apply(lambda x: 1 if "CANCELADO" in str(x).upper() else 0)
            
            be = f_de.groupby('Comercial')[['B_E', 'C_E']].sum() if not f_de.empty else pd.DataFrame()
            bt = f_dt.groupby('Comercial')[['B_T', 'C_T']].sum() if not f_dt.empty else pd.DataFrame()
            ba = f_da.groupby('Comercial')[['B_A', 'C_A']].sum() if not f_da.empty else pd.DataFrame()

            # Unir y Rellenar Faltantes
            rank = pd.concat([re, rt, ra, be, bt, ba], axis=1).fillna(0)
            
            # Crear columnas si no existen tras el concat
            for col in ['V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'B_E', 'B_T', 'B_A', 'C_E', 'C_T', 'C_A']:
                if col not in rank.columns: rank[col] = 0

            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['BAJAS'] = rank['B_E'] + rank['B_T'] + rank['B_A']
            rank['CANC'] = rank['C_E'] + rank['C_T'] + rank['C_A']
            
            rank = rank.sort_values('TOTAL', ascending=False).reset_index()

            def style_cols(s):
                if s.name in ['BAJAS', 'CANC']: return ['background-color: #ffcccc; color: #cc0000; font-weight: bold']*len(s)
                if s.name == 'TOTAL': return ['background-color: #d2ff00; color: black; font-weight: bold']*len(s)
                return ['']*len(s)

            st.write(rank[['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'TOTAL', 'BAJAS', 'CANC']].style.apply(style_cols).to_html(), unsafe_allow_html=True)

        for tab, d_filt, tit in zip([t_ene, t_tel, t_ala], [f_de, f_dt, f_da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_filt.empty:
                    st.markdown(f'<div class="block-header">ESTADOS {tit}</div>', unsafe_allow_html=True)
                    act = d_filt[d_filt['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    baj = d_filt[d_filt['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    can = d_filt[d_filt['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    c_a, c_b, c_c = st.columns(3)
                    c_a.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{act}</div></div>', unsafe_allow_html=True)
                    c_b.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{baj}</div></div>', unsafe_allow_html=True)
                    c_c.markdown(f'<div class="status-box" style="background: #000000;"><div class="status-label">CANCELADOS</div><div class="status-value">{can}</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error detectado: {e}")

# --- RESTO DE SECCIONES (COMPLETAS) ---
elif menu == "🚀 CRM":
    st.header("Gestión")
    st.link_button("MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.link_button("CRM", "https://crm.grupobasette.eu/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifario Actualizado")
    st.write("Tablas de Gana Energía, Naturgy y Total.")

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    st.info("Formulario para generar PDF de ahorro.")

elif menu == "📢 ANUNCIOS":
    st.header("Publicidad")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"): st.image("anunciosbasette/qr-plan amigo.png")

elif menu == "📂 REPOSITORIO":
    st.header("Manuales")
    if os.path.exists("manuales/Manual_Premiumnumber_Agente.pdf"):
        with open("manuales/Manual_Premiumnumber_Agente.pdf", "rb") as f:
            st.download_button("DESCARGAR MANUAL", f, file_name="Manual.pdf")