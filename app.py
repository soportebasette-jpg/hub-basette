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

# 3. CARGA DE DATOS DESDE GOOGLE SHEETS
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    def process(url, label):
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()
            df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha Creación', 'Comercial'])
            df['Año'] = df['Fecha Creación'].dt.year.astype(str)
            df['Mes'] = df['Fecha Creación'].dt.strftime('%m - %B')
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
            # Marcar bajas y cancelados por pestaña
            df[f'B_{label}'] = df['Estado'].str.upper().apply(lambda x: 1 if "BAJA" in str(x) else 0)
            df[f'C_{label}'] = df['Estado'].str.upper().apply(lambda x: 1 if "CANCELADO" in str(x) else 0)
            return df
        except: return pd.DataFrame()

    de = process(URL_ENE, "Ene")
    dt = process(URL_TEL, "Tel")
    da = process(URL_ALA, "Ala")

    if not de.empty:
        de['V_Luz'] = de['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0) if 'CUPS Luz' in de.columns else 0
        de['V_Gas'] = de['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0) if 'CUPS Gas' in de.columns else 0
    
    if not dt.empty:
        def calc_tel(row):
            f, m = 0, 0
            t = str(row.get('Tipo Tarifa', '')).lower()
            if 'fibra' in t: f = 1
            if 'movil' in t: m = 1
            for c in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
                if c in row and pd.notnull(row[c]) and str(row[c]).strip() != "": m += 1
            return f, m
        res = dt.apply(calc_tel, axis=1)
        dt['V_Fibra'] = res.apply(lambda x: x[0])
        dt['V_Móvil'] = res.apply(lambda x: x[1])
    
    if not da.empty: da['V_Alarma'] = 1

    return de, dt, da

# --- LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
        pwd = st.text_input("Contraseña:", type="password")
        if st.button("ACCEDER"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Incorrecto")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
    menu = st.radio("MENÚ", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD Y RANKING (ESTRUCTURA BLINDADA) ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        
        all_anos = sorted(list(set(de['Año'].unique() if not de.empty else []) | set(dt['Año'].unique() if not dt.empty else []) | set(da['Año'].unique() if not da.empty else [])))
        all_meses = sorted(list(set(de['Mes'].unique() if not de.empty else []) | set(dt['Mes'].unique() if not dt.empty else []) | set(da['Mes'].unique() if not da.empty else [])))
        all_coms = sorted(list(set(de['Comercial'].unique() if not de.empty else []) | set(dt['Comercial'].unique() if not dt.empty else []) | set(da['Comercial'].unique() if not da.empty else [])))

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: f_ano = st.selectbox("📅 Año", all_anos, index=len(all_anos)-1 if all_anos else 0)
        with c2: f_meses = st.multiselect("📆 Meses", all_meses, default=[all_meses[-1]] if all_meses else [])
        with c3: f_coms = st.multiselect("👤 Comerciales", all_coms, default=all_coms)

        f_de = de[(de['Año']==f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_coms))] if not de.empty else de
        f_dt = dt[(dt['Año']==f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_coms))] if not dt.empty else dt
        f_da = da[(da['Año']==f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_coms))] if not da.empty else da

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            st.markdown('<div class="block-header">RANKING GLOBAL CONSOLIDADO</div>', unsafe_allow_html=True)
            
            # CREAR TABLA BASE CON CEROS PARA EVITAR KEYERROR
            rank = pd.DataFrame({'Comercial': f_coms})
            cols_necesarias = ['V_Luz', 'V_Gas', 'V_Fibra', 'V_Móvil', 'V_Alarma', 'B_Ene', 'C_Ene', 'B_Tel', 'C_Tel', 'B_Ala', 'C_Ala']
            for c in cols_necesarias: rank[c] = 0.0
            rank = rank.set_index('Comercial')

            # Sumar datos reales si existen
            if not f_de.empty:
                sum_e = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'B_Ene', 'C_Ene']].sum()
                rank.update(sum_e)
            if not f_dt.empty:
                sum_t = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'B_Tel', 'C_Tel']].sum()
                rank.update(sum_t)
            if not f_da.empty:
                sum_a = f_da.groupby('Comercial')[['V_Alarma', 'B_Ala', 'C_Ala']].sum()
                rank.update(sum_a)

            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['BAJAS'] = rank['B_Ene'] + rank['B_Tel'] + rank['B_Ala']
            rank['CANC'] = rank['C_Ene'] + rank['C_Tel'] + rank['C_Ala']
            
            rank = rank.sort_values('TOTAL', ascending=False).reset_index()

            def color_r(s):
                if s.name in ['BAJAS', 'CANC']: return ['background-color: #ffcccc; color: #cc0000; font-weight: bold']*len(s)
                if s.name == 'TOTAL': return ['background-color: #d2ff00; color: black; font-weight: bold']*len(s)
                return ['']*len(s)

            st.write(rank[['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'TOTAL', 'BAJAS', 'CANC']].style.apply(color_r).to_html(), unsafe_allow_html=True)

        for tab, d_f, tit in zip([tab_e, tab_t, tab_a], [f_de, f_dt, f_da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_f.empty:
                    st.markdown(f'<div class="block-header">ESTADOS {tit}</div>', unsafe_allow_html=True)
                    a, b, c = st.columns(3)
                    st_act = d_f[d_f['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    st_baj = d_f[d_f['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    st_can = d_f[d_f['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    a.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{st_act}</div></div>', unsafe_allow_html=True)
                    b.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{st_baj}</div></div>', unsafe_allow_html=True)
                    c.markdown(f'<div class="status-box" style="background: #000000;"><div class="status-label">CANCELADOS</div><div class="status-value">{st_can}</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# --- RESTO DE SECCIONES COMPLETAS ---
elif menu == "🚀 CRM":
    st.header("Accesos Directos")
    st.link_button("MARCADOR VOZ", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.link_button("CRM BASETTE", "https://crm.grupobasette.eu/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifas Oficiales")
    st.write("Carga de tablas de Gana Energía, Naturgy y Total.")

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    st.info("Formulario para generación de propuesta en PDF.")

elif menu == "📢 ANUNCIOS":
    st.header("Marketing")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"): st.image("anunciosbasette/qr-plan amigo.png")

elif menu == "📂 REPOSITORIO":
    st.header("Descargas")
    if os.path.exists("manuales/Manual_Premiumnumber_Agente.pdf"):
        with open("manuales/Manual_Premiumnumber_Agente.pdf", "rb") as f:
            st.download_button("Descargar Manual Marcador", f, file_name="Manual.pdf")