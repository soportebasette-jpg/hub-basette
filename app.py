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

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    # Energía
    df_e = pd.read_csv(URL_ENE)
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    
    # Telefonía
    df_t = pd.read_csv(URL_TEL)
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    
    # Procesamiento robusto de métricas Telco
    def get_telco_metrics(row):
        f, m = 0, 0
        t = str(row.get('Tipo Tarifa', '')).lower()
        if 'fibramovil' in t or ('fibra' in t and 'movil' in t): f, m = 1, 1
        elif 'fibra' in t: f = 1
        elif 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return f, m, (f + m)

    # Creamos las columnas directamente para evitar errores de índice o duplicados
    res = df_t.apply(get_telco_metrics, axis=1)
    df_t['V_Fibra'] = res.apply(lambda x: x[0])
    df_t['V_Móvil'] = res.apply(lambda x: x[1])
    df_t['Total_Tel'] = res.apply(lambda x: x[2])
    
    return df_e, df_t

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
    st.header("Portales de Gestión")
    
    # CONTROL LABORAL
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
        st.link_button("ENTRAR", "https://partners.segurma.com/", use_container_width=True)
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        # Bloque Telecomunicaciones con O2 y Lowi
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">O2</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR O2", "https://o2online.es/auth/login/", use_container_width=True)
        with c_t2:
            st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">LOWI</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)

# --- PRECIOS ---
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
        {"file": "PUBLI3.jpg", "name": "Publicidad 3"}
    ]
    
    col_img1, col_img2, col_img3 = st.columns(3)
    columnas_anuncios = [col_img1, col_img2, col_img3]

    for idx, item in enumerate(lista_anuncios):
        with columnas_anuncios[idx]:
            full_path = f"{path_anuncios}{item['file']}"
            if os.path.exists(full_path):
                st.image(full_path, use_column_width=True)
                with open(full_path, "rb") as file:
                    st.download_button(
                        label=f"Descargar {item['name']}",
                        data=file,
                        file_name=item['file'],
                        mime="image/png" if "png" in item['file'] else "image/jpeg",
                        key=f"dl_{idx}"
                    )
            else:
                st.error(f"No se encontró: {item['file']}")

# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.header("📊 Dashboard de Rendimiento y Ranking")
    try:
        df_e, df_t = load_and_clean_ranking()
        
        c_filt_1, c_filt_2, c_filt_3 = st.columns(3)
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año'])))
        meses = sorted(list(set(df_e['Mes']) | set(df_t['Mes'])))
        comerciales_lista = sorted(list(set(df_e['Comercial']) | set(df_t['Comercial'])))
        
        with c_filt_1:
            f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_filt_2:
            f_mes = st.selectbox("📆 Mes", meses, index=len(meses)-1)
        with c_filt_3:
            f_com = st.multiselect("👤 Comerciales", options=comerciales_lista, default=comerciales_lista)

        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'] == f_mes) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'] == f_mes) & (df_t['Comercial'].isin(f_com))]

        tab_r, tab_e, tab_t = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO"])

        with tab_r:
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum()
            
            # Combinación de datos para el ranking
            rank = pd.concat([re, rt], axis=1).fillna(0)
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Móvil']
            rank = rank.sort_values('TOTAL', ascending=False)

            if not rank.empty:
                ganador = rank.index[0]
                total_ganador = int(rank.iloc[0]['TOTAL'])
                st.markdown(f"""<div class="winner-card">👑 EL NÚMERO 1: {ganador.upper()} ({total_ganador} VENTAS) 👑</div>""", unsafe_allow_html=True)
                
                def asignar_medalla(n):
                    if n == 0: return "🥇 Oro"
                    elif n == 1: return "🥈 Plata"
                    elif n == 2: return "🥉 Bronce"
                    else: return "⭐"
                
                rank_visual = rank.reset_index()
                rank_visual.insert(0, 'Puesto', [asignar_medalla(i) for i in range(len(rank_visual))])
                st.table(rank_visual.style.format(precision=0))
            else:
                st.warning("No hay datos para esta selección.")

        with tab_e:
            col_e1, col_e2 = st.columns([1, 1.2])
            with col_e1:
                if not de.empty:
                    fig_e = px.pie(de, values='Total_Ene', names='Comercializadora', hole=0.5, title="Cuota de Energía")
                    fig_e.update_traces(textposition='outside', textinfo='label+percent')
                    st.plotly_chart(fig_e, use_container_width=True)
                else: st.info("Sin datos de energía.")
            with col_e2:
                if not de.empty:
                    fig_eb = px.bar(de.groupby('Comercial')['Total_Ene'].sum().reset_index().sort_values('Total_Ene'), x='Total_Ene', y='Comercial', orientation='h', text_auto=True, title="Ventas Energía")
                    st.plotly_chart(fig_eb, use_container_width=True)

        with tab_t:
            col_t1, col_t2 = st.columns([1, 1.2])
            with col_t1:
                if not dt.empty:
                    fig_t = px.pie(dt, values='Total_Tel', names='Operadora', hole=0.5, title="Cuota de Telco")
                    fig_t.update_traces(textposition='outside', textinfo='label+percent')
                    st.plotly_chart(fig_t, use_container_width=True)
                else: st.info("Sin datos de telefonía.")
            with col_t2:
                if not dt.empty:
                    fig_tb = px.bar(dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum().reset_index(), x='Comercial', y=['V_Fibra', 'V_Móvil'], barmode='group', title="Mix de Telco")
                    st.plotly_chart(fig_tb, use_container_width=True)

    except Exception as e:
        st.error(f"Error cargando el Dashboard: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    
    # 📁 NUEVA SECCIÓN: CAPTURAS O2
    with st.expander("📁 CAPTURAS O2 PARA ENVIAR A CLIENTES", expanded=True):
        st.write("Visualiza y descarga las tarifas actuales de O2 para enviar:")
        capturas_o2 = [
            {"f": "600Mb_35Gb y TV.png", "n": "Fibra 600Mb + 35GB + TV"},
            {"f": "600Mb_60Gb y TV.png", "n": "Fibra 600Mb + 60GB + TV"},
            {"f": "1Gb_30Gb y TV.png", "n": "Fibra 1Gb + 350GB + TV"},
            {"f": "1Gb_375Gb y TV.png", "n": "Fibra 1Gb + 375GB + TV"},
            {"f": "LINEAS MOVILES ADICIONALES.png", "n": "Líneas Móviles Adicionales"}
        ]
        
        cap_cols = st.columns(2)
        for i, cap in enumerate(capturas_o2):
            with cap_cols[i % 2]:
                file_name = cap['f']
                if os.path.exists(file_name):
                    st.image(file_name, caption=cap['n'], use_column_width=True)
                    with open(file_name, "rb") as f_img:
                        st.download_button(f"📥 Descargar {cap['n']}", f_img, file_name=file_name, key=f"o2_{i}")
                else:
                    st.error(f"Imagen no encontrada: {file_name}")

    st.markdown("---")

    with st.expander("📂 MANUAL DEL MARCADOR"):
        manual_path = "manuales/Manual_Premiumnumber_Agente.pdf"
        if os.path.exists(manual_path):
            with open(manual_path, "rb") as f:
                st.download_button("📖 DESCARGAR MANUAL", f, file_name="Manual_Marcador.pdf")
    
    st.markdown("---")
    
    # DOCUMENTACIÓN LOWI
    with st.expander("📁 DOCUMENTACIÓN LOWI"):
        archivo_lowi = "manuales/TARIFAS_LOWI_MARZO2026.pdf"
        if os.path.exists(archivo_lowi):
            with open(archivo_lowi, "rb") as f:
                st.download_button("📥 DESCARGAR TARIFAS LOWI MARZO 2026", f, file_name="TARIFAS_LOWI_MARZO2026.pdf")
        else:
            st.warning("Archivo TARIFAS_LOWI_MARZO2026.pdf no encontrado en la carpeta manuales.")

    for c in ["GANA ENERGÍA", "NATURGY", "TOTAL", "ENDESA", "O2"]:
        with st.expander(f"📁 DOCUMENTACIÓN {c}"):
            if os.path.exists("manuales"):
                busq = "total" if c == "TOTAL" else c.split()[0].lower()
                archivos = [f for f in os.listdir("manuales") if busq in f.lower() and not f.lower().endswith('.png')]
                for fn in archivos:
                    with open(f"manuales/{fn}", "rb") as f:
                        st.download_button(f"📥 {fn}", f, file_name=fn, key=f"b_{fn}")