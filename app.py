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
    .social-icon {
        transition: transform 0.3s;
    }
    .social-icon:hover {
        transform: scale(1.1);
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

    span[data-baseweb="tag"] {
        background-color: #d2ff00 !important;
        border-radius: 5px !important;
    }
    span[data-baseweb="tag"] span {
        color: black !important;
        font-weight: bold !important;
    }

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

# 3. BASE DE DATOS LUZ - PRECIOS ACTUALIZADOS GANA ENERGÍA
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.119, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,171/0,104/0,08", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
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
            if pwd == "Ventas2026*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# 5. NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.sidebar.radio(
    "Navegación",
    ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR LUZ", "⚖️ COMPARADOR GAS", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO", "🕒 CONTROL LABORAL"]
)

# --- CRM ---
if menu == "🚀 CRM":
    col_t_izq, col_t_der = st.columns([2, 1])
    with col_t_izq:
        st.header("Portales de Gestión")
    with col_t_der:
        st.markdown(f"""
            <div class="social-container">
                <a href="https://www.facebook.com/profile.php?id=61589358886498" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" width="35" class="social-icon">
                </a>
                <a href="https://x.com/tecomparotodo" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" width="35" class="social-icon">
                </a>
                <a href="https://www.instagram.com/tecomparotodo/" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" width="35" class="social-icon">
                </a>
                <a href="https://www.tiktok.com/@tecomparotodo?_r=1&_t=ZN-95nfhnoUU9W" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/3046/3046121.png" width="35" class="social-icon">
                </a>
                <a href="http://www.tecomparotodo.es" target="_blank">
                    <img src="data:image/jpeg;base64,{img_base64}" width="100" style="border-radius:8px; border: 2px solid #d2ff00;" class="social-icon">
                </a>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid #d2ff00; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">REGISTRO DE JORNADA</h4></div>''', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL FORMULARIO", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)
    
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid #d2ff00; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">MARCADOR PRINCIPAL</h4></div>''', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    # Lista modificada: Se unificaron los portales de total en uno solo llamado "TOTAL ENERGY"
    energia = [
        {"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, 
        {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, 
        {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, 
        {"n": "TOTAL ENERGY", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, 
        {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, 
        {"n": "NIBA", "u": "https://clientes.niba.es/"}, 
        {"n": "ENDESA", "u": "https://inergia.app"}
    ]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">{p["n"]}</h4></div>''', unsafe_allow_html=True)
            st.link_button(f"ENTRAR", p["u"], use_container_width=True)
    
    st.markdown("---")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="block-header">🛡️ 🚨 ALARMAS</div>', unsafe_allow_html=True)
        # Distribución en 2 columnas dentro de Alarmas para añadir el nuevo portal 3D
        c_al1, c_al2 = st.columns(2)
        with c_al1:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">SEGURMA</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR", "https://crm.segurma.com/web#action=619&cids=1&menu_id=200&model=sale.order&view_type=list", use_container_width=True)
        with c_al2:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">3D</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR", "https://www.3dseguridad.es/reportes/menu.php", use_container_width=True)
            
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">O2</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR O2", "https://o2online.es/auth/login/?next=%2Fventas%2F&type=retail", use_container_width=True)
        with c_t2:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">LOWI</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)

# --- PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    # Nueva estructura de pestañas: LUZ Y GAS, TELECOMUNICACIONES, ALARMAS
    t1, t2, t3 = st.tabs(["⚡ LUZ Y GAS", "📶 TELECOMUNICACIONES", "🛡️ ALARMAS"])
    
    with t1:
        st.markdown('<div class="block-header">⚡ LUZ Y GAS</div>', unsafe_allow_html=True)
        # Asegúrate de guardar la imagen como 'tarifas_visuales/luz_gas.jpg'
        st.image("tarifas_visuales/luz_gas.jpg", use_container_width=True)

    with t2:
        st.markdown('<div class="block-header">📶 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        
        st.subheader("LOWI")
        # Asegúrate de guardar la imagen como 'tarifas_visuales/lowi.jpg'
        st.image("tarifas_visuales/lowi.jpg", use_container_width=True)
        
        st.divider()
        
        st.subheader("O2")
        # Asegúrate de guardar la imagen como 'tarifas_visuales/o2.jpg'
        st.image("tarifas_visuales/o2.jpg", use_container_width=True)

    with t3:
        st.markdown('<div class="block-header">🛡️ ALARMAS</div>', unsafe_allow_html=True)
        
        st.subheader("SEGURMA")
        # Asegúrate de guardar la imagen como 'tarifas_visuales/segurma.jpg'
        st.image("tarifas_visuales/segurma.jpg", use_container_width=True)
        st.markdown('<div style="background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5rem;">PRIMEROS 12 MESES POR 19.90€</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("3D ALARMAS")
        # Asegúrate de guardar la imagen como 'tarifas_visuales/3d.jpg'
        st.image("tarifas_visuales/3d.jpg", use_container_width=True)
        st.markdown('<div style="background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5rem;">PRIMEROS 12 MESES POR 24.20€</div>', unsafe_allow_html=True)

# --- COMPARADOR GAS ---
elif menu == "⚖️ COMPARADOR GAS":
    st.header("Estudio de Ahorro de Gas Personalizado")

    # 1. BASE DE DATOS ACTUALIZADA
    tarifas_gas = [
        {"COMPAÑÍA": "NATURGY", "TARIFA": "GAS RL.1 (3.1)", "FIJO": 5.34, "ENERGIA": 0.0840, "logo": "manuales/logo_naturgy.png"},
        {"COMPAÑÍA": "NATURGY", "TARIFA": "GAS RL.2 (3.2)", "FIJO": 10.03, "ENERGIA": 0.0810, "logo": "manuales/logo_naturgy.png"},
        {"COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "GAS RL.1 (3.1)", "FIJO": 4.95, "ENERGIA": 0.0700, "logo": "manuales/logo_gana.png"},
        {"COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "GAS RL.2 (3.2)", "FIJO": 9.50, "ENERGIA": 0.0700, "logo": "manuales/logo_gana.png"},
        {"COMPAÑÍA": "TOTALENERGIES", "TARIFA": "GAS RL.1 (TOTAL)", "FIJO": 5.43, "ENERGIA": 0.0500, "logo": "manuales/logo_totalenergy.png"},
        {"COMPAÑÍA": "TOTALENERGIES", "TARIFA": "GAS RL.2 (TOTAL)", "FIJO": 14.50, "ENERGIA": 0.0580, "logo": "manuales/logo_totalenergy.png"},
    ]

    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre del cliente", "Nombre Apellidos")
        f_act = st.number_input("Factura actual con IVA (EUR)", value=0.0, key="gas_f_act")
        dias_factura = st.number_input("Días del periodo de factura", value=30, key="gas_dias")
        alquiler_contador = st.number_input("Alquiler de contador (EUR/mes)", value=0.69)
        iva_sel = st.selectbox("IVA a aplicar (%)", [21, 10], index=0, key="gas_iva")
        iva_factor = 1 + (iva_sel / 100)
    
    with c2:
        comp_sel = st.selectbox("Compañía Propuesta", sorted(list(set(t["COMPAÑÍA"] for t in tarifas_gas))), key="gas_comp")
        tarifas_f = [t["TARIFA"] for t in tarifas_gas if t["COMPAÑÍA"] == comp_sel]
        tarifa_sel_nombre = st.selectbox("Tarifa Seleccionada", tarifas_f, key="gas_tarifa")
        
        sel = next((t for t in tarifas_gas if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tarifa_sel_nombre), tarifas_gas[0])

        if os.path.exists(sel["logo"]): 
            st.image(sel["logo"], width=150)
        
        consumo_kwh = st.number_input("Consumo total del periodo (kWh)", value=0.0, key="gas_kwh")

    # --- CÁLCULOS ---
    p_fijo_mensual = float(sel['FIJO'])
    p_energia_kwh = float(sel['ENERGIA'])
    imp_hidrocarburos = consumo_kwh * 0.00234
    
    coste_fijo_periodo = (p_fijo_mensual / 30) * dias_factura
    coste_variable_periodo = consumo_kwh * p_energia_kwh
    coste_alquiler_periodo = (alquiler_contador / 30) * dias_factura
    
    subtotal = coste_fijo_periodo + coste_variable_periodo + imp_hidrocarburos + coste_alquiler_periodo
    coste_total_iva = subtotal * iva_factor
    ahorro = f_act - coste_total_iva

    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)
    
    if st.button("GENERAR ESTUDIO PDF"):
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # --- LÓGICA DE LOGO PRINCIPAL (JPG) ---
            # Probamos las dos ubicaciones posibles con la extensión correcta .jpg
            logo_principal = None
            opciones_logo = ["manuales/tecomparotodo_logo.jpg", "tecomparotodo_logo.jpg"]
            
            for ruta in opciones_logo:
                if os.path.exists(ruta):
                    logo_principal = ruta
                    break
            
            if logo_principal:
                # Ubicado arriba a la izquierda
                pdf.image(logo_principal, 10, 8, 45)
            else:
                st.error("No se encuentra el archivo tecomparotodo_logo.jpg")
            
            # Logo de la compañía (Derecha)
            if os.path.exists(sel["logo"]): 
                pdf.image(sel["logo"], 160, 8, 35)
            
            pdf.ln(30)
            pdf.set_font("Arial", "B", 18)
            pdf.cell(190, 10, "ESTUDIO COMPARATIVO DE GAS", ln=True, align="C")
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(190, 8, f" DATOS DEL CLIENTE: {cliente.upper()}", ln=True, fill=True)
            
            pdf.set_font("Arial", "", 10)
            pdf.cell(95, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", border=1)
            pdf.cell(95, 8, f"Periodo: {dias_factura} dias", border=1, ln=True)
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(190, 8, " DETALLE DE LA PROPUESTA", ln=True, fill=True)
            
            items_pdf = [
                ("Compania", comp_sel),
                ("Tarifa", tarifa_sel_nombre),
                ("Termino Fijo", f"{p_fijo_mensual:.2f} EUR/mes"),
                ("Termino Energia", f"{p_energia_kwh:.4f} EUR/kWh"),
                ("Imp. Hidrocarburos", f"{imp_hidrocarburos:.2f} EUR"),
                ("Alquiler Contador", f"{coste_alquiler_periodo:.2f} EUR"),
                ("Consumo", f"{consumo_kwh} kWh")
            ]
            
            pdf.set_font("Arial", "", 10)
            for d, v in items_pdf:
                pdf.cell(95, 8, d, border=1)
                pdf.cell(95, 8, str(v), border=1, ln=True)
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(95, 10, "Factura Actual", border=1)
            pdf.cell(95, 10, f"{f_act:.2f} EUR", border=1, ln=True)
            pdf.cell(95, 10, f"Nueva Factura ({iva_sel}%)", border=1)
            pdf.cell(95, 10, f"{coste_total_iva:.2f} EUR", border=1, ln=True)
            
            pdf.ln(5)
            pdf.set_fill_color(210, 255, 0)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(190, 15, f"AHORRO ESTIMADO: {ahorro:.2f} EUR", ln=True, align="C", fill=True)
            
            pdf_data = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 DESCARGAR ESTUDIO PDF", data=pdf_data, file_name=f"Estudio_Gas_{cliente}.pdf")
            
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")

# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🎁 PLAN AMIGO Y FORMULARIOS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("QR Plan Amigo")
        # Ajustado al nombre exacto de tu imagen
        qr_plan = "anunciosbasette/qr-plan amigo.png"
        if os.path.exists(qr_plan):
            st.image(qr_plan, width=200)
            with open(qr_plan, "rb") as file:
                st.download_button("Descargar QR Plan Amigo", file, "qr-plan-amigo.png")
        else:
            st.error(f"No encontrado: {qr_plan}")

    with col2:
        st.subheader("QR Formulario Web")
        # Ajustado al nombre exacto de tu imagen (revisa la extensión .jpeg)
        qr_form = "anunciosbasette/QR FORMULARIO.jpeg"
        if os.path.exists(qr_form):
            st.image(qr_form, width=200)
            with open(qr_form, "rb") as file:
                st.download_button("Descargar QR Formulario", file, "qr-formulario.jpeg")
        else:
            st.error(f"No encontrado: {qr_form}")

    st.markdown('<div class="block-header">🖼️ MATERIAL PUBLICITARIO</div>', unsafe_allow_html=True)
    st.write("Visualiza y descarga los últimos anuncios:")
    
    path_anuncios = "anunciosbasette/"
    # Lista actualizada con los nombres exactos de tu imagen
    lista_anuncios = [
        {"file": "ahorro facil dazon total.png", "name": "Ahorro Fácil Dazon"},
        {"file": "tarifa solar actualizada 250526.png", "name": "Tarifa Solar"},
        {"file": "tarifas actualizadas 250526 energia.png", "name": "Tarifas Energía"},
        {"file": "tecomparotodolowi_1(1).png", "name": "Tarifas Lowi"},
        {"file": "tecomparotodoo2.png", "name": "Tarifas O2"},
        {"file": "verano plan amigo.jpeg", "name": "Verano Plan Amigo"}
    ]
    
    cols_anuncios = st.columns(3)
    for idx, item in enumerate(lista_anuncios):
        with cols_anuncios[idx % 3]:
            full_path = f"{path_anuncios}{item['file']}"
            if os.path.exists(full_path):
                st.image(full_path, use_container_width=True)
                with open(full_path, "rb") as f_anuncio:
                    st.download_button(
                        label=f"📥 {item['name']}",
                        data=f_anuncio.read(),
                        file_name=item['file'],
                        mime="image/png" if item['file'].lower().endswith('.png') else "image/jpeg",
                        key=f"btn_anuncio_{idx}"
                    )
            else:
                st.warning(f"Falta: {item['file']}")

# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        # Función para cargar datos desde Google Sheets en tiempo real
        def load_and_clean_ranking():
            # Estos son tus enlaces convertidos a formato CSV de descarga directa
            urls = {
                "de": "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv",
                "dt": "https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/export?format=csv",
                "da": "https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/export?format=csv"
            }
            dfs = []
            for url in urls.values():
                try:
                    df = pd.read_csv(url)
                    df.columns = df.columns.str.strip() # Limpiar espacios en nombres
                    dfs.append(df)
                except Exception:
                    dfs.append(pd.DataFrame()) # Si falla, devuelve vacío para no romper
            return dfs[0], dfs[1], dfs[2]

        st.balloons()

        # Frases diarias
        frases = {1: "¡Hoy es un gran día!", 2: "Tu esfuerzo es el éxito.", 3: "Vamos a por todas."}
        st.markdown(f'<h1 style="text-align:center; color:#d2ff00;">{frases.get(datetime.now().day % 3 + 1, "¡A por el objetivo!")}</h1>', unsafe_allow_html=True)

        de, dt, da = load_and_clean_ranking()

        # Filtros
        c_filtros, c_video = st.columns([2, 1])
        with c_filtros:
            meses_disp = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes']))) if 'Mes' in de.columns else []
            f_mes = st.multiselect("Mes:", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
            coms_disp = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial']))) if 'Comercial' in de.columns else []
            f_coms = st.multiselect("Comerciales:", coms_disp, default=coms_disp)

        with c_video:
            if os.path.exists("WhatsApp Video 2026-04-28 at 00.31.03.mp4"):
                st.video("WhatsApp Video 2026-04-28 at 00.31.03.mp4")

        # Procesamiento
        f_de = de[(de['Mes'].isin(f_mes)) & (de['Comercial'].isin(f_coms))] if 'Mes' in de.columns else de
        f_dt = dt[(dt['Mes'].isin(f_mes)) & (dt['Comercial'].isin(f_coms))] if 'Mes' in dt.columns else dt
        f_da = da[(da['Mes'].isin(f_mes)) & (da['Comercial'].isin(f_coms))] if 'Mes' in da.columns else da

        r1 = f_de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum() if not f_de.empty else pd.DataFrame()
        r2 = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum() if not f_dt.empty else pd.DataFrame()
        r3 = f_da.groupby('Comercial')[['V_Alarma']].sum() if not f_da.empty else pd.DataFrame()
        
        rank = pd.concat([r1, r2, r3], axis=1).fillna(0)
        rank['Total Neto'] = rank.sum(axis=1)

        # Nº1 en Ventas
        if not rank.empty:
            top = rank.sort_values('Total Neto', ascending=False).iloc[0]
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <div style="background: rgba(210, 255, 0, 0.1); border: 2px solid #d2ff00; display: inline-block; padding: 10px 30px; border-radius: 50px;">
                        <span style="color: white;">🏆 Nº1 EN VENTAS: </span>
                        <span style="color: #d2ff00; font-weight: bold;">{str(top.name).upper()} ({int(top['Total Neto'])})</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Tabla Pro
            st.dataframe(
                rank.sort_values('Total Neto', ascending=False).style.format("{:.0f}")
                .background_gradient(subset=['Total Neto'], cmap='Greens')
                .set_properties(**{'text-align': 'center'}), 
                use_container_width=True
            )
        
        # Objetivo
        v_equipo = int(rank['Total Neto'].sum()) if not rank.empty else 0
        v_falta = max(0, 75 - v_equipo)
        st.markdown(f'<div style="background:#161b22;padding:15px;border-radius:15px;border:1px solid #d2ff00;text-align:center;max-width:300px;margin:auto;"><p style="color:#d2ff00;">🚀 FALTAN PARA EL OBJETIVO</p><h1>{v_falta}</h1></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error cargando los datos: {e}")

#-----REPOSITORIO----
elif menu == "📂 REPOSITORIO":
    import os  # Crucial para que funcionen las carpetas
    st.markdown('<div class="block-header">📂 REPOSITORIO DE DOCUMENTACIÓN</div>', unsafe_allow_html=True)

    # Función Maestra: Escanea la carpeta y genera botones para CADA archivo válido
    def mostrar_contenido_carpeta(nombre_carpeta, titulo_visible, icono="📁"):
        # Construimos la ruta buscando exactamente como se llaman tus carpetas
        ruta_especifica = os.path.join("manuales", nombre_carpeta)
        
        if os.path.exists(ruta_especifica):
            with st.expander(f"{icono} {titulo_visible}"):
                try:
                    # Listamos todos los archivos reales (.pdf, .jpg, .png, etc.)
                    archivos = [f for f in os.listdir(ruta_especifica) if os.path.isfile(os.path.join(ruta_especifica, f))]
                    
                    if archivos:
                        for filename in archivos:
                            ruta_archivo = os.path.join(ruta_especifica, filename)
                            with open(ruta_archivo, "rb") as f:
                                contenido = f.read()
                                ext = filename.split('.')[-1].lower()
                                
                                # Filtrar y asignar el MIME type adecuado para los formatos solicitados
                                if ext == "pdf":
                                    m_type = "application/pdf"
                                elif ext == "docx":
                                    m_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                elif ext in ["jpg", "jpeg", "png"]:
                                    m_type = f"image/{ext}"
                                else:
                                    m_type = "application/octet-stream"  # Tipo genérico por si hay algún otro archivo
                                
                                st.download_button(
                                    label=f"📄 Ver/Descargar: {filename}",
                                    data=contenido,
                                    file_name=filename,
                                    mime=m_type,
                                    key=f"btn_{nombre_carpeta}_{filename}".replace(" ", "_")
                                )
                    else:
                        st.write("ℹ️ Esta carpeta está vacía.")
                except Exception as e:
                    st.error(f"Error al leer la carpeta {nombre_carpeta}: {e}")
        else:
            # Si sale este mensaje es que el nombre de la carpeta no coincide con el disco duro
            st.caption(f"🚫 No detectada: manuales/{nombre_carpeta}")

    # --- DISTRIBUCIÓN SEGÚN TUS CARPETAS EN MAYÚSCULAS ---
    col_a, col_b = st.columns(2)

    with col_a:
        mostrar_contenido_carpeta("MARCADOR", "MANUAL DEL MARCADOR", "📂")
        mostrar_contenido_carpeta("ARGUMENTARIO", "ARGUMENTARIOS DE VENTAS", "📝")
        mostrar_contenido_carpeta("TARIFAS O2", "TARIFAS O2", "📱")
        mostrar_contenido_carpeta("TARIFAS LOWI", "TARIFAS LOWI", "📱")
        mostrar_contenido_carpeta("TARIFAS SEGURMA", "DOCUMENTACIÓN SEGURMA", "🛡️")

    with col_b:
        mostrar_contenido_carpeta("TARIFAS ENDESA", "TARIFAS ENDESA", "⚡")
        mostrar_contenido_carpeta("TARIFAS IBERDROLA", "TARIFAS IBERDROLA", "⚡")
        mostrar_contenido_carpeta("TARIFAS NATURGY", "TARIFAS NATURGY", "⚡")
        mostrar_contenido_carpeta("TARIFAS TOTAL", "TARIFAS TOTAL ENERGIES", "⚡")
        mostrar_contenido_carpeta("TARIFAS GANA", "TARIFAS GANA ENERGÍA", "⚡")
        # Nueva carpeta añadida manteniendo el formato y los iconos correspondientes
        mostrar_contenido_carpeta("TARIFAS 3D", "TARIFAS 3D", "⚡")

    st.markdown("---")
# --- CONTROL LABORAL ---
elif menu == "🕒 CONTROL LABORAL":
    import pandas as pd
    import calendar
    from datetime import datetime, time
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL Y ASISTENCIA</div>', unsafe_allow_html=True)
    
    try:
        # 1. CARGA Y LIMPIEZA
        sheet_id = "175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY"
        url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df_laboral = pd.read_csv(url_csv)
        df_laboral.columns = [str(c).strip().upper() for c in df_laboral.columns]
        
        col_comercial = "COMERCIAL"
        col_temporal = next((c for c in df_laboral.columns if "TEMPORAL" in c), None)
        col_accion = next((c for c in df_laboral.columns if "HACER" in c), None)
        df_laboral[col_temporal] = pd.to_datetime(df_laboral[col_temporal], dayfirst=True, errors='coerce')
        df_laboral = df_laboral.dropna(subset=[col_temporal])
        
        # 2. CONFIGURACIÓN DE DÍAS ESPECIALES
        festivos = ['2026-04-02', '2026-04-03', '2026-04-22', '2026-05-01']
        vacaciones_raquel = [d.strftime('%Y-%m-%d') for d in pd.date_range('2026-06-22', '2026-06-28')]
        libre_lorena_obj = ['2026-04-17']

        # --- CALENDARIO ANUAL ---
        with st.expander("📅 PLANIFICACIÓN ANUAL"):
            col_cal1, col_cal2 = st.columns(2)
            for i, m in enumerate([4, 6]):
                with [col_cal1, col_cal2][i]:
                    st.write(f"**{calendar.month_name[m]} 2026**")
                    cal = calendar.monthcalendar(2026, m)
                    for week in cal:
                        cols = st.columns(7)
                        for idx, day in enumerate(week):
                            if day != 0:
                                f_str = f"2026-{m:02d}-{day:02d}"
                                bg, txt_c, etiq = "transparent", "white", ""
                                if f_str in festivos: bg, etiq = "#ff4b4b", "FESTIVO"
                                elif f_str in vacaciones_raquel: bg, txt_c, etiq = "#d2ff00", "black", "VACAS RAQUEL"
                                elif f_str in libre_lorena_obj: bg, txt_c, etiq = "#00f0ff", "black", "OBJ. LORENA"
                                
                                label_h = f'<div style="font-size:0.5rem; font-weight:bold;">{etiq}</div>' if etiq else ""
                                cols[idx].markdown(f'<div style="background:{bg}; color:{txt_c}; text-align:center; border-radius:5px; padding:2px; min-height:45px; border:1px solid #30363d;"><div style="font-size:0.9rem;">{day}</div>{label_h}</div>', unsafe_allow_html=True)

        st.markdown("---")
        com_sel = st.selectbox("👤 Selecciona Comercial", sorted(df_laboral[col_comercial].unique()))

        # 3. LÓGICA DE CÁLCULO
        def calcular_auditoria_v12(df, nombre):
            datos = df[df[col_comercial] == nombre].copy()
            min_ret, dias_deuda, dias_rojos, min_medicos, min_objetivos, lista_justificantes = 0, [], [], 0, 0, []
            hoy = datetime.now().date()
            inicio = datos[col_temporal].min().date()
            
            fin_p = hoy
            if "MACARENA BACA" in nombre.upper(): fin_p = pd.Timestamp('2026-03-19').date()
            elif "LUIS RODRIGUEZ" in nombre.upper(): fin_p = pd.Timestamp('2026-04-24').date()

            for dia in pd.date_range(inicio, fin_p):
                d_str = dia.strftime('%Y-%m-%d')
                if dia.weekday() >= 5 or d_str in festivos: continue 
                if "RAQUEL" in nombre.upper() and d_str in vacaciones_raquel: continue
                
                # Gestión de días libres por objetivo
                if "LORENA" in nombre.upper() and d_str in libre_lorena_obj:
                    min_objetivos += 300 # El día libre cuenta como recuperado
                    continue

                es_esp = (dia >= pd.Timestamp('2026-03-29') and dia <= pd.Timestamp('2026-04-05')) or \
                         (dia >= pd.Timestamp('2026-04-19') and dia <= pd.Timestamp('2026-04-26'))
                
                h_lim_e = time(9, 0) if ("RAQUEL GUADALUPE" in nombre.upper() or es_esp) else time(9, 30)
                dia_data = datos[datos[col_temporal].dt.date == dia.date()]
                
                if dia_data.empty:
                    dias_deuda.append(dia.strftime('%d/%m/%Y'))
                else:
                    entradas = dia_data[dia_data[col_accion].astype(str).str.contains("ENTRADA", case=False, na=False)]
                    if entradas.empty:
                        dias_deuda.append(dia.strftime('%d/%m/%Y'))
                    else:
                        h_real = entradas[col_temporal].min().time()
                        if h_real > h_lim_e:
                            min_ret += (datetime.combine(dia, h_real) - datetime.combine(dia, h_lim_e)).total_seconds() / 60
                            dias_rojos.append(dia.date())

            # CASO LORENA: Horas Médicas y Objetivos
            if "LORENA" in nombre.upper():
                min_medicos = 180 
                lista_justificantes.append({"fecha": "27/04/2026", "motivo": "Cita Médica", "tramo": "11:30 a 14:30", "horas": "3h"})

            return int(min_ret), dias_deuda, dias_rojos, min_medicos, min_objetivos, lista_justificantes

        m_ret, l_deuda, d_rojos, m_med, m_obj, justificantes = calcular_auditoria_v12(df_laboral, com_sel)
        
        # 4. TOTALES
        bruto = m_ret + (len(l_deuda) * 300)
        # Belen y Deborah recuperan normal, Lorena suma sus objetivos
        recup_base = bruto if any(x in com_sel.upper() for x in ["BELEN", "DEBORAH"]) else 0
        if "LORENA" in com_sel.upper():
            recup_base = bruto # Lorena también tiene su histórico recuperado
        
        pend = max(0, bruto - recup_base)
        hf, mf = divmod(pend, 60)
        h_med, m_med_r = divmod(m_med, 60)
        h_obj, m_obj_r = divmod(m_obj, 60)

        # 5. DASHBOARD (6 Columnas)
        st.markdown(f"### 📊 Resumen Auditoría: {com_sel}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        def card_v(l, v, s, c):
            return f'<div style="background:#1c2128; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; min-height:110px;"><p style="color:#8b949e; font-size:0.75rem; margin:0;">{l}</p><h2 style="color:{c}; margin:10px 0; font-size:1.4rem;">{v}</h2><p style="color:#58a6ff; font-size:0.65rem; margin:0;">{s}</p></div>'

        c1.markdown(card_v("RETRASOS", f"{m_ret} m", f"{len(d_rojos)} registros", "#ffab70"), unsafe_allow_html=True)
        c2.markdown(card_v("DEUDA DÍAS", f"{len(l_deuda)*300} m", f"{len(l_deuda)} días", "#ff7b72"), unsafe_allow_html=True)
        c3.markdown(card_v("RECUPERADO", f"{recup_base} m", "Total abonado", "#7ee787"), unsafe_allow_html=True)
        c4.markdown(card_v("HORAS MÉDICAS", f"{int(h_med)}h {int(m_med_r)}m", "Justificadas", "#a371f7"), unsafe_allow_html=True)
        c5.markdown(card_v("LIBRE OBJETIVO", f"{int(h_obj)}h {int(m_obj_r)}m", "Premio Ventas", "#00f0ff"), unsafe_allow_html=True)
        
        p_col = "#d2ff00" if pend <= 0 else "#ff4b4b"
        c6.markdown(f'<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid {p_col}; text-align:center; min-height:110px;"><p style="color:{p_col}; font-weight:bold; margin:0; font-size:0.8rem;">PENDIENTE</p><h2 style="color:{p_col}; margin:5px 0; font-size:1.5rem;">{int(hf)}h {int(mf)}m</h2><p style="color:#8b949e; font-size:0.65rem; margin:0;">{pend} min</p></div>', unsafe_allow_html=True)

        # SECCIÓN DE JUSTIFICANTES MÉDICOS Y OBJETIVOS
        if justificantes or "LORENA" in com_sel.upper():
            st.markdown("#### 📑 DETALLE DE AUSENCIAS JUSTIFICADAS")
            if "LORENA" in com_sel.upper():
                st.success("**17/04/2024:** LIBRE POR OBJETIVO CUMPLIDO (5h justificadas)")
            for j in justificantes:
                st.info(f"**Fecha:** {j['fecha']} | **Tramo:** {j['tramo']} | **Total:** {j['horas']} | **Motivo:** {j['motivo']}")

        if l_deuda: st.warning(f"📌 Días con deuda (300m/día): {', '.join(l_deuda)}")

        # 6. HISTORIAL
        st.markdown("---")
        with st.expander("🔍 VER HISTORIAL DE REGISTROS"):
            h_df = df_laboral[df_laboral[col_comercial] == com_sel][[col_temporal, col_accion]].sort_values(col_temporal, ascending=False)
            st.dataframe(h_df.style.apply(lambda r: ['background-color: #440000; color: white' if r[col_temporal].date() in d_rojos and "ENTRADA" in str(r[col_accion]).upper() else '' for _ in r], axis=1), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")