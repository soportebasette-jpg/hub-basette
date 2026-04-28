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
    ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO", "🕒 CONTROL LABORAL"]
)

# --- CRM ---
if menu == "🚀 CRM":
    col_t_izq, col_t_der = st.columns([2, 1])
    with col_t_izq:
        st.header("Portales de Gestión")
    with col_t_der:
        st.markdown(f"""
            <div class="social-container">
                <a href="https://www.facebook.com/share/1CqrZ4hGYp/?mibextid=wwXIfr" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" width="35" class="social-icon">
                </a>
                <a href="https://x.com/tecomparotodoes?s=21" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" width="35" class="social-icon">
                </a>
                <a href="https://www.instagram.com/tecomparotodoes?igsh=MXRkcTV2anJ6NmJkcA%3D%3D&utm_source=qr" target="_blank">
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
    energia = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, {"n": "NIBA", "u": "https://clientes.niba.es/"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">{p["n"]}</h4></div>''', unsafe_allow_html=True)
            st.link_button(f"ENTRAR", p["u"], use_container_width=True)
    
    st.markdown("---")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="block-header">🛡️ 🚨 ALARMAS</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">SEGURMA</h4></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://crm.segurma.com/web#action=619&cids=1&menu_id=200&model=sale.order&view_type=list", use_container_width=True)
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">O2</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR O2", "https://o2online.es/auth/login/?next=%2Fventas%2F&type=retail", use_container_width=True)
        with c_t2:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">LOWI</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)# --- PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        df_precios = pd.DataFrame(tarifas_luz).drop(columns=['logo'])
        st.dataframe(df_precios, use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([
            {"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"},
            {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"},
            {"PRIORIDAD": 3, "COMPAÑÍA": "GANA ENERGÍA", "FIJO RL1": "3,93 €", "ENERGIA RL1": "VARIABLE (BENEF. 0,11€)", "FIJO RL2": "8,11 €", "ENERGIA RL2": "VARIABLE (BENEF. 0,006€)"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 SOLO FIBRA</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        solo_fibra = [("300 Mb", "23€"), ("600 Mb", "27€"), ("1 Gb", "31€")]
        for i, (vel, pre) in enumerate(solo_fibra):
            with f_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">FIBRA {vel}</div><div class="price-val">{pre}</div><div class="price-sub">Precio Final / Mes</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES</div>', unsafe_allow_html=True)
        ad_cols = st.columns(3)
        lineas_ad = [("300 Mb", "15€"), ("600 Mb", "20€"), ("1 Gb", "27€")]
        for i, (vel, pre) in enumerate(lineas_ad):
            with ad_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">ADICIONAL {vel}</div><div class="price-val">{pre}</div><div class="price-sub">Precio / Mes</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">🌐 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        fm_cols = st.columns(3)
        fibra_movil = [
            ("600 Mb", "35€", "1 LÍNEA MÓVIL (60GB)"),
            ("600 Mb", "35€", "2 LÍNEAS (10GB + 40GB)"),
            ("1 Gb", "38€", "1 LÍNEA MÓVIL (120GB)")
        ]
        for i, (vel, pre, lin) in enumerate(fibra_movil):
            with fm_cols[i % 3]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel} + {lin}</div><div class="price-val">{pre}</div><div class="price-sub">Conexión de Alta Velocidad</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">📺 FIBRA, MÓVIL Y TV</div>', unsafe_allow_html=True)
        tv_cols = st.columns(3)
        planes_tv = [
            ("SOLO TV", "9.99€", "Streaming", "O2 TV"),
            ("600 Mb + TV M+", "38€", "35 GB", "1 LÍNEA MÓVIL"),
            ("600 Mb + TV M+ + NETFLIX", "45€", "60 GB", "1 LÍNEA MÓVIL"),
            ("1 Gb + TV M+", "50€", "350 GB", "1 LÍNEA MÓVIL"),
            ("1 Gb + TV M+ + NETFLIX", "56€", "375 GB", "1 LÍNEA MÓVIL")
        ]
        for i, (vel, pre, gb, lin) in enumerate(planes_tv):
            with tv_cols[i % 3]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel}</div><div class="price-val">{pre}</div><div class="price-sub">{gb} | {lin}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES (TV)</div>', unsafe_allow_html=True)
        ad_tv_cols = st.columns(3)
        lineas_ad_tv = [("40 GB", "5€"), ("150 GB", "10€"), ("300 GB", "15€")]
        for i, (gb, pre) in enumerate(lineas_ad_tv):
            with ad_tv_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">ADICIONAL {gb}</div><div class="price-val">{pre}</div><div class="price-sub">Precio / Mes</div></div>', unsafe_allow_html=True)

# --- COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro Personalizado")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre del cliente", "Nombre Apellidos")
        f_act = st.number_input("Factura actual con IVA (EUR)", value=0.0)
        potencia = st.number_input("Potencia contratada (kW)", value=4.6)
        dias_factura = st.number_input("Días del periodo de factura", value=30)
    with c2:
        comp_sel = st.selectbox("Compañía Propuesta", sorted(list(set(t["COMPAÑÍA"] for t in tarifas_luz))))
        tarifas_f = [t["TARIFA"] for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel]
        tarifa_sel_nombre = st.selectbox("Tarifa Seleccionada", tarifas_f)
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tarifa_sel_nombre)
        if os.path.exists(sel["logo"]): st.image(sel["logo"], width=120)
        consumo = st.number_input("Consumo del periodo (kWh)", value=0.0)
    try:
        p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    except:
        p_calc = 0.11
    coste_p = (potencia * sel["P1"] * dias_factura) + (potencia * sel["P2"] * dias_factura)
    coste_e = consumo * p_calc
    coste_total_iva = (coste_p + coste_e) * 1.21
    ahorro = f_act - coste_total_iva
    st.info(f"**Tarifa Seleccionada:** {tarifa_sel_nombre} | Energía: **{sel['ENERGIA']}** €/kWh | Potencia: **{sel['P1']}** €/kW día")
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)
    if st.button("GENERAR ESTUDIO PDF PROFESIONAL"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists(LOGO_PRINCIPAL): pdf.image(LOGO_PRINCIPAL, 10, 8, 33)
        if os.path.exists(sel["logo"]): pdf.image(sel["logo"], 165, 8, 30)
        pdf.ln(30); pdf.set_font("Arial", "B", 18); pdf.cell(190, 10, "ESTUDIO COMPARATIVO DE AHORRO", ln=True, align="C")
        pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 8, f" DATOS DEL CLIENTE: {cliente.upper()}", ln=True, fill=True)
        pdf.set_font("Arial", "", 10); pdf.cell(95, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", border=1)
        pdf.cell(95, 8, f"Periodo: {dias_factura} dias", border=1, ln=True); pdf.ln(5)
        pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, " DETALLE DE LA PROPUESTA", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        for d, v in [("Compania", comp_sel), ("Tarifa", tarifa_sel_nombre), ("Potencia", f"{potencia} kW"), ("Energia", f"{sel['ENERGIA']} EUR/kWh")]:
            pdf.cell(95, 8, d, border=1); pdf.cell(95, 8, str(v), border=1, ln=True)
        pdf.ln(5); pdf.set_font("Arial", "B", 12); pdf.cell(95, 10, "Factura Actual", border=1); pdf.cell(95, 10, f"{f_act:.2f} EUR", border=1, ln=True)
        pdf.cell(95, 10, "Nueva Factura", border=1); pdf.cell(95, 10, f"{coste_total_iva:.2f} EUR", border=1, ln=True)
        pdf.ln(5); pdf.set_fill_color(210, 255, 0); pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 15, f"AHORRO TOTAL: {ahorro:.2f} EUR", ln=True, align="C", fill=True)
        pdf.ln(10); pdf.set_font("Arial", "B", 12); pdf.cell(190, 10, "PLAN AMIGO BASETTE", ln=True)
        if os.path.exists(QR_PLAN_AMIGO):
            pdf.image(QR_PLAN_AMIGO, 80, pdf.get_y(), 50)
        st.download_button(label="📥 DESCARGAR ESTUDIO PDF", data=pdf.output(dest='S').encode('latin-1', 'replace'), file_name=f"Estudio_{cliente}.pdf")

# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🎁 PLAN AMIGO</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Enlace Plan Amigo")
        st.code("https://forms.gle/mU6XzRvywDoBQ5Q47")
        st.link_button("Ir al Formulario", "https://forms.gle/mU6XzRvywDoBQ5Q47")
    with col2:
        st.subheader("QR Plan Amigo")
        if os.path.exists(QR_PLAN_AMIGO):
            st.image(QR_PLAN_AMIGO, width=250)
            with open(QR_PLAN_AMIGO, "rb") as file:
                st.download_button("Descargar QR", file, "qr-plan-amigo.png")
        else:
            st.error("Archivo QR no encontrado.")

    st.markdown('<div class="block-header">🖼️ MATERIAL PUBLICITARIO</div>', unsafe_allow_html=True)
    st.write("Visualiza y descarga los últimos anuncios:")
    
    path_anuncios = "anunciosbasette/"
    lista_anuncios = [
        {"file": "Anuncio1_qr.png", "name": "Anuncio 1 QR"},
        {"file": "Anuncio2_qr.png", "name": "Anuncio 2 QR"},
        {"file": "PUBLI3.jpg", "name": "Publicidad 3"},
        {"file": "anuncio alarma1.png", "name": "Anuncio Alarma 1"},
        {"file": "anuncio1.png", "name": "Anuncio 1"},
        {"file": "anuncio2.png", "name": "Anuncio 2"}
    ]
    
    cols_anuncios = st.columns(3)
    for idx, item in enumerate(lista_anuncios):
        with cols_anuncios[idx % 3]:
            full_path = f"{path_anuncios}{item['file']}"
            if os.path.exists(full_path):
                st.image(full_path, use_container_width=True)
                with open(full_path, "rb") as f_anuncio:
                    data_anuncio = f_anuncio.read()
                    st.download_button(
                        label=f"Descargar {item['name']}",
                        data=data_anuncio,
                        file_name=item['file'],
                        mime="image/png" if item['file'].lower().endswith('.png') else "image/jpeg",
                        key=f"btn_anuncio_{idx}"
                    )
            else:
                st.error(f"Falta: {item['file']}")

# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        de, dt, da = load_and_clean_ranking()
        
        # --- FILTROS ---
        all_anos = sorted(list(set(de['Año']) | set(dt['Año']) | set(da['Año'])))
        all_meses = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
        all_coms = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: f_ano = st.selectbox("📅 Año", all_anos, index=len(all_anos)-1 if all_anos else 0)
        with c2: f_meses = st.multiselect("📆 Meses", all_meses, default=[all_meses[-1]] if all_meses else [])
        with c3: f_coms = st.multiselect("👤 Filtrar Comerciales", all_coms, default=all_coms)

        f_de = de[(de['Año']==f_ano) & (de['Mes'].isin(f_meses)) & (de['Comercial'].isin(f_coms))].copy()
        f_dt = dt[(dt['Año']==f_ano) & (dt['Mes'].isin(f_meses)) & (dt['Comercial'].isin(f_coms))].copy()
        f_da = da[(da['Año']==f_ano) & (da['Mes'].isin(f_meses)) & (da['Comercial'].isin(f_coms))].copy()

        # --- LÓGICA DE CÁLCULO, OBJETIVOS Y REFERIDOS ---
        for df_temp in [f_de, f_dt, f_da]:
            if not df_temp.empty:
                if 'Canal' in df_temp.columns:
                    df_temp['V_REF'] = df_temp['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0)
                else:
                    df_temp['V_REF'] = 0
                
                if 'V_Movil' in df_temp.columns: df_temp.rename(columns={'V_Movil': 'V_Móvil'}, inplace=True)
                if 'Estado' in df_temp.columns:
                    df_temp['V_Baja'] = df_temp['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0)
                    df_temp['V_Cancelado'] = df_temp['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0)
                else:
                    df_temp['V_Baja'], df_temp['V_Cancelado'] = 0, 0

        r1 = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'V_Baja', 'V_Cancelado', 'V_REF']].sum() if not f_de.empty else pd.DataFrame()
        r2 = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'V_Baja', 'V_Cancelado', 'V_REF']].sum() if not f_dt.empty else pd.DataFrame()
        r3 = f_da.groupby('Comercial')[['V_Alarma', 'V_Baja', 'V_Cancelado', 'V_REF']].sum() if not f_da.empty else pd.DataFrame()
        
        rank_calc = pd.concat([r1, r2, r3], axis=1).fillna(0)
        
        # Cálculo TOTAL (Sin móviles) y Faltantes
        rank_calc['TOTAL_NETO'] = (rank_calc.get('V_Luz',0) + rank_calc.get('V_Gas',0) + rank_calc.get('V_Fibra',0) + rank_calc.get('V_Alarma',0)) - rank_calc.filter(like='V_Baja').sum(axis=1) - rank_calc.filter(like='V_Cancelado').sum(axis=1)
        rank_calc['FALTAN_PARA_25'] = rank_calc['TOTAL_NETO'].apply(lambda x: max(0, 25 - int(x)))
        rank_calc['REF_TOTAL'] = rank_calc.filter(like='V_REF').sum(axis=1)

        # MOSTRAR IMAGEN ROSCO
        col_img1, col_img2, col_img3 = st.columns([1, 0.8, 1])
        with col_img2:
            if os.path.exists("rosco.jpg"):
                st.image("rosco.jpg", use_container_width=True)

        # IDENTIFICAR AL GANADOR
        if not rank_calc.empty and rank_calc['TOTAL_NETO'].max() > 0:
            ganador_nombre = rank_calc['TOTAL_NETO'].idxmax()
            ganador_ventas = int(rank_calc['TOTAL_NETO'].max())
        else:
            ganador_nombre = "ESPERANDO VENTAS..."
            ganador_ventas = 0

        # --- DISEÑO: FRASE GIGANTE Y NÚMERO 1 ---
        frases_dia = ["EL ÉXITO ES LA SUMA DE PEQUEÑOS ESFUERZOS REPETIDOS DÍA TRAS DÍA.", "TU ÚNICA LIMITACIÓN ES TU MENTE. ¡A POR TODAS!", "TRABAJA EN SILENCIO, QUE EL ÉXITO SE ENCARGUE DE HACER EL RUIDO.", "NO CUENTES LOS DÍAS, HAZ QUE LOS DÍAS CUENTEN.", "LA DISCIPLINA ES EL PUENTE ENTRE LAS METAS Y LOS LOGROS.", "LA EXCELENCIA NO ES UN ACTO, SINO UN HÁBITO."]
        frase_hoy = frases_dia[datetime.now().day % len(frases_dia)]

        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1c2128 0%, #0d1117 100%); padding: 30px; border-radius: 20px; border: 2px solid #d2ff00; text-align: center; margin-bottom: 30px;">
                <h1 style="color: #d2ff00; font-size: 50px; font-weight: 900; line-height: 1.1; margin-bottom: 20px;">"{frase_hoy}"</h1>
                <div style="background: rgba(210, 255, 0, 0.1); padding: 25px; border-radius: 15px; border: 1px dashed #d2ff00; display: inline-block; min-width: 400px;">
                    <p style="color: #8b949e; letter-spacing: 5px; font-size: 1.2rem; margin-bottom: 10px;">TOP VENTAS ACTUAL 🏆</p>
                    <h2 style="color: white; font-size: 3.5rem; margin: 0;">{ganador_nombre}</h2>
                    <h3 style="color: #d2ff00; font-size: 3rem; margin: 0;">{ganador_ventas} VENTAS</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- TABS ---
        t_rank, t_ene, t_tel, t_ala = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with t_rank:
            st.markdown('<div class="block-header">RANKING DE PRODUCTIVIDAD (META 25)</div>', unsafe_allow_html=True)
            
            # Limpiar tabla para mostrar (sin decimales)
            rank_display = rank_calc.copy()
            rank_display = rank_display.rename(columns={
                'V_Luz': 'Luz', 'V_Gas': 'Gas', 'V_Fibra': 'Fibra', 
                'V_Móvil': 'Móvil', 'V_Alarma': 'Alarma', 'REF_TOTAL': 'Referidos',
                'TOTAL_NETO': 'Total Neto', 'FALTAN_PARA_25': 'Faltan para Objetivo'
            })
            
            # Consolidar Bajas/Cancelados
            for st_col in ['Baja', 'Cancelado']:
                v_tag = f'V_{st_col}'
                rank_display[st_col] = rank_display.filter(like=v_tag).sum(axis=1) if not rank_display.filter(like=v_tag).empty else 0

            cols_f = ['Luz', 'Gas', 'Fibra', 'Móvil', 'Alarma', 'Referidos', 'Baja', 'Cancelado', 'Total Neto', 'Faltan para Objetivo']
            # Convertir todo a entero para quitar decimales
            st.table(rank_display[[c for c in cols_f if c in rank_display.columns]].astype(int).sort_values('Total Neto', ascending=False))

            st.markdown("---")
            # --- CUADROS DE ABAJO CON MEJOR COLOR ---
            m1, m2, m3, m4 = st.columns(4)
            estilo_caja = "background-color: #1c2128; border: 2px solid #d2ff00; padding: 20px; border-radius: 15px; text-align: center;"
            
            m1.markdown(f'<div style="{estilo_caja}"><p style="color: #8b949e; margin:0; font-size: 1rem;">Ventas Energía</p><h2 style="color: #ffffff; margin:0; font-size: 2.2rem;">{int(rank_display["Luz"].sum() + rank_display["Gas"].sum())}</h2></div>', unsafe_allow_html=True)
            m2.markdown(f'<div style="{estilo_caja}"><p style="color: #8b949e; margin:0; font-size: 1rem;">Ventas Fibra</p><h2 style="color: #ffffff; margin:0; font-size: 2.2rem;">{int(rank_display["Fibra"].sum())}</h2></div>', unsafe_allow_html=True)
            m3.markdown(f'<div style="{estilo_caja}"><p style="color: #8b949e; margin:0; font-size: 1rem;">Total Referidos</p><h2 style="color: #ffffff; margin:0; font-size: 2.2rem;">{int(rank_display["Referidos"].sum())}</h2></div>', unsafe_allow_html=True)
            m4.markdown(f'<div style="{estilo_caja}"><p style="color: #d2ff00; margin:0; font-size: 1rem; font-weight: bold;">Netas Equipo</p><h2 style="color: #ffffff; margin:0; font-size: 2.2rem;">{int(rank_display["Total Neto"].sum())}</h2></div>', unsafe_allow_html=True)

        with t_ene:
            if not f_de.empty:
                col_e1, col_e2 = st.columns(2)
                with col_e1: st.plotly_chart(px.pie(f_de, names='Comercial', values='V_Luz', title="Distribución Luz"), use_container_width=True)
                with col_e2: st.plotly_chart(px.bar(f_de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum().reset_index(), x='Comercial', y=['V_Luz', 'V_Gas'], title="Ventas Energía"), use_container_width=True)
        with t_tel:
            if not f_dt.empty:
                col_t1, col_t2 = st.columns(2)
                with col_t1: st.plotly_chart(px.pie(f_dt, names='Comercial', values='V_Fibra', title="Distribución Fibra"), use_container_width=True)
                with col_t2: st.plotly_chart(px.bar(f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum().reset_index(), x='Comercial', y=['V_Fibra', 'V_Móvil'], title="Ventas Telco"), use_container_width=True)
        with t_ala:
            if not f_da.empty:
                col_a1, col_a2 = st.columns(2)
                with col_a1: st.plotly_chart(px.pie(f_da, names='Comercial', values='V_Alarma', title="Distribución Alarmas"), use_container_width=True)
                with col_a2: st.plotly_chart(px.bar(f_da.groupby('Comercial')['V_Alarma'].sum().reset_index(), x='V_Alarma', y='Comercial', orientation='h', title="Ranking Alarmas"), use_container_width=True)

    except Exception as e:
        st.error(f"Error cargando el Dashboard: {e}")#-----REPOSITORIO----
elif menu == "📂 REPOSITORIO":
    import os  # Crucial para que funcionen las carpetas
    st.markdown('<div class="block-header">📂 REPOSITORIO DE DOCUMENTACIÓN</div>', unsafe_allow_html=True)

    # Función Maestra: Escanea la carpeta y genera botones para CADA archivo
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
                                # MIME type para que el navegador sepa qué es
                                m_type = "application/pdf" if ext == "pdf" else f"image/{ext}"
                                
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
        def calcular_auditoria_v11(df, nombre):
            datos = df[df[col_comercial] == nombre].copy()
            min_ret, dias_deuda, dias_rojos, min_medicos, lista_justificantes = 0, [], [], 0, []
            hoy = datetime.now().date()
            inicio = datos[col_temporal].min().date()
            
            fin_p = hoy
            if "MACARENA BACA" in nombre.upper(): fin_p = pd.Timestamp('2026-03-19').date()
            elif "LUIS RODRIGUEZ" in nombre.upper(): fin_p = pd.Timestamp('2026-04-24').date()

            for dia in pd.date_range(inicio, fin_p):
                d_str = dia.strftime('%Y-%m-%d')
                if dia.weekday() >= 5 or d_str in festivos: continue 
                if "RAQUEL" in nombre.upper() and d_str in vacaciones_raquel: continue
                if "LORENA" in nombre.upper() and d_str in libre_lorena_obj:
                    dias_deuda.append(f"{dia.strftime('%d/%m/%Y')} (Libre Obj)")
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

            # CASO LORENA: Horas Médicas hoy 27/04
            if "LORENA" in nombre.upper() and hoy == pd.Timestamp('2026-04-27').date():
                min_medicos = 180 
                lista_justificantes.append({"fecha": "27/04/2026", "motivo": "Cita Médica", "tramo": "11:30 a 14:30", "horas": "3h"})

            return int(min_ret), dias_deuda, dias_rojos, min_medicos, lista_justificantes

        m_ret, l_deuda, d_rojos, m_med, justificantes = calcular_auditoria_v11(df_laboral, com_sel)
        
        # 4. TOTALES
        bruto = m_ret + (len(l_deuda) * 300)
        # Belen recupera todo para estar a 0
        recup = bruto if "BELEN" in com_sel.upper() else (bruto if any(x in com_sel.upper() for x in ["LORENA", "DEBORAH"]) else 0)
        
        pend = max(0, bruto - recup)
        hf, mf = divmod(pend, 60)
        h_med, m_med_r = divmod(m_med, 60)

        # 5. DASHBOARD
        st.markdown(f"### 📊 Resumen Auditoría: {com_sel}")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        def card_v(l, v, s, c):
            return f'<div style="background:#1c2128; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; min-height:110px;"><p style="color:#8b949e; font-size:0.75rem; margin:0;">{l}</p><h2 style="color:{c}; margin:10px 0; font-size:1.4rem;">{v}</h2><p style="color:#58a6ff; font-size:0.65rem; margin:0;">{s}</p></div>'

        c1.markdown(card_v("RETRASOS", f"{m_ret} m", f"{len(d_rojos)} registros", "#ffab70"), unsafe_allow_html=True)
        c2.markdown(card_v("DEUDA DÍAS", f"{len(l_deuda)*300} m", f"{len(l_deuda)} días", "#ff7b72"), unsafe_allow_html=True)
        c3.markdown(card_v("RECUPERADO", f"{recup} m", "Total abonado", "#7ee787"), unsafe_allow_html=True)
        c4.markdown(card_v("HORAS MÉDICAS", f"{int(h_med)}h {int(m_med_r)}m", "Justificadas", "#a371f7"), unsafe_allow_html=True)
        
        p_col = "#d2ff00" if pend <= 0 else "#ff4b4b"
        c5.markdown(f'<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid {p_col}; text-align:center; min-height:110px;"><p style="color:{p_col}; font-weight:bold; margin:0; font-size:0.8rem;">PENDIENTE</p><h2 style="color:{p_col}; margin:5px 0; font-size:1.5rem;">{int(hf)}h {int(mf)}m</h2><p style="color:#8b949e; font-size:0.65rem; margin:0;">{pend} min</p></div>', unsafe_allow_html=True)

        # SECCIÓN DE JUSTIFICANTES MÉDICOS
        if justificantes:
            st.markdown("#### 🩺 DETALLE DE HORAS MÉDICAS JUSTIFICADAS")
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