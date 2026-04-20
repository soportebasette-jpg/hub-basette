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
    def process(url):
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()
            df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha Creación', 'Comercial'])
            df['Año'] = df['Fecha Creación'].dt.year.astype(str)
            df['Mes'] = df['Fecha Creación'].dt.strftime('%m - %B')
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
            return df
        except: return pd.DataFrame()
    return process(URL_ENE), process(URL_TEL), process(URL_ALA)

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
    st.markdown("---")
    menu = st.radio("Menú Principal:", ["🚀 CRM Y GESTIÓN", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD Y RANKING ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        
        all_anos = sorted(list(set(de['Año']) | set(dt['Año']) | set(da['Año'])))
        all_meses = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
        all_coms = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: f_ano = st.selectbox("📅 Año", all_anos, index=len(all_anos)-1 if all_anos else 0)
        with c2: f_meses = st.multiselect("📆 Meses", all_meses, default=[all_meses[-1]] if all_meses else [])
        with c3: f_coms = st.multiselect("👤 Filtrar Comerciales", all_coms, default=all_coms)

        f_de = de[(de['Año']==f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_coms))] if not de.empty else de
        f_dt = dt[(dt['Año']==f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_coms))] if not dt.empty else dt
        f_da = da[(da['Año']==f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_coms))] if not da.empty else da

        t_rank, t_ene, t_tel, t_ala = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_rank:
            st.markdown('<div class="block-header">RANKING DE VENTAS Y ESTADOS</div>', unsafe_allow_html=True)
            
            rank = pd.DataFrame(index=f_coms)
            for c in ['Luz', 'Gas', 'Fibra', 'Móvil', 'Alarma', 'Activos', 'Bajas', 'Cancelados']: rank[c] = 0

            # Proceso manual blindado
            datasets = [f_de, f_dt, f_da]
            for i, df_f in enumerate(datasets):
                if not df_f.empty:
                    for _, r in df_f.iterrows():
                        com = r['Comercial']
                        if i == 0: # Energía
                            if 'CUPS Luz' in r and pd.notnull(r['CUPS Luz']): rank.at[com, 'Luz'] += 1
                            if 'CUPS Gas' in r and pd.notnull(r['CUPS Gas']): rank.at[com, 'Gas'] += 1
                        elif i == 1: # Telco
                            tipo = str(r.get('Tipo Tarifa', '')).lower()
                            if 'fibra' in tipo: rank.at[com, 'Fibra'] += 1
                            if 'movil' in tipo: rank.at[com, 'Móvil'] += 1
                        elif i == 2: # Alarmas
                            rank.at[com, 'Alarma'] += 1
                        
                        # Conteo de estados
                        est = str(r['Estado']).upper()
                        if "ACTIVO" in est: rank.at[com, 'Activos'] += 1
                        elif "BAJA" in est: rank.at[com, 'Bajas'] += 1
                        elif "CANCELADO" in est: rank.at[com, 'Cancelados'] += 1

            rank['TOTAL_V'] = rank['Luz'] + rank['Gas'] + rank['Fibra'] + rank['Alarma']
            # Cálculo de % (Bajas + Canc) / Total Ventas
            rank['% B+C'] = ((rank['Bajas'] + rank['Cancelados']) / rank['TOTAL_V'].replace(0, 1) * 100).round(1).astype(str) + '%'
            
            rank = rank.sort_values('TOTAL_V', ascending=False).reset_index().rename(columns={'index':'Comercial'})

            def style_ranking(s):
                if s.name in ['Bajas', 'Cancelados', '% B+C']: return ['background-color: #ffcccc; color: #cc0000; font-weight: bold']*len(s)
                if s.name == 'Activos': return ['background-color: #e6ffed; color: #28a745; font-weight: bold']*len(s)
                if s.name == 'TOTAL_V': return ['background-color: #d2ff00; color: black; font-weight: bold']*len(s)
                return ['']*len(s)

            st.write(rank.style.apply(style_ranking).to_html(), unsafe_allow_html=True)

        for tab, d_filt, tit in zip([t_ene, t_tel, t_ala], [f_de, f_dt, f_da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not d_filt.empty:
                    st.markdown(f'<div class="block-header">ANÁLISIS {tit}</div>', unsafe_allow_html=True)
                    s_a = d_filt[d_filt['Estado'].str.upper().str.contains("ACTIVO", na=False)].shape[0]
                    s_b = d_filt[d_filt['Estado'].str.upper().str.contains("BAJA", na=False)].shape[0]
                    s_c = d_filt[d_filt['Estado'].str.upper().str.contains("CANCELADO", na=False)].shape[0]
                    col_s1, col_s2, col_s3 = st.columns(3)
                    col_s1.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{s_a}</div></div>', unsafe_allow_html=True)
                    col_s2.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{s_b}</div></div>', unsafe_allow_html=True)
                    col_s3.markdown(f'<div class="status-box" style="background: #000000;"><div class="status-label">CANCELADOS</div><div class="status-value">{s_c}</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Centro de Documentación")
    
    with st.expander("📂 NATURGY - DOCUMENTACIÓN OFICIAL"):
        # Aseguramos que la ruta existe o informamos
        path_nat = "manuales/naturgy" 
        if os.path.exists(path_nat):
            for file in os.listdir(path_nat):
                if file.endswith(".pdf"):
                    with open(os.path.join(path_nat, file), "rb") as f:
                        st.download_button(f"📄 Descargar {file}", f, file_name=file, key=file)
        else:
            st.warning("La carpeta 'manuales/naturgy' no se encuentra en el servidor.")

    with st.expander("📂 MANUAL MARCADOR"):
        m_path = "manuales/Manual_Premiumnumber_Agente.pdf"
        if os.path.exists(m_path):
            with open(m_path, "rb") as f:
                st.download_button("📖 DESCARGAR MANUAL MARCADOR", f, file_name="Manual_Marcador.pdf")

    with st.expander("📁 DOCUMENTACIÓN LOWI"):
        l_path = "manuales/TARIFAS_LOWI_MARZO2026.pdf"
        if os.path.exists(l_path):
            with open(l_path, "rb") as f:
                st.download_button("📄 TARIFAS LOWI", f, file_name="Tarifas_Lowi.pdf")

# --- OTRAS SECCIONES (COMPLETAS) ---
elif menu == "🚀 CRM Y GESTIÓN":
    st.header("Accesos a Portales")
    c_c1, c_c2 = st.columns(2)
    with c_c1: st.link_button("🔥 MARCADOR VOZ CENTER", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    with c_c2: st.link_button("💎 CRM BASETTE", "https://crm.grupobasette.eu/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tablas de Precios")
    st.info("Consulte los PDFs en el repositorio para ver los precios actualizados.")

elif menu == "⚖️ COMPARADOR":
    st.header("Generador de Estudios")
    st.write("Complete los datos de la factura para generar el ahorro.")

elif menu == "📢 ANUNCIOS":
    st.header("Material Marketing")
    if os.path.exists("anunciosbasette/qr-plan amigo.png"):
        st.image("anunciosbasette/qr-plan amigo.png")