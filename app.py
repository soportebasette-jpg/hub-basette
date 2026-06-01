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
        # 1. FUNCIÓN DE CARGA DESDE GOOGLE SHEETS (ROBUSTA)
        def load_and_clean_ranking():
            urls = {
                "de": "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv",
                "dt": "https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/export?format=csv",
                "da": "https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/export?format=csv"
            }
            dfs = []
            for url in urls.values():
                try:
                    df = pd.read_csv(url)
                    df.columns = df.columns.str.strip() # Limpieza de espacios
                    # Mapeo inteligente para evitar KeyError
                    mapeo = {c: 'Mes' for c in df.columns if 'mes' in c.lower()}
                    mapeo.update({c: 'Comercial' for c in df.columns if 'comercial' in c.lower()})
                    df = df.rename(columns=mapeo)
                    dfs.append(df)
                except:
                    dfs.append(pd.DataFrame())
            return dfs[0], dfs[1], dfs[2]

        # 2. ACCIÓN VISUAL AL ABRIR
        st.balloons()

        # 3. FRASES MOTIVADORAS DIARIAS
        frases = {1: "¡Hoy es un gran día para romper récords!", 2: "Tu esfuerzo de hoy es el éxito de mañana.", 3: "La disciplina es el puente hacia tus metas."}
        st.markdown(f'<h1 style="text-align:center; color:#d2ff00;">{frases.get(datetime.now().day % 3 + 1, "¡A por el objetivo!")}</h1>', unsafe_allow_html=True)

        de, dt, da = load_and_clean_ranking()

        # 4. FILTROS
        c_filtros, c_video = st.columns([2, 1])
        with c_filtros:
            meses_disp = sorted(list(set(de.get('Mes', [])) | set(dt.get('Mes', [])) | set(da.get('Mes', []))))
            f_mes = st.multiselect("Mes:", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
            coms_disp = sorted(list(set(de.get('Comercial', [])) | set(dt.get('Comercial', [])) | set(da.get('Comercial', []))))
            f_coms = st.multiselect("Comerciales:", coms_disp, default=coms_disp)

        # 5. CÁLCULO DE RANKING (ROBUSTO)
        def agrupar(df):
            if df.empty or 'Mes' not in df.columns: return pd.DataFrame()
            f = df[(df['Mes'].isin(f_mes)) & (df['Comercial'].isin(f_coms))]
            return f.groupby('Comercial').sum(numeric_only=True)

        r1 = agrupar(de)
        r2 = agrupar(dt)
        r3 = agrupar(da)
        
        rank = pd.concat([r1, r2, r3], axis=1).fillna(0)
        rank['Total Neto'] = rank.sum(axis=1)

        # 6. ENMARCADO Nº1
        if not rank.empty:
            top = rank.sort_values('Total Neto', ascending=False).iloc[0]
            st.markdown(f"""
                <div style="border: 3px solid #d2ff00; padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0;">
                    <h3 style="color: #d2ff00; margin: 0;">🏆 Nº1 VENTAS NETAS</h3>
                    <h2 style="color: white; margin: 0;">{str(top.name).upper()} ({int(top['Total Neto'])})</h2>
                </div>
            """, unsafe_allow_html=True)

            st.dataframe(rank.style.background_gradient(subset=['Total Neto'], cmap='Greens'), use_container_width=True)
        else:
            st.info("Selecciona filtros para ver el ranking.")

        # 7. TOTALES CANCELACIONES
        st.markdown("### 📊 DESGLOSE DE CANCELACIONES")
        cx1, cx2 = st.columns(2)
        cx1.metric("Total Cancelaciones", int(rank.filter(like="Cancel").sum().sum()))
        cx2.metric("Total Bajas", int(rank.filter(like="Baja").sum().sum()))

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")
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
# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        # 1. LANZAR GLOBOS AL ABRIR
        st.balloons()

        # 2. CARGA DE DATOS DESDE GOOGLE SHEETS (ROBUSTA)
        def load_and_clean_ranking():
            urls = {
                "de": "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv",
                "dt": "https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/export?format=csv",
                "da": "https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/export?format=csv"
            }
            dfs = []
            for url in urls.values():
                try:
                    df = pd.read_csv(url)
                    df.columns = [c.strip() for c in df.columns] # Limpiar espacios
                    # Normalizar nombres básicos
                    mapeo = {c: 'Mes' for c in df.columns if 'mes' in c.lower()}
                    mapeo.update({c: 'Comercial' for c in df.columns if 'comercial' in c.lower()})
                    df = df.rename(columns=mapeo)
                    dfs.append(df)
                except:
                    dfs.append(pd.DataFrame())
            return dfs[0], dfs[1], dfs[2]

        de, dt, da = load_and_clean_ranking()

        # 3. FILTROS Y VIDEO
        c1, c2 = st.columns([2, 1])
        with c1:
            meses_disp = sorted(list(set(de.get('Mes', [])) | set(dt.get('Mes', [])) | set(da.get('Mes', []))))
            f_mes = st.multiselect("Mes:", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
            coms_disp = sorted(list(set(de.get('Comercial', [])) | set(dt.get('Comercial', [])) | set(da.get('Comercial', []))))
            f_coms = st.multiselect("Comerciales:", coms_disp, default=coms_disp)
        with c2:
            if os.path.exists("WhatsApp Video 2026-04-28 at 00.31.03.mp4"):
                st.video("WhatsApp Video 2026-04-28 at 00.31.03.mp4")

        # 4. CÁLCULO SEGURO DEL RANKING
        def get_group(df):
            if 'Mes' not in df.columns or 'Comercial' not in df.columns: return pd.DataFrame()
            f = df[(df['Mes'].isin(f_mes)) & (df['Comercial'].isin(f_coms))]
            return f.groupby('Comercial').sum(numeric_only=True)

        r1, r2, r3 = get_group(de), get_group(dt), get_group(da)
        rank = pd.concat([r1, r2, r3], axis=1).fillna(0)
        rank['Total Neto'] = rank.sum(axis=1)

        # 5. RESULTADO VISUAL
        if not rank.empty:
            top = rank.sort_values('Total Neto', ascending=False).iloc[0]
            st.markdown(f"""
                <div style="border: 3px solid #d2ff00; padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0;">
                    <h3 style="color: #d2ff00; margin: 0;">🏆 Nº1 VENTAS NETAS</h3>
                    <h2 style="color: white; margin: 0;">{str(top.name).upper()} ({int(top['Total Neto'])})</h2>
                </div>
            """, unsafe_allow_html=True)
            st.dataframe(rank.style.background_gradient(subset=['Total Neto'], cmap='Greens'), use_container_width=True)
        else:
            st.info("Selecciona filtros para ver el ranking.")

        # 6. CUADROS DE DESGLOSE (CANCELACIONES/BAJAS)
        st.markdown("### 📊 DESGLOSE DE CANCELACIONES Y BAJAS")
        cx1, cx2, cx3, cx4 = st.columns(4)
        box = "background:#161b22; border:1px solid #ff4b4b; padding:10px; border-radius:10px; text-align:center;"
        cx1.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">CANCEL. ENERGÍA</p><h3>{int(rank.filter(like="Cancel_E").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">CANCEL. FIBRA</p><h3>{int(rank.filter(like="Cancel_F").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">BAJAS ENERGÍA</p><h3>{int(rank.filter(like="Baja_E").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">BAJAS FIBRA</p><h3>{int(rank.filter(like="Baja_F").sum().sum())}</h3></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error procesando datos: {e}")