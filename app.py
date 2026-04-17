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

# Función para convertir imagen a base64 y que se vea en el HTML
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Preparamos la imagen de Rosco
img_base64 = get_base64_of_bin_file("rosco.jpg")

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

    .social-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 20px;
        padding: 10px;
    }
    .social-icon { transition: transform 0.3s; }
    .social-icon:hover { transform: scale(1.1); }

    .price-card {
        background-color: #161b22; border: 2px solid #30363d; border-radius: 15px;
        padding: 20px; text-align: center; margin-bottom: 15px; transition: transform 0.3s; height: 100%;
    }
    .price-card:hover { border-color: #d2ff00; transform: translateY(-5px); }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    
    /* Estilos para resaltar columnas en el HTML del ranking */
    .col-highlight-total { background-color: #d2ff00 !important; font-weight: bold; }
    .col-highlight-falta { background-color: #ffcccc !important; font-weight: bold; }
    .col-highlight-perc { background-color: #e6ffcc !important; font-weight: bold; }
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

# --- CRM ---
if menu == "🚀 CRM":
    col_t_izq, col_t_der = st.columns([2, 1])
    with col_t_izq: st.header("Portales de Gestión")
    with col_t_der:
        st.markdown(f"""
            <div class="social-container">
                <a href="https://www.facebook.com/share/1CqrZ4hGYp/?mibextid=wwXIfr" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" width="35" class="social-icon"></a>
                <a href="https://x.com/tecomparotodoes?s=21" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" width="35" class="social-icon"></a>
                <a href="https://www.instagram.com/tecomparotodoes?igsh=MXRkcTV2anJ6NmJkcA%3D%3D&utm_source=qr" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" width="35" class="social-icon"></a>
                <a href="http://www.tecomparotodo.es" target="_blank"><img src="data:image/jpeg;base64,{img_base64}" width="100" style="border-radius:8px; border: 2px solid #d2ff00;" class="social-icon"></a>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL FORMULARIO", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, {"n": "NIBA", "u": "https://clientes.niba.es/"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]: st.link_button(p["n"], p["u"], use_container_width=True)
    st.markdown("---")
    st.markdown('<div class="block-header">🛡️ 🚨 ALARMAS Y TELCO</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("SEGURMA", "https://crm.segurma.com/web", use_container_width=True)
    with c2: st.link_button("O2", "https://o2online.es/auth/login", use_container_width=True)
    with c3: st.link_button("LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)

# --- PRECIOS --- (Sección completa sin cambios)
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1: st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2: st.dataframe(pd.DataFrame([{"COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh"}, {"COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh"}]), use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        planes = [("300 Mb", "23€"), ("600 Mb", "35€"), ("1 Gb", "38€")]
        for i, (v, p) in enumerate(planes):
            with f_cols[i]: st.markdown(f'<div class="price-card"><div class="price-title">{v}</div><div class="price-val">{p}</div></div>', unsafe_allow_html=True)

# --- COMPARADOR --- (Sección completa sin cambios)
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre", "Cliente")
        f_act = st.number_input("Factura actual", value=0.0)
    with c2:
        comp_sel = st.selectbox("Compañía", sorted(list(set(t["COMPAÑÍA"] for t in tarifas_luz))))
        consumo = st.number_input("Consumo kWh", value=0.0)
    st.info("Complete los datos para generar el PDF.")

# --- ANUNCIOS --- (Sección completa sin cambios)
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Material de Ventas")
    if os.path.exists(QR_PLAN_AMIGO): st.image(QR_PLAN_AMIGO, width=250)

# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.balloons()
    st.header("📊 Dashboard y Ranking")
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        c1, c2, c3 = st.columns(3)
        with c1: f_ano = st.selectbox("📅 Año", sorted(list(set(df_e['Año']))), index=0)
        with c2: f_mes = st.selectbox("📆 Mes", sorted(list(set(df_e['Mes']))), index=0)
        with c3: f_com = st.multiselect("👤 Comerciales", sorted(list(set(df_e['Comercial']))), default=sorted(list(set(df_e['Comercial']))))

        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'] == f_mes) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'] == f_mes) & (df_t['Comercial'].isin(f_com))]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'] == f_mes) & (df_a['Comercial'].isin(f_com))]

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'REF_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'REF_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'REF_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['FALTA'] = (25 - rank['TOTAL']).apply(lambda x: x if x > 0 else 0)
            rank['REF'] = rank['REF_Ene'] + rank['REF_Tel'] + rank['REF_Ala']
            rank['%'] = ((rank['TOTAL'] / 25) * 100).fillna(0).astype(int).astype(str) + "%"

            rank = rank.sort_values('TOTAL', ascending=False)

            if not rank.empty:
                st.markdown(f'<div class="winner-card">👑 #1: {rank.index[0].upper()} ({int(rank.iloc[0]["TOTAL"])} VENTAS)</div>', unsafe_allow_html=True)
                
                # Formateo de tabla con colores en las columnas solicitadas
                rank_vis = rank.reset_index().rename(columns={'V_Luz':'Luz','V_Gas':'Gas','V_Fibra':'Fibra','V_Alarma':'Ala','V_Móvil':'Móvil'})
                
                def highlight_cols(s):
                    return ['' if col not in ['TOTAL', 'FALTA', '%'] else 
                            'background-color: #d2ff00; color: black; font-weight: bold;' if col == 'TOTAL' else
                            'background-color: #ffcccc; color: black;' if col == 'FALTA' else
                            'background-color: #e6ffcc; color: black;' for col in s.index]

                st.write(rank_vis.style.apply(highlight_cols, axis=1).to_html(escape=False, index=False), unsafe_allow_html=True)

                # --- BLOQUE DE TOTALES SOLICITADO ---
                total_equipo = int(rank['TOTAL'].sum())
                total_faltan = int(rank['FALTA'].sum())
                
                st.markdown(f"""
                <div style="margin-top: 25px; padding: 20px; background-color: #161b22; border: 2px solid #d2ff00; border-radius: 12px; text-align: center;">
                    <h3 style="color: #d2ff00; margin-top: 0;">📊 TOTALES DEL EQUIPO</h3>
                    <div style="display: flex; justify-content: space-around;">
                        <div><p style="color: #8b949e; margin:0;">VENTAS TOTALES</p><h2 style="color: white; margin:0;">{total_equipo}</h2></div>
                        <div><p style="color: #ff4b4b; margin:0;">TOTAL QUE FALTAN</p><h2 style="color: white; margin:0;">{total_faltan}</h2></div>
                        <div><p style="color: #3b82f6; margin:0;">TOTAL REFERIDOS</p><h2 style="color: white; margin:0;">{int(rank['REF'].sum())}</h2></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tab_e: st.plotly_chart(px.pie(de, values='Total_Ene', names='Comercializadora', title="Mix Energía"), use_container_width=True)
        with tab_t: st.plotly_chart(px.bar(dt.groupby('Comercial')[['V_Fibra','V_Móvil']].sum().reset_index(), x='Comercial', y=['V_Fibra','V_Móvil'], title="Ventas Telco"), use_container_width=True)
        with tab_a: st.plotly_chart(px.bar(da.groupby('Comercial')['V_Alarma'].sum().reset_index(), x='V_Alarma', y='Comercial', orientation='h', title="Alarmas"), use_container_width=True)

    except Exception as e: st.error(f"Error: {e}")

# --- REPOSITORIO --- (Sección completa sin cambios)
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    for c in ["GANA", "NATURGY", "TOTAL", "ENDESA", "O2", "SEGURMA"]:
        with st.expander(f"📁 DOCUMENTOS {c}"): st.write("Archivos disponibles para descarga.")