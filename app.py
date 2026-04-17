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

# 3. CARGA DE DATOS (RECONSTRUCCIÓN SEGURA)
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
            
            # Crear columnas de Bajas/Canc por defecto
            df['B_Ene'] = 0; df['C_Ene'] = 0; df['B_Tel'] = 0; df['C_Tel'] = 0; df['B_Ala'] = 0; df['C_Ala'] = 0
            
            # Lógica de estados
            cond_baja = df['Estado'].str.upper().str.contains("BAJA", na=False)
            cond_canc = df['Estado'].str.upper().str.contains("CANCELADO", na=False)
            df.loc[cond_baja, f'B_{label}'] = 1
            df.loc[cond_canc, f'C_{label}'] = 1
            return df
        except: return pd.DataFrame()

    de = process(URL_ENE, "Ene")
    dt = process(URL_TEL, "Tel")
    da = process(URL_ALA, "Ala")

    # Asegurar métricas de Energía
    if not de.empty:
        de['V_Luz'] = de['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0) if 'CUPS Luz' in de.columns else 0
        de['V_Gas'] = de['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0) if 'CUPS Gas' in de.columns else 0
    
    # Asegurar métricas de Telco
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
    
    # Asegurar métricas de Alarmas
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
            else: st.error("Acceso Denegado")
    st.stop()

# --- NAVEGACIÓN ---
with st.sidebar:
    st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
    menu = st.radio("MENÚ PRINCIPAL", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD Y RANKING (ESTRUCTURA ANTIBLOQUEO) ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        
        all_anos = sorted(list(set(de['Año']) | set(dt['Año']) | set(da['Año'])))
        all_meses = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
        all_coms = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: f_ano = st.selectbox("📅 Año", all_anos, index=len(all_anos)-1 if all_anos else 0)
        with c2: f_meses = st.multiselect("📆 Meses", all_meses, default=[all_meses[-1]] if all_meses else [])
        with c3: f_coms = st.multiselect("👤 Comerciales", all_coms, default=all_coms)

        f_de = de[(de['Año']==f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_coms))] if not de.empty else pd.DataFrame()
        f_dt = dt[(dt['Año']==f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_coms))] if not dt.empty else pd.DataFrame()
        f_da = da[(da['Año']==f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_coms))] if not da.empty else pd.DataFrame()

        t_rank, t_ene, t_tel, t_ala = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_rank:
            st.markdown('<div class="block-header">RANKING DE PRODUCTIVIDAD</div>', unsafe_allow_html=True)
            
            # 1. Crear matriz de ceros para todos los comerciales seleccionados
            rank = pd.DataFrame(index=f_coms)
            cols = ['V_Luz', 'V_Gas', 'V_Fibra', 'V_Móvil', 'V_Alarma', 'B_Ene', 'C_Ene', 'B_Tel', 'C_Tel', 'B_Ala', 'C_Ala']
            for c in cols: rank[c] = 0.0

            # 2. Inyectar datos reales con validación de existencia
            if not f_de.empty:
                sum_e = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'B_Ene', 'C_Ene']].sum()
                rank.update(sum_e)
            if not f_dt.empty:
                sum_t = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'B_Tel', 'C_Tel']].sum()
                rank.update(sum_t)
            if not f_da.empty:
                sum_a = f_da.groupby('Comercial')[['V_Alarma', 'B_Ala', 'C_Ala']].sum()
                rank.update(sum_a)

            # 3. Totales finales
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['BAJAS'] = rank['B_Ene'] + rank['B_Tel'] + rank['B_Ala']
            rank['CANC'] = rank['C_Ene'] + rank['C_Tel'] + rank['C_Ala']
            
            rank = rank.sort_values('TOTAL', ascending=False).reset_index().rename(columns={'index':'Comercial'})

            def style_rank(s):
                if s.name in ['BAJAS', 'CANC']: return ['background-color: #ffcccc; color: #cc0000; font-weight: bold']*len(s)
                if s.name == 'TOTAL': return ['background-color: #d2ff00; color: black; font-weight: bold']*len(s)
                return ['']*len(s)

            st.write(rank[['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Alarma', 'V_Móvil', 'TOTAL', 'BAJAS', 'CANC']].style.apply(style_rank).to_html(), unsafe_allow_html=True)

        # Tabs de detalles individuales
        for tab, d_filt, tit in zip([t_ene, t_tel, t_ala], [f_de, f_dt, f_da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_filt.empty:
                    st.markdown(f'<div class="block-header">ESTADOS {tit}</div>', unsafe_allow_html=True)
                    ca, cb, cc = st.columns(3)
                    s_act = d_filt[d_filt['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    s_baj = d_filt[d_filt['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    s_can = d_filt[d_filt['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    ca.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{s_act}</div></div>', unsafe_allow_html=True)
                    cb.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{s_baj}</div></div>', unsafe_allow_html=True)
                    cc.markdown(f'<div class="status-box" style="background: #333333;"><div class="status-label">CANCELADOS</div><div class="status-value">{s_can}</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error crítico en Dashboard: {e}")

# --- SECCIONES RESTANTES (MANTENIENDO TODO LO QUE FUNCIONABA) ---
elif menu == "🚀 CRM":
    st.header("Herramientas de Venta")
    st.link_button("🔥 MARCADOR VOZ CENTER", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.link_button("💎 CRM INTERNO BASETTE", "https://crm.grupobasette.eu/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifas y Comisiones")
    st.write("Carga de ficheros Excel de Gana, Naturgy y Total.")

elif menu == "⚖️ COMPARADOR":
    st.header("Generador de Estudios de Ahorro")
    st.info("Utilice esta sección para crear el PDF comparativo para el cliente.")

elif menu == "📢 ANUNCIOS":
    st.header("Recursos de Marketing")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"): 
        st.image("anunciosbasette/qr-plan amigo.png", caption="QR Plan Amigo")

elif menu == "📂 REPOSITORIO":
    st.header("Documentación Técnica")
    if os.path.exists("manuales/Manual_Premiumnumber_Agente.pdf"):
        with open("manuales/Manual_Premiumnumber_Agente.pdf", "rb") as f:
            st.download_button("📂 DESCARGAR MANUAL AGENTE", f, file_name="Manual_Basette.pdf")