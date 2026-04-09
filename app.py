import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

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

# --- FUNCIONES DE CARGA ---
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
    # Corregido: Referidos Energía
    df_e['REF_Ene'] = df_e['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_e.columns else 0
    
    # TELCO
    df_t = pd.read_csv(URL_TEL)
    df_t.columns = df_t.columns.str.strip()
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    # Corregido: Referidos Telco
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
    # Corregido: Referidos Alarma
    df_a['REF_Ala'] = df_a['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_a.columns else 0
    
    return df_e, df_t, df_a

# --- LOGIN (Simpificado para espacio) ---
LOGO_PRINCIPAL = "1000233813.jpg"
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    pwd = st.text_input("Introduce Clave Comercial:", type="password")
    if st.button("ACCEDER"):
        if pwd == "Ventas2024*":
            st.session_state["password_correct"] = True
            st.rerun()
    st.stop()

# 5. NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- DASHBOARD Y RANKING (SECCIÓN ACTUALIZADA) ---
if menu == "📈 DASHBOARD Y RANKING":
    st.header("📊 Dashboard de Rendimiento y Ranking")
    
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        
        # Filtros
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año']) | set(df_a['Año'])))
        meses = sorted(list(set(df_e['Mes']) | set(df_t['Mes']) | set(df_a['Mes'])))
        
        c_f1, c_f2 = st.columns(2)
        with c_f1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_f2: f_mes = st.selectbox("📆 Mes", meses, index=len(meses)-1)

        # Filtrado
        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'] == f_mes)]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'] == f_mes)]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'] == f_mes)]

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            # Agrupar datos
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'REF_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'REF_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'REF_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            
            # Cálculos finales solicitados
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['T+M'] = rank['TOTAL'] + rank['V_Móvil']
            rank['REF'] = rank['REF_Ene'] + rank['REF_Tel'] + rank['REF_Ala']
            rank['OBJ'] = 25
            rank['OBJ REF'] = 8
            rank['FALTA'] = (rank['OBJ'] - rank['TOTAL']).apply(lambda x: x if x > 0 else 0)
            rank['%'] = (rank['TOTAL'] / rank['OBJ'] * 100).round(0).astype(int)

            rank = rank.sort_values('TOTAL', ascending=False).reset_index()

            # Estilo de Semáforo
            def style_color(val, type='progreso'):
                if type == 'faltan':
                    if val <= 5: color = '#90EE90' # Verde (Cerca del objetivo)
                    elif val <= 15: color = '#FFFFE0' # Amarillo
                    else: color = '#FFCCCB' # Rojo (Lejos)
                elif type == 'ref':
                    if val >= 8: color = '#90EE90'
                    elif val >= 4: color = '#FFFFE0'
                    else: color = '#FFCCCB'
                elif type == 'perc':
                    if val >= 80: color = '#90EE90'
                    elif val >= 40: color = '#FFFFE0'
                    else: color = '#FFCCCB'
                return f'background-color: {color}; color: black; font-weight: bold'

            # Iconos de medallas
            rank.insert(0, 'Pos', [("🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "⭐") for i in range(len(rank))])
            
            # Formatear el % para visualización
            rank['%_str'] = rank['%'].astype(str) + "%"

            # Columnas a mostrar
            display_cols = ['Pos', 'Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Móvil', 'V_Alarma', 'TOTAL', 'T+M', 'OBJ', 'FALTA', 'REF', 'OBJ REF', '%_str']
            
            # Renombrar para compactar tabla
            final_df = rank[display_cols].rename(columns={
                'V_Luz': 'Luz', 'V_Gas': 'Gas', 'V_Fibra': 'Fibra', 'V_Móvil': 'Móvil', 
                'V_Alarma': 'Alarma', '%_str': '%'
            })

            # Mostrar Ganador
            if not rank.empty:
                st.markdown(f'<div class="winner-card">👑 #1: {rank.iloc[0]["Comercial"]}</div>', unsafe_allow_html=True)

            # Aplicar Estilos y mostrar tabla completa
            st.table(
                final_df.style
                .map(lambda x: style_color(x, 'faltan'), subset=['FALTA'])
                .map(lambda x: style_color(x, 'ref'), subset=['REF'])
                .map(lambda x: style_color(int(x.replace('%','')), 'perc'), subset=['%'])
            )

        # (Resto de pestañas ENE, TEL, ALA se mantienen igual pero con sus datos filtrados)
        with tab_e:
            if not de.empty: st.plotly_chart(px.bar(de.groupby('Comercial')['Total_Ene'].sum().reset_index(), x='Total_Ene', y='Comercial', orientation='h', title="Ventas Energía"), use_container_width=True)
        with tab_t:
            if not dt.empty: st.plotly_chart(px.bar(dt.groupby('Comercial')['Total_Tel'].sum().reset_index(), x='Comercial', y='Total_Tel', title="Ventas Telco"), use_container_width=True)
        with tab_a:
            if not da.empty: st.plotly_chart(px.bar(da.groupby('Comercial')['V_Alarma'].sum().reset_index(), x='Comercial', y='V_Alarma', title="Ventas Alarmas"), use_container_width=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# El resto del código (CRM, Precios, Repositorio) sigue igual después de esto...
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    # ... (Tu código de CRM actual)
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    # ... (Tu código de Precios actual)
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    # ... (Tu código de Repositorio actual)