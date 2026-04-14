import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD (GENERAL)
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

    .price-card {
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
        height: 100%;
    }
    .price-card:hover {
        border-color: #d2ff00;
        transform: translateY(-5px);
    }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.85rem; margin-bottom: 5px; }

    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
        background-color: #161b22 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS DASHBOARD ---
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
    df_e['REF_Ene'] = df_e['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_e.columns else 0
    
    # TELCO
    df_t = pd.read_csv(URL_TEL)
    df_t.columns = df_t.columns.str.strip()
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    df_t['REF_Tel'] = df_t['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_t.columns else 0
    
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

    # ALARMAS
    df_a = pd.read_csv(URL_ALA)
    df_a.columns = df_a.columns.str.strip()
    df_a['Fecha Creación'] = pd.to_datetime(df_a['Fecha Creación'], dayfirst=True, errors='coerce')
    df_a = df_a.dropna(subset=['Comercial', 'Fecha Creación'])
    df_a['Año'] = df_a['Fecha Creación'].dt.year.astype(str)
    df_a['Mes'] = df_a['Fecha Creación'].dt.strftime('%m - %B')
    df_a['V_Alarma'] = 1 
    df_a['REF_Ala'] = df_a['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_a.columns else 0
    
    return df_e, df_t, df_a

# 3. BASE DE DATOS LUZ
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

# (Secciones Intermedias omitidas por brevedad, concentrándonos en el Dashboard solicitado)

# --- DASHBOARD Y RANKING ---
if menu == "📈 DASHBOARD Y RANKING":
    st.balloons() 
    st.markdown("""
        <style>
        .ranking-table-container { background-color: white !important; padding: 10px; border-radius: 10px; overflow-x: auto; }
        div[data-testid="stTable"] table { color: black !important; font-size: 11px !important; }
        div[data-testid="stTable"] th { background-color: #f1f1f1 !important; color: black !important; font-weight: bold !important; }
        div[data-testid="stTable"] td { background-color: white !important; color: black !important; padding: 4px 8px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 Dashboard de Rendimiento y Ranking")
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        
        c_filt_1, c_filt_2, c_filt_3 = st.columns(3)
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año']) | set(df_a['Año'])))
        meses = sorted(list(set(df_e['Mes']) | set(df_t['Mes']) | set(df_a['Mes'])))
        comerciales_lista = sorted(list(set(df_e['Comercial']) | set(df_t['Comercial']) | set(df_a['Comercial'])))
        
        with c_filt_1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_filt_2: f_mes = st.selectbox("📆 Mes", meses, index=len(meses)-1)
        with c_filt_3: f_com = st.multiselect("👤 Comerciales", options=comerciales_lista, default=comerciales_lista)

        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'] == f_mes) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'] == f_mes) & (df_t['Comercial'].isin(f_com))]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'] == f_mes) & (df_a['Comercial'].isin(f_com))]

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'REF_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'REF_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'REF_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            
            rank['VENTAS TOTALES SIN MOVIL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['TOTAL CON MOVIL'] = rank['VENTAS TOTALES SIN MOVIL'] + rank['V_Móvil']
            rank['TOTAL REF'] = rank['REF_Ene'] + rank['REF_Tel'] + rank['REF_Ala']
            rank['OBJETIVO REF'] = 8
            rank['OBJETIVO'] = 25
            rank['FALTAN'] = (rank['OBJETIVO'] - rank['VENTAS TOTALES SIN MOVIL']).clip(lower=0)
            rank['% CONSECUCION'] = ((rank['VENTAS TOTALES SIN MOVIL'] / rank['OBJETIVO']) * 100).fillna(0).astype(int)

            def get_motivacion_html(row):
                perc = row['% CONSECUCION']
                if perc >= 100: return f'<b style="color: green;">🔥 ¡LEYENDA!</b>'
                elif perc >= 80: return f'<b style="color: #2E8B57;">🚀 IMPARABLE</b>'
                elif perc >= 50: return f'<b style="color: #B8860B;">💪 BUEN RITMO</b>'
                else: return f'<b style="color: #FF4500;">🎯 A POR ELLO</b>'
            
            rank['MOTIVACIÓN'] = rank.apply(get_motivacion_html, axis=1)
            rank = rank.sort_values('VENTAS TOTALES SIN MOVIL', ascending=False)

            if not rank.empty:
                # --- FILA DE TOTALES ---
                total_luz = rank['V_Luz'].sum()
                total_gas = rank['V_Gas'].sum()
                total_fibra = rank['V_Fibra'].sum()
                total_movil = rank['V_Móvil'].sum()
                total_alarma = rank['V_Alarma'].sum()
                total_ventas_sin_m = rank['VENTAS TOTALES SIN MOVIL'].sum()
                total_ventas_con_m = rank['TOTAL CON MOVIL'].sum()
                total_faltan = rank['FALTAN'].sum()
                total_ref = rank['TOTAL REF'].sum()

                rank_visual = rank.reset_index()
                
                # Formatear la columna % para visualizar con el símbolo
                rank_visual['%'] = rank_visual['% CONSECUCION'].astype(str) + "%"

                cols_finales = {
                    'Comercial': 'Comercial', 'V_Luz': 'Luz', 'V_Gas': 'Gas', 
                    'V_Fibra': 'Fibra', 'V_Móvil': 'Móvil', 'V_Alarma': 'Alarma', 
                    'VENTAS TOTALES SIN MOVIL': 'TOTAL', 'TOTAL CON MOVIL': 'T+M', 
                    'OBJETIVO': 'OBJ', 'FALTAN': 'FALTA', 
                    'TOTAL REF': 'REF', '%': '%', 'MOTIVACIÓN': 'INFO'
                }
                
                rank_visual = rank_visual[list(cols_finales.keys())].rename(columns=cols_finales)
                for c in ['Luz', 'Gas', 'Fibra', 'Móvil', 'Alarma', 'TOTAL', 'T+M', 'OBJ', 'FALTA', 'REF']:
                    rank_visual[c] = rank_visual[c].astype(int)

                # Mostramos la tabla principal
                st.write(
                    rank_visual.style
                    .map(lambda x: 'background-color: #90EE90;' if x == 0 else 'background-color: #FFCDD2;' if x > 10 else 'background-color: #FFF9C4;', subset=['FALTA'])
                    .set_properties(subset=['TOTAL', 'T+M'], **{'background-color': '#F0F4F8', 'font-weight': 'bold'})
                    .to_html(escape=False, index=False), 
                    unsafe_allow_html=True
                )

                # --- BLOQUE DE TOTALES GLOBALES (ABAJO) ---
                st.markdown(f"""
                <div style="margin-top: 20px; padding: 20px; background-color: #161b22; border: 2px solid #d2ff00; border-radius: 10px;">
                    <h3 style="color: #d2ff00; margin-top: 0; text-align: center;">📊 TOTALES ACUMULADOS DEL EQUIPO</h3>
                    <table style="width: 100%; color: white; text-align: center; border-collapse: collapse;">
                        <tr style="font-size: 1.1rem; border-bottom: 1px solid #30363d;">
                            <th>LUZ</th><th>GAS</th><th>FIBRA</th><th>MÓVIL</th><th>ALARMA</th><th>REF</th>
                        </tr>
                        <tr style="font-size: 1.5rem; font-weight: bold;">
                            <td>{int(total_luz)}</td><td>{int(total_gas)}</td><td>{int(total_fibra)}</td>
                            <td>{int(total_movil)}</td><td>{int(total_alarma)}</td><td>{int(total_ref)}</td>
                        </tr>
                    </table>
                    <div style="display: flex; justify-content: space-around; margin-top: 15px; border-top: 1px solid #30363d; padding-top: 15px;">
                        <div style="text-align: center;">
                            <p style="margin: 0; color: #8b949e;">TOTAL SIN MÓVILES</p>
                            <h2 style="margin: 0; color: #d2ff00;">{int(total_ventas_sin_m)}</h2>
                        </div>
                        <div style="text-align: center;">
                            <p style="margin: 0; color: #8b949e;">FALTAN PARA OBJETIVOS</p>
                            <h2 style="margin: 0; color: #ff4b4b;">{int(total_faltan)}</h2>
                        </div>
                        <div style="text-align: center;">
                            <p style="margin: 0; color: #8b949e;">TOTAL CON MÓVILES</p>
                            <h2 style="margin: 0; color: #3b82f6;">{int(total_ventas_con_m)}</h2>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.warning("No hay datos para esta selección.")

    except Exception as e:
        st.error(f"Error cargando el Dashboard: {e}")

# (Resto de secciones CRM, PRECIOS, COMPARADOR etc. se mantienen igual)
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    # ... tu código de CRM aquí
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    # ... tu código de PRECIOS aquí
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    # ... tu código de COMPARADOR aquí
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("Anuncios")
    # ... tu código de ANUNCIOS aquí
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    # ... tu código de REPOSITORIO aquí