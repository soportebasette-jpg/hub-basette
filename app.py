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

# 3. BASE DE DATOS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "logo_endesa.png"}
]

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
QR_PLAN_AMIGO = "qr-plan amigo.png"

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
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.link_button(f"REGISTRO DE JORNADA", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)

    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.link_button(p["n"], p["u"], use_container_width=True)
    
    st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
    c_t1, c_t2 = st.columns(2)
    with c_t1: st.link_button("ENTRAR O2", "https://o2online.es/auth/login/", use_container_width=True)
    with c_t2: st.link_button("ENTRAR LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)

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
            {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📺 FIBRA, MÓVIL Y TV</div>', unsafe_allow_html=True)
        tv_cols = st.columns(3)
        planes_tv = [
            ("600 Mb + TV M+", "38€", "35 GB"),
            ("600 Mb + TV M+ + NETFLIX", "45€", "60 GB"),
            ("1 Gb + TV M+", "50€", "350 GB"),
            ("1 Gb + TV M+ + NETFLIX", "56€", "375 GB")
        ]
        for i, (vel, pre, gb) in enumerate(planes_tv):
            with tv_cols[i % 3]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel}</div><div class="price-val">{pre}</div><div class="price-sub">{gb}</div></div>', unsafe_allow_html=True)

# --- COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
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
        consumo = st.number_input("Consumo del periodo (kWh)", value=0.0)

    try:
        p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    except: p_calc = 0.11

    coste_p = (potencia * sel["P1"] * dias_factura) + (potencia * sel["P2"] * dias_factura)
    coste_e = consumo * p_calc
    coste_total_iva = (coste_p + coste_e) * 1.21
    ahorro = f_act - coste_total_iva

    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🎁 PLAN AMIGO</div>', unsafe_allow_html=True)
    st.code("https://forms.gle/mU6XzRvywDoBQ5Q47")
    if os.path.exists(QR_PLAN_AMIGO): st.image(QR_PLAN_AMIGO, width=250)

# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.header("Dashboard de Rendimiento")
    try:
        df_e, df_t = load_and_clean_ranking()
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año'])))
        meses = sorted(list(set(df_e['Mes']) | set(df_t['Mes'])))
        
        c_filt_1, c_filt_2 = st.columns(2)
        with c_filt_1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_filt_2: f_mes = st.selectbox("📆 Mes", meses, index=len(meses)-1)

        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'] == f_mes)]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'] == f_mes)]

        re = de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum()
        rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum()
        rank = pd.concat([re, rt], axis=1).fillna(0)
        rank['TOTAL'] = rank.sum(axis=1)
        rank = rank.sort_values('TOTAL', ascending=False)

        if not rank.empty:
            st.markdown(f"""<div class="winner-card">👑 EL NÚMERO 1: {rank.index[0].upper()} ({int(rank.iloc[0]['TOTAL'])} VENTAS) 👑</div>""", unsafe_allow_html=True)
            st.table(rank.style.format(precision=0))
    except Exception as e:
        st.error(f"Error cargando el Dashboard: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    
    # DOCUMENTACIÓN LOWI
    with st.expander("📁 DOCUMENTACIÓN LOWI"):
        archivo_lowi = "TARIFAS_LOWI_MARZO2026.pdf"
        if os.path.exists(archivo_lowi):
            with open(archivo_lowi, "rb") as f:
                st.download_button("📥 DESCARGAR TARIFAS LOWI MARZO 2026", f, file_name=archivo_lowi)
        else: st.warning("PDF de Lowi no encontrado en la raíz.")

    # CAPTURAS O2 PARA ENVIAR A CLIENTES (CORREGIDO)
    with st.expander("📁 CAPTURAS O2 PARA ENVIAR A CLIENTES"):
        st.write("Visualiza y descarga las tarifas actuales de O2 para enviar:")
        capturas = [
            {"f": "600Mb_35Gb y TV.png", "n": "Fibra 600Mb + 35GB + TV"},
            {"f": "600Mb_60Gb y TV.png", "n": "Fibra 600Mb + 60GB + TV"},
            {"f": "1Gb_30Gb y TV.png", "n": "Fibra 1Gb + 350GB + TV"},
            {"f": "1Gb_375Gb y TV.png", "n": "Fibra 1Gb + 375GB + TV"},
            {"f": "LINEAS MOVILES ADICIONALES.png", "n": "Líneas Móviles Adicionales"}
        ]
        
        cap_cols = st.columns(2)
        for i, cap in enumerate(capturas):
            with cap_cols[i % 2]:
                # Buscamos en la raíz del repositorio, que es donde se suben por defecto
                file_path = cap['f'] 
                if os.path.exists(file_path):
                    st.image(file_path, caption=cap['n'], use_column_width=True)
                    with open(file_path, "rb") as f_img:
                        st.download_button(f"📥 Descargar {cap['f']}", f_img, file_name=cap['f'], key=f"btn_{cap['f']}")
                else:
                    st.error(f"No encontrado: {cap['f']}")