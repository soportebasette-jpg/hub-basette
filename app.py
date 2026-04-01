import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import base64

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- FUNCIÓN PARA LOGO EN BASE64 (Para posicionamiento absoluto) ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. CSS DE ALTA VISIBILIDAD Y POSICIONAMIENTO DE LOGOS
logo_path = "tecomparotodo_logo/tecomparotodo_logo.jpg"
logo_html = ""

if os.path.exists(logo_path):
    bin_str = get_base64_of_bin_file(logo_path)
    logo_html = f"""
    <style>
    /* Logo Arriba Derecha */
    .logo-top-right {{
        position: fixed;
        top: 10px;
        right: 20px;
        width: 150px;
        z-index: 999;
    }}
    /* Logo Abajo Izquierda */
    .logo-bottom-left {{
        position: fixed;
        bottom: 10px;
        left: 20px;
        width: 120px;
        z-index: 999;
    }}
    </style>
    <img src="data:image/png;base64,{bin_str}" class="logo-top-right">
    <img src="data:image/png;base64,{bin_str}" class="logo-bottom-left">
    """

st.markdown(f"""
    {logo_html}
    <style>
    .stApp {{ background-color: #0d1117; color: #ffffff; }}
    header {{ visibility: hidden; }}
    label[data-testid="stWidgetLabel"] p {{
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }}
    button p, .stDownloadButton button p, .stButton button p {{ 
        color: #000000 !important; 
        font-weight: 900 !important; 
    }}
    button, .stDownloadButton button, .stButton button {{ 
        background-color: #ffffff !important; 
        border: 2px solid #d2ff00 !important; 
    }}
    .stTable {{ background-color: white !important; border-radius: 10px; }}
    .stTable td, .stTable th {{ color: #000000 !important; text-align: center !important; }}
    
    .block-header {{
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem;
    }}
    
    .winner-card {{ 
        background: linear-gradient(90deg, #1e3a8a, #3b82f6); 
        padding: 25px; 
        border-radius: 15px; 
        color: white !important; 
        text-align: center; 
        font-weight: bold; 
        font-size: 28px; 
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }}

    .price-card {{
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
        height: 100%;
    }}
    .price-card:hover {{
        border-color: #d2ff00;
        transform: translateY(-5px);
    }}
    .price-title {{ color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }}
    .price-val {{ color: white; font-size: 2rem; font-weight: 900; }}
    .price-sub {{ color: #8b949e; font-size: 0.85rem; margin-bottom: 5px; }}

    span[data-baseweb="tag"] {{
        background-color: #d2ff00 !important;
        border-radius: 5px !important;
    }}
    span[data-baseweb="tag"] span {{
        color: black !important;
        font-weight: bold !important;
    }}

    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {{
        background-color: #161b22 !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS DASHBOARD (Sin cambios) ---
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    df_e = pd.read_csv(URL_ENE)
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    df_t = pd.read_csv(URL_TEL)
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
    return df_e, df_t

tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
]

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
QR_PLAN_AMIGO = "anunciosbasette/qr-plan amigo.png"

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
        pwd = st.text_input("Introduce Clave Comercial:", type="password")
        if st.button("ACCEDER AL HUB"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# 5. NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- LÓGICA DE SECCIONES ---

if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL FORMULARIO", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, {"n": "NIBA", "u": "https://clientes.niba.es/"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">{p["n"]}</h4></div>''', unsafe_allow_html=True)
            st.link_button(f"ENTRAR", p["u"], use_container_width=True)
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="block-header">🛡️ 🚨 ALARMAS</div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://partners.segurma.com/", use_container_width=True)
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        c_t1, c_t2 = st.columns(2)
        with c_t1: st.link_button("ENTRAR O2", "https://o2online.es/auth/login/", use_container_width=True)
        with c_t2: st.link_button("ENTRAR LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        df_precios = pd.DataFrame(tarifas_luz).drop(columns=['logo'])
        st.dataframe(df_precios, use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([{"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"}])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 SOLO FIBRA</div>', unsafe_allow_html=True)
        st.write("300 Mb: 23€ | 600 Mb: 27€ | 1 Gb: 31€")

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    # ... (Lógica de comparador sin cambios solicitados) ...

elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🖼️ MATERIAL PUBLICITARIO</div>', unsafe_allow_html=True)
    
    path_anuncios = "anunciosbasette/"
    if os.path.exists(path_anuncios):
        # LECTURA DINÁMICA DE LA CARPETA
        archivos = [f for f in os.listdir(path_anuncios) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if archivos:
            cols = st.columns(3)
            for idx, archi in enumerate(archivos):
                with cols[idx % 3]:
                    full_p = os.path.join(path_anuncios, archi)
                    st.image(full_p, use_container_width=True, caption=archi)
                    with open(full_p, "rb") as file:
                        st.download_button(f"Descargar {archi}", file, file_name=archi, key=f"an_{idx}")
        else: st.info("No hay imágenes en la carpeta anunciosbasette.")

elif menu == "📈 DASHBOARD Y RANKING":
    # ... (Lógica de Dashboard sin cambios solicitados) ...
    st.header("Dashboard")

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    
    # REPOSITORIO IBERDROLA - RUTA CORREGIDA
    with st.expander("📁 DOCUMENTACIÓN IBERDROLA", expanded=True):
        file_ib = "manuales/PRECIOS_IBERDROLA_31032026.pdf"
        if os.path.exists(file_ib):
            with open(file_ib, "rb") as f:
                st.download_button("📥 DESCARGAR PRECIOS IBERDROLA 31/03/2026", f, file_name="PRECIOS_IBERDROLA_31032026.pdf")
        else:
            st.error(f"No se encuentra el archivo: {file_ib}")

    # RESTO DE MANUALES DINÁMICOS
    for c in ["GANA ENERGÍA", "NATURGY", "TOTAL", "ENDESA", "O2", "LOWI"]:
        with st.expander(f"📁 DOCUMENTACIÓN {c}"):
            if os.path.exists("manuales"):
                busq = c.split()[0].lower()
                archivos = [f for f in os.listdir("manuales") if busq in f.lower() and f.lower().endswith('.pdf')]
                for fn in archivos:
                    with open(f"manuales/{fn}", "rb") as f:
                        st.download_button(f"📥 {fn}", f, file_name=fn, key=f"rep_{fn}")