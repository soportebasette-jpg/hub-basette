import streamlit as st
import os
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime

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

# 3. CARGA DE DATOS CON LIMPIEZA EXTREMA
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
            # LIMPIEZA DE COLUMNAS: Quita espacios y asegura nombres estándar
            df.columns = [str(c).strip() for c in df.columns]
            df['Fecha Creación'] = pd.to_datetime(df['Fecha Creación'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha Creación', 'Comercial'])
            df['Año'] = df['Fecha Creación'].dt.year.astype(str)
            df['Mes'] = df['Fecha Creación'].dt.strftime('%m - %B')
            return df
        except: return pd.DataFrame()
    return process(URL_ENE), process(URL_TEL), process(URL_ALA)

# --- LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
        pwd = st.text_input("Clave:", type="password")
        if st.button("ACCEDER"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
    st.stop()

# --- NAVEGACIÓN ---
with st.sidebar:
    st.image("1000233813.jpg") if os.path.exists("1000233813.jpg") else None
    menu = st.radio("MENÚ", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD Y RANKING ---
if menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        all_anos = sorted(list(set(de['Año']) | set(dt['Año']) | set(da['Año'])))
        all_meses = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
        all_coms = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: f_ano = st.selectbox("Año", all_anos, index=len(all_anos)-1 if all_anos else 0)
        with c2: f_meses = st.multiselect("Meses", all_meses, default=[all_meses[-1]] if all_meses else [])
        with c3: f_coms = st.multiselect("Comerciales", all_coms, default=all_coms)

        f_de = de[(de['Año']==f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_coms))] if not de.empty else pd.DataFrame()
        f_dt = dt[(dt['Año']==f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_coms))] if not dt.empty else pd.DataFrame()
        f_da = da[(da['Año']==f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_coms))] if not da.empty else pd.DataFrame()

        t_rank, t_ene, t_tel, t_ala = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_rank:
            st.markdown('<div class="block-header">RANKING GLOBAL CON ESTADOS DRIVE</div>', unsafe_allow_html=True)
            rank = pd.DataFrame(index=f_coms)
            for col in ['Luz', 'Gas', 'Fibra', 'Móvil', 'Alarma', 'Activos', 'Bajas', 'Cancelados']: rank[col] = 0

            # Conteo Blindado
            for df_actual, tipo in [(f_de, 'E'), (f_dt, 'T'), (f_da, 'A')]:
                if not df_actual.empty:
                    for _, r in df_actual.iterrows():
                        com = r['Comercial']
                        # Productos
                        if tipo == 'E':
                            if 'CUPS Luz' in r and pd.notnull(r['CUPS Luz']): rank.at[com, 'Luz'] += 1
                            if 'CUPS Gas' in r and pd.notnull(r['CUPS Gas']): rank.at[com, 'Gas'] += 1
                        elif tipo == 'T':
                            tipo_t = str(r.get('Tipo Tarifa', '')).lower()
                            if 'fibra' in tipo_t: rank.at[com, 'Fibra'] += 1
                            if 'movil' in tipo_t: rank.at[com, 'Móvil'] += 1
                        elif tipo == 'A': rank.at[com, 'Alarma'] += 1
                        
                        # Estados (Usando .get para evitar KeyError)
                        est = str(r.get('Estado', '')).upper()
                        if "ACTIVO" in est: rank.at[com, 'Activos'] += 1
                        elif "BAJA" in est: rank.at[com, 'Bajas'] += 1
                        elif "CANCELADO" in est: rank.at[com, 'Cancelados'] += 1

            rank['TOTAL_V'] = rank['Luz'] + rank['Gas'] + rank['Fibra'] + rank['Alarma']
            rank['% B+C'] = rank.apply(lambda x: f"{(round(((x['Bajas']+x['Cancelados'])/x['TOTAL_V'])*100,1)) if x['TOTAL_V']>0 else 0.0}%", axis=1)
            rank = rank.sort_values('TOTAL_V', ascending=False).reset_index().rename(columns={'index':'Comercial'})

            def style_r(s):
                if s.name in ['Bajas', 'Cancelados', '% B+C']: return ['background-color: #ffcccc; color: #cc0000; font-weight: bold']*len(s)
                if s.name == 'Activos': return ['background-color: #e6ffed; color: #28a745; font-weight: bold']*len(s)
                if s.name == 'TOTAL_V': return ['background-color: #d2ff00; color: black; font-weight: bold']*len(s)
                return ['']*len(s)

            st.write(rank.style.apply(style_r).to_html(), unsafe_allow_html=True)

        for tab, df_i, tit in zip([t_ene, t_tel, t_ala], [f_de, f_dt, f_da], ["ENERGÍA", "TELCO", "ALARMAS"]):
            with tab:
                if not df_i.empty and 'Estado' in df_i.columns:
                    st.markdown(f'<div class="block-header">ESTADOS {tit}</div>', unsafe_allow_html=True)
                    e_ser = df_i['Estado'].fillna('').str.upper()
                    sa, sb, sc = (e_ser=="ACTIVO").sum(), (e_ser=="BAJA").sum(), (e_ser=="CANCELADO").sum()
                    cl1, cl2, cl3 = st.columns(3)
                    cl1.markdown(f'<div class="status-box" style="background: #1b4d3e;"><div class="status-label">ACTIVOS</div><div class="status-value">{sa}</div></div>', unsafe_allow_html=True)
                    cl2.markdown(f'<div class="status-box" style="background: #990000;"><div class="status-label">BAJAS</div><div class="status-value">{sb}</div></div>', unsafe_allow_html=True)
                    cl3.markdown(f'<div class="status-box" style="background: #000000;"><div class="status-label">CANCELADOS</div><div class="status-value">{sc}</div></div>', unsafe_allow_html=True)

    except Exception as e: st.error(f"Error: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Descargas")
    with st.expander("📂 NATURGY"):
        if os.path.exists("manuales/naturgy"):
            for f_n in os.listdir("manuales/naturgy"):
                if f_n.endswith(".pdf"):
                    with open(f"manuales/naturgy/{f_n}", "rb") as f:
                        st.download_button(f"📄 {f_n}", f, file_name=f_n, key=f_n)
    with st.expander("📂 MANUAL MARCADOR"):
        if os.path.exists("manuales/Manual_Premiumnumber_Agente.pdf"):
            with open("manuales/Manual_Premiumnumber_Agente.pdf", "rb") as f:
                st.download_button("📖 DESCARGAR MANUAL", f, file_name="Manual.pdf")

# --- OTROS ---
elif menu == "🚀 CRM":
    st.link_button("🔥 MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.link_button("💎 CRM", "https://crm.grupobasette.eu/login", use_container_width=True)
elif menu == "📊 PRECIOS": st.info("Ver Repositorio")
elif menu == "⚖️ COMPARADOR": st.header("Estudio Ahorro")
elif menu == "📢 ANUNCIOS":
    if os.path.exists("anunciosbasette/qr-plan amigo.png"): st.image("anunciosbasette/qr-plan amigo.png")