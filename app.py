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
                <a href="https://www.youtube.com/@tecomparotodo" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="35" class="social-icon">
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
    energia = [
        {"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, 
        {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, 
        {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, 
        {"n": "TOTAL ENERGY", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, 
        {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, 
        {"n": "NIBA", "u": "https://clientes.niba.es/"}, 
        {"n": "ENDESA", "u": "https://inergia.app"},
        {"n": "REPSOL", "u": "https://inergia.app/login.php"}
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
    
    t1, t2, t3 = st.tabs(["⚡ LUZ Y GAS", "📶 TELECOMUNICACIONES", "🛡️ ALARMAS"])
    
    with t1:
        st.markdown('<div class="block-header">⚡ LUZ Y GAS</div>', unsafe_allow_html=True)
        if os.path.exists("tarifas_visuales/luz_gas.jpg"):
            st.image("tarifas_visuales/luz_gas.jpg", use_container_width=True)
        else:
            st.warning("Imagen 'tarifas_visuales/luz_gas.jpg' no encontrada.")

    with t2:
        st.markdown('<div class="block-header">📶 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        
        st.subheader("LOWI")
        if os.path.exists("tarifas_visuales/lowi.jpg"):
            st.image("tarifas_visuales/lowi.jpg", use_container_width=True)
        
        st.divider()
        
        st.subheader("O2")
        # --- BÚSQUEDA INTELIGENTE DE IMAGEN ---
        carpeta = "tarifas_visuales"
        archivos_en_carpeta = os.listdir(carpeta) if os.path.exists(carpeta) else []
        
        # Buscamos cualquier archivo que contenga "PRECIOS JUNIO O2" sin importar mayúsculas
        archivo_o2 = next((f for f in archivos_en_carpeta if "PRECIOS JUNIO O2" in f.upper()), None)
        
        if archivo_o2:
            st.image(f"{carpeta}/{archivo_o2}", use_container_width=True)
        else:
            st.error(f"No se encontró ninguna imagen para O2 en '{carpeta}'. Archivos hallados: {archivos_en_carpeta}")

    with t3:
        st.markdown('<div class="block-header">🛡️ ALARMAS</div>', unsafe_allow_html=True)
        
        st.subheader("SEGURMA")
        if os.path.exists("tarifas_visuales/segurma.jpg"):
            st.image("tarifas_visuales/segurma.jpg", use_container_width=True)
        st.markdown('<div style="background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5rem;">PRIMEROS 12 MESES POR 19.90€</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("3D ALARMAS")
        if os.path.exists("tarifas_visuales/3d.jpg"):
            st.image("tarifas_visuales/3d.jpg", use_container_width=True)
        st.markdown('<div style="background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5rem;">PRIMEROS 12 MESES POR 24.20€</div>', unsafe_allow_html=True)

# --- COMPARADOR LUZ ---
elif menu == "⚖️ COMPARADOR LUZ":
    st.header("⚖️ Comparador de Luz")
    
    # 1. CARGA SEGURA DEL CSV
    # Saltamos las filas iniciales que no tienen datos de columna
    try:
        df = pd.read_csv("TARIFAS LUZ Y GAS JUNIO 2026.xlsx - Hoja1.csv", skiprows=2)
        df.columns = [str(c).strip() for c in df.columns]
        # Limpiar filas donde no hay comercial (quitar las filas vacías)
        df = df[df['COMERCIALIZADORA'].notna()]
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # 2. INTERFAZ
    c1, c2 = st.columns(2)
    with c1:
        f_act = st.number_input("Factura actual (€)", value=0.0)
        potencia = st.number_input("Potencia (kW)", value=4.6)
        dias = st.number_input("Días", value=30)
    
    with c2:
        comp_sel = st.selectbox("Compañía", df['COMERCIALIZADORA'].unique())
        # Filtramos por comercial
        opciones = df[df['COMERCIALIZADORA'] == comp_sel]
        # Usamos la columna real del CSV para la tarifa
        tarifa_sel = st.selectbox("Tarifa", opciones['COMERCIALIZADORA'].index)
        datos = opciones.loc[tarifa_sel]

    # 3. CÁLCULO
    col1, col2, col3 = st.columns(3)
    c_punta = col1.number_input("Consumo Punta (kWh)", value=0.0)
    c_llano = col2.number_input("Consumo Llano (kWh)", value=0.0)
    c_valle = col3.number_input("Consumo Valle (kWh)", value=0.0)

    # Convertimos los valores a números de forma segura
    def limpiar_num(val):
        return float(str(val).replace(',', '.').split()[0]) if pd.notnull(val) else 0.0

    precio_kwh = limpiar_num(datos['SIN SVA'])
    p1 = limpiar_num(datos['P1'])
    p2 = limpiar_num(datos['P2'])
    
    coste_energia = (c_punta + c_llano + c_valle) * precio_kwh
    coste_potencia = potencia * (p1 + p2) * dias
    total_propuesta = (coste_energia + coste_potencia) * 1.21 
    
    st.markdown(f"### AHORRO ESTIMADO: {f_act - total_propuesta:.2f} €")
# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🖼️ MATERIAL PUBLICITARIO</div>', unsafe_allow_html=True)
    
    path_anuncios = "anunciosbasette/"
    
    # Búsqueda automática de archivos en la carpeta
    if os.path.exists(path_anuncios):
        # Listamos todos los archivos que sean imágenes (png, jpg, jpeg)
        archivos = [f for f in os.listdir(path_anuncios) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not archivos:
            st.info("La carpeta 'anunciosbasette' está vacía o no contiene imágenes.")
        else:
            # Mostramos en rejilla de 3 columnas
            cols = st.columns(3)
            for idx, file_name in enumerate(archivos):
                with cols[idx % 3]:
                    full_path = os.path.join(path_anuncios, file_name)
                    
                    # Mostrar imagen
                    st.image(full_path, use_container_width=True)
                    
                    # Botón de descarga
                    with open(full_path, "rb") as f_anuncio:
                        mime = "image/png" if file_name.lower().endswith('.png') else "image/jpeg"
                        st.download_button(
                            label=f"📥 {file_name[:18]}...", # Nombre truncado para evitar romper el diseño
                            data=f_anuncio.read(),
                            file_name=file_name,
                            mime=mime,
                            key=f"btn_{idx}"
                        )
    else:
        st.error(f"La carpeta '{path_anuncios}' no existe en el directorio del proyecto. Por favor, verifica la ruta.")

# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        # 1. FUNCIÓN PARA IMÁGENES
        def get_img_64(file_path):
            import base64
            import os
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return None

        # 2. ANIMACIÓN DE PERRITOS (ROSCO)
        rosco_b64 = get_img_64("rosco.jpg")
        if rosco_b64:
            falling_items = ""
            for i in range(15): 
                left = random.randint(0, 95)
                delay = random.uniform(0, 3)
                dur = random.uniform(3, 6)
                size = random.randint(60, 100)
                falling_items += f'<img src="data:image/jpeg;base64,{rosco_b64}" class="rosco-fall" style="left:{left}%; animation-delay:{delay}s; animation-duration:{dur}s; width:{size}px;">'
            
            st.markdown(f"""
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9999; pointer-events: none;">
                    {falling_items}
                </div>
                <style>
                    .rosco-fall {{ position: absolute; top: -150px; opacity: 0.8; animation: fall linear forwards; }}
                    @keyframes fall {{ 0% {{ top: -150px; transform: rotate(0deg); opacity: 1; }} 100% {{ top: 110vh; transform: rotate(360deg); opacity: 0; }} }}
                </style>
            """, unsafe_allow_html=True)

        # 3. CARGA DE DATOS
        de, dt, da = load_and_clean_ranking()

        # 4. FILTROS Y VIDEO
        c_filtros, c_video = st.columns([2, 1])
        with c_filtros:
            st.markdown('<p style="color:#d2ff00; font-weight:bold; margin-bottom:0;">📅 FILTROS</p>', unsafe_allow_html=True)
            meses_disp = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
            f_mes = st.multiselect("Mes:", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
            coms_disp = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))
            f_coms = st.multiselect("Comerciales:", coms_disp, default=coms_disp)

        with c_video:
            video_file = "WhatsApp Video 2026-04-28 at 00.31.03.mp4"
            st.markdown('<p style="color:#d2ff00; font-size:0.7rem; text-align:right; margin-bottom:0;">🔊 Música Rosco</p>', unsafe_allow_html=True)
            st.video(video_file, format="video/mp4")

        # 5. APLICAR FILTROS Y LÓGICA DE COLUMNAS (Incluyendo Pte Firma)
        def procesar_df(df, es_energia=False, es_fibra=False):
            if df.empty: return df
            df = df[(df['Mes'].isin(f_mes)) & (df['Comercial'].isin(f_coms))].copy()
            if 'Canal' in df.columns:
                df['V_REF'] = df['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0)
            if 'Estado' in df.columns:
                df['Baja'] = df['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0)
                df['Cancel'] = df['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0)
                df['Pte_Firma'] = df['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "PTE FIRMA" else 0)
            return df

        f_de = procesar_df(de)
        f_dt = procesar_df(dt)
        f_da = procesar_df(da)

        r1 = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'V_REF', 'Baja', 'Cancel', 'Pte_Firma']].sum() if not f_de.empty else pd.DataFrame()
        r2 = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'V_REF', 'Baja', 'Cancel', 'Pte_Firma']].sum() if not f_dt.empty else pd.DataFrame()
        r3 = f_da.groupby('Comercial')[['V_Alarma', 'V_REF', 'Pte_Firma']].sum() if not f_da.empty else pd.DataFrame()
        
        rank = pd.concat([r1, r2, r3], axis=1).fillna(0)
        rank['REF'] = rank.filter(like='V_REF').sum(axis=1)
        rank['Bajas_Total'] = rank.filter(like='Baja').sum(axis=1)
        rank['Cancel_Total'] = rank.filter(like='Cancel').sum(axis=1)
        rank['Pte_Firma_Total'] = rank.filter(like='Pte_Firma').sum(axis=1)
        rank['Ventas_Sin_Movil'] = (rank.get('V_Luz',0) + rank.get('V_Gas',0) + rank.get('V_Fibra',0) + rank.get('V_Alarma',0))
        
        # TOTAL NETO: Sin contar Bajas, Cancelaciones ni Pte Firma
        rank['Total Neto'] = rank['Ventas_Sin_Movil'] - rank['Bajas_Total'] - rank['Cancel_Total'] - rank['Pte_Firma_Total']
        rank['Faltan para 25'] = rank.index.to_series().apply(lambda x: max(0, 25 - int(rank.loc[x, 'Total Neto'])) if "LUIS" not in str(x).upper() else 0)

        # 6. DETERMINAR EL Nº1
        nombre_n1, ventas_n1 = ("---", 0)
        if not rank.empty:
            top_comercial = rank.sort_values('Total Neto', ascending=False).iloc[0]
            nombre_n1, ventas_n1 = (top_comercial.name, int(top_comercial['Total Neto']))

        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <h1 style="color: #d2ff00; font-size: 2.1rem; margin-bottom:5px;">"EL ÉXITO ES EL RESULTADO DE LA DISCIPLINA DIARIA"</h1>
                <div style="background: rgba(210, 255, 0, 0.1); border: 2px solid #d2ff00; display: inline-block; padding: 10px 30px; border-radius: 50px; margin-top: 10px;">
                    <span style="color: white; font-size: 1.2rem;">🏆 Nº1 EN VENTAS NETAS: </span>
                    <span style="color: #d2ff00; font-size: 1.5rem; font-weight: bold;">{nombre_n1.upper()} ({ventas_n1})</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 7. TABLA DE RANKING (Incluyendo Pte Firma)
        df_vis = rank.rename(columns={'V_Luz':'Luz','V_Gas':'Gas','V_Fibra':'Fibra','V_Móvil':'Móvil','V_Alarma':'Alarma','Bajas_Total':'Bajas','Cancel_Total':'Cancelados','Pte_Firma_Total':'Pte Firma'})
        cols_tab = ['Luz','Gas','Fibra','Móvil','Alarma','REF','Bajas','Cancelados','Pte Firma','Total Neto','Faltan para 25']
        st.table(df_vis[[c for c in cols_tab if c in df_vis.columns]].astype(int).sort_values('Total Neto', ascending=False).style.apply(
            lambda x: ['background-color: rgba(210, 255, 0, 0.2); color: #d2ff00; font-weight: bold' if x.name in ['Total Neto', 'Faltan para 25'] else '' for i in x], axis=1))

        # 8. TOTALES BRUTOS Y GESTIÓN
        st.markdown("---")
        cx1, cx2, cx3, cx4 = st.columns(4)
        box_alt = "background:#161b22; border:1px solid #ff4b4b; padding:15px; border-radius:10px; text-align:center;"
        cx1.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCELACIONES</p><h3 style="color:white;margin:0;">{int(rank["Cancel_Total"].sum())}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS</p><h3 style="color:white;margin:0;">{int(rank["Bajas_Total"].sum())}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">PTE. FIRMA</p><h3 style="color:white;margin:0;">{int(rank["Pte_Firma_Total"].sum())}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box_alt} border:1px solid #d2ff00;"><p style="color:#d2ff00;font-size:0.75rem;margin:0;">TOTAL NETO</p><h3 style="color:white;margin:0;">{int(rank["Total Neto"].sum())}</h3></div>', unsafe_allow_html=True)

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
# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        # 1. FUNCIÓN DE CARGA ROBUSTA
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
                    df.columns = [c.strip() for c in df.columns]
                    # Convertir Marca temporal a Mes
                    if "Marca temporal" in df.columns:
                        df['Mes'] = pd.to_datetime(df["Marca temporal"], dayfirst=True, errors='coerce').dt.strftime('%Y-%m')
                    # Renombrar Comercial
                    if "¿Quién eres?" in df.columns:
                        df = df.rename(columns={"¿Quién eres?": "Comercial"})
                    dfs.append(df)
                except:
                    dfs.append(pd.DataFrame())
            return dfs[0], dfs[1], dfs[2]

        st.balloons() # Animación al abrir
        de, dt, da = load_and_clean_ranking()

        # 2. FILTROS
        c1, c2 = st.columns([2, 1])
        with c1:
            meses_disp = sorted(list(set(de.get('Mes', [])) | set(dt.get('Mes', [])) | set(da.get('Mes', []))))
            f_mes = st.multiselect("Mes:", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
            coms_disp = sorted(list(set(de.get('Comercial', [])) | set(dt.get('Comercial', [])) | set(da.get('Comercial', []))))
            f_coms = st.multiselect("Comerciales:", coms_disp, default=coms_disp)

        # 3. PROCESAMIENTO
        def filtrar_rank(df):
            if 'Mes' in df.columns and 'Comercial' in df.columns:
                return df[(df['Mes'].isin(f_mes)) & (df['Comercial'].isin(f_coms))].groupby('Comercial').sum(numeric_only=True)
            return pd.DataFrame()

        rank = pd.concat([filtrar_rank(de), filtrar_rank(dt), filtrar_rank(da)], axis=1).fillna(0)
        rank['Total Neto'] = rank.sum(axis=1)

        # 4. RANKING DESTACADO
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
            st.info("Selecciona filtros para visualizar.")

        # 5. CUADROS DE DESGLOSE
        st.markdown("### 📊 DESGLOSE DE CANCELACIONES Y BAJAS")
        cx1, cx2, cx3, cx4 = st.columns(4)
        box = "background:#161b22; border:1px solid #ff4b4b; padding:10px; border-radius:10px; text-align:center;"
        cx1.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">CANCEL. ENERGÍA</p><h3>{int(rank.filter(like="Cancel").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">CANCEL. FIBRA</p><h3>{int(rank.filter(like="Cancel").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">BAJAS ENERGÍA</p><h3>{int(rank.filter(like="Baja").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box}"><p style="font-size:0.7rem;">BAJAS FIBRA</p><h3>{int(rank.filter(like="Baja").sum().sum())}</h3></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error procesando dashboard: {e}")