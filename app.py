import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    button p, .stDownloadButton button p, .stButton button p { 
        color: #000000 !important; 
        font-weight: 900 !important; 
    }
    button, .stDownloadButton button, .stButton button { 
        background-color: #ffffff !important; 
        border: 2px solid #d2ff00 !important; 
    }
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    
    .block-header {
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem;
    }
    
    .winner-card { 
        background: linear-gradient(90deg, #1e3a8a, #3b82f6); 
        padding: 25px; 
        border-radius: 15px; 
        color: white !important; 
        text-align: center; 
        font-weight: bold; 
        font-size: 28px; 
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit?usp=drive_link', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_VACACIONES = get_csv_url("https://docs.google.com/spreadsheets/d/1CUma-cn2oHYC1ORWjfNVMi2cexYvJUyvwIN3j_fvyM8/edit?usp=drive_link")

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
    
    def count_t(row):
        f, m = 0, 0
        t = str(row['Tipo Tarifa']).lower()
        if 'fibramovil' in t or ('fibra' in t and 'movil' in t): f, m = 1, 1
        elif 'fibra' in t: f = 1
        elif 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return pd.Series([f, m, f + m])
    
    df_t[['V_Fibra', 'V_Móvil', 'Total_Tel']] = df_t.apply(count_t, axis=1)
    return df_e, df_t

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "📈 DASHBOARD", "📅 AUSENCIAS"], label_visibility="collapsed")

# --- LÓGICA DE SECCIONES ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    # (Aquí iría tu código de botones de CRM que ya tienes)
    st.info("Sección CRM cargada.")

elif menu == "📅 AUSENCIAS":
    st.header("Gestión de Vacaciones")
    
    # 1. MOSTRAR PRÓXIMAS (Corregido para evitar KeyError)
    try:
        df_v = pd.read_csv(URL_VACACIONES)
        # Limpiar nombres de columnas por si acaso hay espacios
        df_v.columns = df_v.columns.str.strip()
        st.subheader("Próximas Salidas")
        st.table(df_v.tail(5)) # Muestra las últimas 5 registradas
    except Exception as e:
        st.error(f"Error cargando el Excel: {e}")

    # 2. FORMULARIO
    with st.form("vacas"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Comercial")
            f_ini = st.date_input("Inicio")
        with col2:
            mot = st.selectbox("Motivo", ["Vacaciones", "Baja", "Asuntos Propios"])
            f_fin = st.date_input("Fin")
        
        # Calcular días
        dias = (f_fin - f_ini).days + 1
        st.write(f"Días totales: {dias}")
        
        btn = st.form_submit_button("REGISTRAR EN EXCEL")
        
        if btn:
            if not os.path.exists("credentials.json"):
                st.error("⚠️ Error: No se encuentra el archivo 'credentials.json' en la carpeta MI_INTRANET.")
            else:
                try:
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                    client = gspread.authorize(creds)
                    # Abrir por el nombre exacto
                    sheet = client.open("SOLICITUDES_VACACIONES_HUB").sheet1
                    
                    fila = [datetime.now().strftime("%d/%m/%Y"), nom, f_ini.strftime("%d/%m/%Y"), f_fin.strftime("%d/%m/%Y"), mot, dias]
                    sheet.append_row(fila)
                    st.success("✅ ¡Registrado con éxito!")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

elif menu == "📈 DASHBOARD":
    st.header("Ranking de Ventas")
    try:
        df_e, df_t = load_and_clean_ranking()
        # Aquí van tus pestañas de Ranking, Energía y Telco
        t1, t2, t3 = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO"])
        with t1:
            st.write("Cargando Ranking...")
            # Lógica de ranking...
    except Exception as e:
        st.error(f"Error en Dashboard: {e}")