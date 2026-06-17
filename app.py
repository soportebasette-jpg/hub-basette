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
    ["🚀 CRM", "📊 PRECIOS", "⚡ COMPARADOR ENERGÍA", "📶 COMPARADOR TELCO", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO", "🕒 CONTROL LABORAL", "🔐 ZONA DIRECTIVOS"]
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
        # Buscar la imagen en varios formatos posibles
        img_luz_gas = None
        for ext in ["luz_gas.jpeg", "luz_gas.jpg", "luz_gas.png"]:
            ruta_candidata = f"tarifas_visuales/{ext}"
            if os.path.exists(ruta_candidata):
                img_luz_gas = ruta_candidata
                break
        if img_luz_gas:
            st.image(img_luz_gas, use_container_width=True)
        else:
            st.warning("Imagen de Luz y Gas no encontrada en tarifas_visuales/ (se busca luz_gas.jpeg / .jpg / .png)")

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

# --- COMPARADOR ENERGÍA ---
elif menu == "⚡ COMPARADOR ENERGÍA":
    st.markdown('<div class="block-header">⚡ COMPARADOR DE ENERGÍA</div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="background:#161b22; border:2px solid #d2ff00; border-radius:15px; padding:30px; text-align:center; margin-bottom:30px;">
            <h2 style="color:#d2ff00; margin-bottom:10px;">🔗 Comparador de Luz y Gas</h2>
            <p style="color:#8b949e; font-size:1rem; margin-bottom:20px;">Accede a la herramienta de comparación de tarifas de energía para encontrar la mejor oferta para tu cliente.</p>
        </div>
    """, unsafe_allow_html=True)
    st.link_button("⚡ ABRIR COMPARADOR DE ENERGÍA", "https://soportebasette-jpg.github.io/Tecomparotodo/", use_container_width=True)

# --- COMPARADOR TELCO ---
elif menu == "📶 COMPARADOR TELCO":
    st.markdown('<div class="block-header">📶 COMPARADOR DE TELECOMUNICACIONES</div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="background:#161b22; border:2px solid #d2ff00; border-radius:15px; padding:30px; text-align:center; margin-bottom:30px;">
            <h2 style="color:#d2ff00; margin-bottom:10px;">🔗 Comparador de Telco</h2>
            <p style="color:#8b949e; font-size:1rem; margin-bottom:20px;">Accede a la herramienta de comparación de tarifas de telecomunicaciones para encontrar la mejor oferta de fibra y móvil para tu cliente.</p>
        </div>
    """, unsafe_allow_html=True)
    st.link_button("📶 ABRIR COMPARADOR DE TELCO", "https://soportebasette-jpg.github.io/Tecomparotodo-telco/telco.html", use_container_width=True)
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

# 9. TOTALES INFERIORES BRUTOS
        st.markdown("---")
        st.markdown('<p style="color:#d2ff00; font-weight:bold; text-align:center;">📊 TOTALES BRUTOS (VENTAS SIN DESCUENTOS)</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        box = "background:#0d1117; border:2px solid #d2ff00; padding:15px; border-radius:10px; text-align:center;"
        
        # Usamos filter(like=...) para que no dé error si la columna no existe
        c1.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ENERGÍA BRUTA</p><h2 style="color:white;margin:0;">{int(rank.filter(like="V_Luz").sum().sum() + rank.filter(like="V_Gas").sum().sum())}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">FIBRA BRUTA</p><h2 style="color:white;margin:0;">{int(rank.filter(like="V_Fibra").sum().sum())}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ALARMA BRUTA</p><h2 style="color:white;margin:0;">{int(rank.filter(like="V_Alarma").sum().sum())}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="{box} background:#d2ff00;"><p style="color:black;font-weight:bold;margin:0;">TOTAL BRUTO</p><h2 style="color:black;margin:0;">{int(rank["Ventas_Sin_Movil"].sum())}</h2></div>', unsafe_allow_html=True)

        # 10. CUADROS: CANCELACIONES, BAJAS Y PTE FIRMA (Corregidos)
        st.markdown("<br>", unsafe_allow_html=True)
        cx1, cx2, cx3, cx4, cx5 = st.columns(5)
        box_alt = "background:#161b22; border:1px solid #ff4b4b; padding:15px; border-radius:10px; text-align:center;"
        
        # Filtramos por columnas que contengan 'Cancel' o 'Baja' para no depender de nombres exactos
        cx1.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. ENERGÍA</p><h3 style="color:white;margin:0;">{int(rank.filter(like="Cancel_E").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. FIBRA</p><h3 style="color:white;margin:0;">{int(rank.filter(like="Cancel_F").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS ENERGÍA</p><h3 style="color:white;margin:0;">{int(rank.filter(like="Baja_E").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS FIBRA</p><h3 style="color:white;margin:0;">{int(rank.filter(like="Baja_F").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx5.markdown(f'<div style="{box_alt} border:1px solid #d2ff00;"><p style="color:#d2ff00;font-size:0.75rem;margin:0;">PTE. FIRMA</p><h3 style="color:white;margin:0;">{int(rank["Pte_Firma_Total"].sum())}</h3></div>', unsafe_allow_html=True)
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

        # 2. ANIMACIÓN DE PERRITOS (ROSCO) - NO INFINITA
        rosco_b64 = get_img_64("rosco.jpg")
        if rosco_b64:
            falling_items = ""
            for i in range(15):  # Número de perritos
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
                    .rosco-fall {{ 
                        position: absolute; 
                        top: -150px; 
                        opacity: 0.8; 
                        animation: fall linear forwards; 
                    }}
                    @keyframes fall {{ 
                        0% {{ top: -150px; transform: rotate(0deg); opacity: 1; }} 
                        100% {{ top: 110vh; transform: rotate(360deg); opacity: 0; }} 
                    }}
                </style>
            """, unsafe_allow_html=True)

        # 3. CARGA DE DATOS
        de, dt, da = load_and_clean_ranking()

        # 4. FILTROS (IZQUIERDA) Y VIDEO (DERECHA)
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

        # 4. APLICAR FILTROS
        f_de = de[(de['Mes'].isin(f_mes)) & (de['Comercial'].isin(f_coms))].copy()
        f_dt = dt[(dt['Mes'].isin(f_mes)) & (dt['Comercial'].isin(f_coms))].copy()
        f_da = da[(da['Mes'].isin(f_mes)) & (da['Comercial'].isin(f_coms))].copy()

        # 5. PROCESAMIENTO DETALLADO
        if not f_de.empty:
            f_de['V_REF'] = f_de['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0) if 'Canal' in f_de.columns else 0
            f_de['Baja_E'] = f_de['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0) if 'Estado' in f_de.columns else 0
            f_de['Cancel_E'] = f_de['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0) if 'Estado' in f_de.columns else 0

        if not f_dt.empty:
            f_dt['V_REF'] = f_dt['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0) if 'Canal' in f_dt.columns else 0
            f_dt['Baja_F'] = f_dt['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0) if 'Estado' in f_dt.columns else 0
            f_dt['Cancel_F'] = f_dt['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0) if 'Estado' in f_dt.columns else 0

        if not f_da.empty:
            f_da['V_REF'] = f_da['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0) if 'Canal' in f_da.columns else 0
            f_da['Baja_A'] = f_da['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0) if 'Estado' in f_da.columns else 0
            f_da['Cancel_A'] = f_da['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0) if 'Estado' in f_da.columns else 0

        r1 = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'V_REF', 'Baja_E', 'Cancel_E']].sum() if not f_de.empty else pd.DataFrame()
        r2 = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'V_REF', 'Baja_F', 'Cancel_F']].sum() if not f_dt.empty else pd.DataFrame()
        r3 = f_da.groupby('Comercial')[['V_Alarma', 'V_REF']].sum() if not f_da.empty else pd.DataFrame()
        
        rank = pd.concat([r1, r2, r3], axis=1).fillna(0)
        rank['REF'] = rank.filter(like='V_REF').sum(axis=1)
        rank['Bajas_Total'] = rank.filter(like='Baja_').sum(axis=1)
        rank['Cancel_Total'] = rank.filter(like='Cancel_').sum(axis=1)
        rank['Ventas_Sin_Movil'] = (rank.get('V_Luz',0) + rank.get('V_Gas',0) + rank.get('V_Fibra',0) + rank.get('V_Alarma',0))
        
        # Total Neto para el objetivo individual
        rank['Total Neto'] = rank['Ventas_Sin_Movil'] - rank['Bajas_Total'] - rank['Cancel_Total']
        rank['Faltan para 25'] = rank.index.to_series().apply(lambda x: max(0, 25 - int(rank.loc[x, 'Total Neto'])) if "LUIS" not in str(x).upper() else 0)

        # 6. CABECERA TÍTULO (Sin Nº1)
        st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <h1 style="color: #d2ff00; font-size: 2.1rem; margin-bottom:5px;">"EL ÉXITO ES EL RESULTADO DE LA DISCIPLINA DIARIA"</h1>
            </div>
        """, unsafe_allow_html=True)

        # 7. OBJETIVO EQUIPO
        v_equipo_neta = int(rank['Total Neto'].sum())
        v_falta_equipo = max(0, 75 - v_equipo_neta)
        st.markdown(f'<div style="background:#161b22;padding:15px;border-radius:15px;border:1px solid #30363d;margin:0 auto 20px auto;text-align:center;max-width:320px;"><p style="color:#d2ff00;margin:0;font-weight:bold;font-size:0.9rem;">🚀 FALTAN PARA EL OBJETIVO</p><h1 style="color:white;margin:0;font-size:2.8rem;">{v_falta_equipo}</h1></div>', unsafe_allow_html=True)

        # 8. TABLA DE RANKING
        df_vis = rank.rename(columns={'V_Luz':'Luz','V_Gas':'Gas','V_Fibra':'Fibra','V_Móvil':'Móvil','V_Alarma':'Alarma','Bajas_Total':'Bajas','Cancel_Total':'Cancelados'})
        cols_tab = ['Luz','Gas','Fibra','Móvil','Alarma','REF','Bajas','Cancelados','Total Neto','Faltan para 25']
        st.table(df_vis[[c for c in cols_tab if c in df_vis.columns]].astype(int).sort_values('Total Neto', ascending=False).style.apply(
            lambda x: ['background-color: rgba(210, 255, 0, 0.2); color: #d2ff00; font-weight: bold' if x.name in ['Total Neto', 'Faltan para 25'] else '' for i in x], axis=1))

        # 9. TOTALES INFERIORES BRUTOS
        st.markdown("---")
        st.markdown('<p style="color:#d2ff00; font-weight:bold; text-align:center;">📊 TOTALES BRUTOS (VENTAS SIN DESCUENTOS)</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        box = "background:#0d1117; border:2px solid #d2ff00; padding:15px; border-radius:10px; text-align:center;"
        
        c1.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ENERGÍA BRUTA</p><h2 style="color:white;margin:0;">{int(rank["V_Luz"].sum() + rank["V_Gas"].sum()) if "V_Luz" in rank else 0}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">FIBRA BRUTA</p><h2 style="color:white;margin:0;">{int(rank["V_Fibra"].sum()) if "V_Fibra" in rank else 0}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ALARMA BRUTA</p><h2 style="color:white;margin:0;">{int(rank["V_Alarma"].sum()) if "V_Alarma" in rank else 0}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="{box} background:#d2ff00;"><p style="color:black;font-weight:bold;margin:0;">TOTAL BRUTO</p><h2 style="color:black;margin:0;">{int(rank["Ventas_Sin_Movil"].sum())}</h2></div>', unsafe_allow_html=True)

        # 10. NUEVOS CUADROS: CANCELACIONES Y BAJAS
        st.markdown("<br>", unsafe_allow_html=True)
        cx1, cx2, cx3, cx4 = st.columns(4)
        box_alt = "background:#161b22; border:1px solid #ff4b4b; padding:15px; border-radius:10px; text-align:center;"
        
        cx1.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. ENERGÍA</p><h3 style="color:white;margin:0;">{int(rank["Cancel_E"].sum()) if "Cancel_E" in rank else 0}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. FIBRA</p><h3 style="color:white;margin:0;">{int(rank["Cancel_F"].sum()) if "Cancel_F" in rank else 0}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS ENERGÍA</p><h3 style="color:white;margin:0;">{int(rank["Baja_E"].sum()) if "Baja_E" in rank else 0}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS FIBRA</p><h3 style="color:white;margin:0;">{int(rank["Baja_F"].sum()) if "Baja_F" in rank else 0}</h3></div>', unsafe_allow_html=True)

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

# --- CONTROL LABORAL ---
elif menu == "🕒 CONTROL LABORAL":
    import pandas as pd
    import calendar
    from datetime import datetime, time, date
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL Y ASISTENCIA</div>', unsafe_allow_html=True)
    
    # ── BAJAS DE EMPRESA ── (no cuentan como falta durante su periodo en la empresa)
    # fecha_alta: primer día que trabaja | fecha_baja: último día que trabaja (None = sigue activa)
    empleados_empresa = {
        "BELEN TRONCOSO CAMPOS":      {"alta": date(2026, 3, 16), "baja": date(2026, 5, 20)},
        "DEBORAH RODRIGUEZ URBINA":   {"alta": date(2026, 3, 16), "baja": date(2026, 5, 13)},
        "LORENA POZO ALVAREZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 6, 17)},
        "MACARENA BACA LOPEZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 3, 19)},
        "LUIS RODRIGUEZ GOMEZ":       {"alta": date(2025, 4,  6), "baja": date(2026, 4, 24)},
        "MARIA JOSE MORENO":          {"alta": date(2026, 5,  4), "baja": date(2026, 5, 18)},
        "LAURA RUBIO GARCIA":         {"alta": date(2026, 5, 25), "baja": date(2026, 5, 27)},
        "MARIA JOSE ARACIL RUEDA":    {"alta": date(2026, 5,  4), "baja": None},   # activa
        "RAQUEL GUADALUPE CASTILLO":  {"alta": date(2026, 3, 2), "baja": None},    # activa
    }

    # Periodo de gracia: del 02/03 al 18/03 Raquel aparece como OK aunque no haya fichado
    PERIODOS_GRACIA = {
        "RAQUEL GUADALUPE CASTILLO": (date(2026, 3, 2), date(2026, 3, 18)),
    }

    def empleado_activo_en_fecha(nombre_comercial, fecha):
        nombre_up = nombre_comercial.upper()
        for emp, periodos in empleados_empresa.items():
            if emp.upper() in nombre_up or nombre_up in emp.upper():
                alta = periodos["alta"]
                baja = periodos["baja"]
                if alta <= fecha:
                    if baja is None or fecha <= baja:
                        return True
        return False

    def en_periodo_gracia(nombre_comercial, fecha):
        nombre_up = nombre_comercial.upper()
        for emp, (inicio, fin) in PERIODOS_GRACIA.items():
            if emp.upper() in nombre_up or nombre_up in emp.upper():
                if inicio <= fecha <= fin:
                    return True
        return False

    # ── VACACIONES ──
    vacaciones = {
        "RAQUEL GUADALUPE": (date(2026, 6, 22), date(2026, 6, 28)),
        "MARIA JOSE ARACIL": (date(2026, 8, 3), date(2026, 8, 9))
    }

    # ── PANEL DE INFO ──
    tab_vac, tab_emp = st.tabs(["🏖️ Vacaciones Programadas", "👥 Plantilla / Bajas Empresa"])

    with tab_vac:
        cols = st.columns(len(vacaciones))
        for i, (nombre, (inicio, fin)) in enumerate(vacaciones.items()):
            dias_hasta = (inicio - date.today()).days
            estado_color = "#d2ff00" if dias_hasta > 7 else "#ffaa00" if dias_hasta > 0 else "#7ee787"
            cols[i].markdown(f"""
                <div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid {estado_color}; text-align:center;">
                <p style="margin:0; font-size:0.85rem; color:{estado_color}; font-weight:bold;">{nombre}</p>
                <b style="font-size:1rem; color:white;">{inicio.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}</b>
                <p style="margin:4px 0 0 0; font-size:0.75rem; color:#8b949e;">{(fin - inicio).days + 1} días laborables</p>
                </div>
            """, unsafe_allow_html=True)

    with tab_emp:
        st.markdown('<p style="color:#8b949e; font-size:0.85rem; margin-bottom:10px;">Los días fuera del rango Alta–Baja se marcan como <b style="color:#888">BAJA EMPRESA</b> y no computan como falta.</p>', unsafe_allow_html=True)
        activas = {k: v for k, v in empleados_empresa.items() if v["baja"] is None}
        bajas   = {k: v for k, v in empleados_empresa.items() if v["baja"] is not None}
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p style="color:#7ee787; font-weight:bold;">✅ Activas en plantilla</p>', unsafe_allow_html=True)
            for nombre, p in activas.items():
                st.markdown(f'<div style="background:#0d2818; border:1px solid #7ee787; border-radius:8px; padding:8px 12px; margin-bottom:6px;"><span style="color:white; font-size:0.9rem;">{nombre}</span><br><span style="color:#8b949e; font-size:0.75rem;">Alta: {p["alta"].strftime("%d/%m/%Y")}</span></div>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<p style="color:#ff4b4b; font-weight:bold;">📋 Bajas procesadas</p>', unsafe_allow_html=True)
            for nombre, p in bajas.items():
                st.markdown(f'<div style="background:#1a0a0a; border:1px solid #30363d; border-radius:8px; padding:8px 12px; margin-bottom:6px;"><span style="color:#8b949e; font-size:0.9rem;">{nombre}</span><br><span style="color:#8b949e; font-size:0.75rem;">Alta: {p["alta"].strftime("%d/%m/%Y")} · Baja: {p["baja"].strftime("%d/%m/%Y")}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

    try:
        # ── CARGA Y LIMPIEZA ──
        sheet_id = "175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY"
        url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df_laboral = pd.read_csv(url_csv)
        df_laboral.columns = [str(c).strip().upper() for c in df_laboral.columns]
        
        col_comercial = next((c for c in df_laboral.columns if "QUIÉN" in c or "COMERCIAL" in c), None)
        col_temporal  = next((c for c in df_laboral.columns if "TEMPORAL" in c or "MARCA" in c), None)
        col_accion    = next((c for c in df_laboral.columns if "HACER" in c), None)
        
        df_laboral[col_temporal] = pd.to_datetime(df_laboral[col_temporal], dayfirst=True, errors='coerce')
        df_laboral = df_laboral.dropna(subset=[col_temporal, col_comercial])

        # ── FILTROS ──
        col_f1, col_f2 = st.columns(2)
        coms    = sorted(df_laboral[col_comercial].unique().astype(str))
        com_sel = col_f1.selectbox("👤 Selecciona Comercial", coms)
        mes_sel = col_f2.selectbox("📅 Selecciona Mes", range(1, 13), index=datetime.now().month - 1)

        # ── BADGE HORARIO DEL COMERCIAL SELECCIONADO ──
        if "RAQUEL" in com_sel.upper() and "GUADALUPE" in com_sel.upper():
            st.markdown('<div style="background:#1a1a2e; border:1px solid #FFD700; border-radius:8px; padding:8px 16px; margin-bottom:10px; display:inline-block;"><span style="color:#FFD700; font-weight:bold;">⏰ Horario:</span> <span style="color:white;">09:00 – 14:30 · 17:00 – 19:30 (turno partido)</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:8px 16px; margin-bottom:10px; display:inline-block;"><span style="color:#d2ff00; font-weight:bold;">⏰ Horario:</span> <span style="color:white;">09:30 – 14:30</span></div>', unsafe_allow_html=True)

        # ── LÓGICA DE AUDITORÍA ──
        festivos = [
            date(2026, 4, 2), date(2026, 4, 3), date(2026, 4, 22),
            date(2026, 5, 1), date(2026, 5, 29), date(2026, 6, 4)
        ]

        # ── HORARIOS POR COMERCIAL ──
        # General: 9:30 – 14:30 (comerciales)
        # Raquel:  9:00 – 14:30 + 17:00 – 19:30 (turno partido)
        def get_horario(nombre):
            if "RAQUEL" in nombre.upper() and "GUADALUPE" in nombre.upper():
                return {
                    "entrada": time(9, 0),
                    "partido": True,
                    "tarde_inicio": time(17, 0),
                    "tarde_fin":    time(19, 30),
                }
            return {
                "entrada": time(9, 30),
                "partido": False,
            }

        datos = df_laboral[
            (df_laboral[col_comercial] == com_sel) &
            (df_laboral[col_temporal].dt.month == mes_sel)
        ].copy()

        horario = get_horario(com_sel)
        hora_entrada_limite = horario["entrada"]
        es_turno_partido = horario.get("partido", False)

        min_ret, faltas, dias_vac, dias_baja_emp = 0, 0, 0, 0
        historial_diario = []
        dias_mes = calendar.monthrange(2026, mes_sel)[1]

        for d in range(1, dias_mes + 1):
            fecha = date(2026, mes_sel, d)
            if fecha > date.today(): break
            if fecha.weekday() >= 5 or fecha in festivos: continue

            # ── Baja de empresa: no computa ──
            activo = empleado_activo_en_fecha(com_sel, fecha)
            if not activo:
                dias_baja_emp += 1
                historial_diario.append({
                    "Fecha": fecha, "Entrada": "-", "Salida": "-",
                    "Incidencia": "🔴 BAJA EMPRESA"
                })
                continue

            # ── Vacaciones ──
            es_vac = any(com_sel.upper() in nom.upper() and i <= fecha <= f for nom, (i, f) in vacaciones.items())
            if es_vac:
                dias_vac += 1
                historial_diario.append({
                    "Fecha": fecha, "Entrada": "-", "Salida": "-",
                    "Incidencia": "🏖️ VACACIONES"
                })
                continue

            dia_data = datos[datos[col_temporal].dt.date == fecha]
            entradas = dia_data[dia_data[col_accion].str.contains("ENTRADA", case=False, na=False)]
            salidas  = dia_data[dia_data[col_accion].str.contains("SALIDA",  case=False, na=False)]

            h_in  = entradas[col_temporal].min().time() if not entradas.empty else None
            h_out = salidas[col_temporal].max().time()  if not salidas.empty  else None

            if not entradas.empty:
                incidencia = "✅ OK"

                # ── Cálculo retraso entrada ──
                if h_in > hora_entrada_limite:
                    retraso = (datetime.combine(fecha, h_in) - datetime.combine(fecha, hora_entrada_limite)).total_seconds() / 60
                    min_ret += retraso
                    incidencia = f"⚠️ RETRASO ENTRADA ({int(retraso)}m)"

                # ── Turno partido (Raquel): usa un único login/logout, no se comprueba tarde ──
                if es_turno_partido:
                    historial_diario.append({
                        "Fecha":    fecha,
                        "Entrada":  str(h_in)[:5] if h_in else "-",
                        "Salida":   str(h_out)[:5] if h_out else "—",
                        "Incidencia": incidencia
                    })
                else:
                    historial_diario.append({
                        "Fecha":   fecha,
                        "Entrada": str(h_in)[:5] if h_in else "-",
                        "Salida":  str(h_out)[:5] if h_out else "—",
                        "Incidencia": incidencia
                    })
            else:
                # Periodo de gracia → OK aunque no haya fichaje
                if en_periodo_gracia(com_sel, fecha):
                    historial_diario.append({
                        "Fecha": fecha, "Entrada": "—", "Salida": "—", "Incidencia": "✅ OK"
                    })
                else:
                    faltas += 1
                    historial_diario.append({
                        "Fecha": fecha, "Entrada": "-", "Salida": "-", "Incidencia": "❌ FALTA"
                    })

        # ── DASHBOARD MÉTRICAS ──
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div style="background:#262730; padding:15px; border-radius:10px; border-left:8px solid #ff4b4b; text-align:center;"><p style="color:#ff4b4b; font-size:0.8rem; margin:0; font-weight:bold;">⏰ RETRASO ACUM.</p><h1 style="color:white; margin:5px 0;">{int(min_ret)} m</h1></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="background:#262730; padding:15px; border-radius:10px; border-left:8px solid #ffaa00; text-align:center;"><p style="color:#ffaa00; font-size:0.8rem; margin:0; font-weight:bold;">❌ FALTAS</p><h1 style="color:white; margin:5px 0;">{faltas}</h1></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="background:#262730; padding:15px; border-radius:10px; border-left:8px solid #7ee787; text-align:center;"><p style="color:#7ee787; font-size:0.8rem; margin:0; font-weight:bold;">🏖️ VACACIONES</p><h1 style="color:white; margin:5px 0;">{dias_vac} d</h1></div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="background:#262730; padding:15px; border-radius:10px; border-left:8px solid #8b949e; text-align:center;"><p style="color:#8b949e; font-size:0.8rem; margin:0; font-weight:bold;">🔴 BAJA EMPRESA</p><h1 style="color:white; margin:5px 0;">{dias_baja_emp} d</h1></div>', unsafe_allow_html=True)
        
        st.markdown("---")

        # ── TABLA HISTORIAL ──
        if historial_diario:
            df_hist = pd.DataFrame(historial_diario).sort_values("Fecha", ascending=False)
            df_hist["Fecha"] = df_hist["Fecha"].apply(lambda x: x.strftime("%a %d/%m/%Y").upper())

            def color_incidencia(val):
                if "FALTA" in val:       return "background-color: rgba(255,75,75,0.2); color: #ff4b4b; font-weight:bold"
                if "RETRASO" in val:     return "background-color: rgba(255,170,0,0.2); color: #ffaa00; font-weight:bold"
                if "VACACIONES" in val:  return "background-color: rgba(126,231,135,0.15); color: #7ee787"
                if "BAJA EMPRESA" in val:return "background-color: rgba(139,148,158,0.15); color: #8b949e"
                return "color: #7ee787"

            try:
                styled = df_hist.style.map(color_incidencia, subset=["Incidencia"])
            except AttributeError:
                styled = df_hist.style.applymap(color_incidencia, subset=["Incidencia"])
            st.dataframe(styled, use_container_width=True, height=450)
        else:
            st.info("Sin registros en este periodo.")

    except Exception as e:
        st.error(f"Error procesando datos: {e}")

# ══════════════════════════════════════════════════════
# --- ZONA DIRECTIVOS ---
# ══════════════════════════════════════════════════════
elif menu == "🔐 ZONA DIRECTIVOS":
    import os
    from datetime import datetime

    # ── CSS adicional para la zona directivos ──
    st.markdown("""
        <style>
        .dir-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border: 2px solid #gold;
            border-image: linear-gradient(135deg, #FFD700, #FFA500) 1;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }
        .dir-card {
            background: linear-gradient(135deg, #161b22, #1c2430);
            border: 1px solid #FFD700;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 12px;
            transition: all 0.3s;
        }
        .dir-card:hover { border-color: #FFA500; transform: translateY(-3px); }
        .gold-badge {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: black;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── AUTENTICACIÓN DIRECTIVOS ──
    if "dir_auth" not in st.session_state:
        st.session_state["dir_auth"] = False

    if not st.session_state["dir_auth"]:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460); border:2px solid #FFD700;
                        border-radius:20px; padding:40px; text-align:center; max-width:450px; margin:60px auto;">
                <h1 style="color:#FFD700; font-size:2.5rem; margin-bottom:5px;">🔐</h1>
                <h2 style="color:#FFD700; margin-bottom:5px;">ZONA DIRECTIVOS</h2>
                <p style="color:#8b949e; font-size:0.9rem;">Acceso restringido · Basette Group</p>
            </div>
        """, unsafe_allow_html=True)

        _, col_dir, _ = st.columns([1, 1.2, 1])
        with col_dir:
            pwd_dir = st.text_input("🔑 Clave Directivos:", type="password", key="pwd_dir_input")
            if st.button("ACCEDER A ZONA DIRECTIVOS", use_container_width=True):
                if pwd_dir == "Directivos2026*":
                    st.session_state["dir_auth"] = True
                    st.rerun()
                else:
                    st.error("❌ Clave incorrecta. Acceso denegado.")
        st.stop()

    # ── CONTENIDO ZONA DIRECTIVOS (solo si autenticado) ──
    st.markdown("""
        <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460); border:2px solid #FFD700;
                    border-radius:15px; padding:25px; text-align:center; margin-bottom:25px;">
            <h2 style="color:#FFD700; margin:0;">🏛️ ZONA DIRECTIVOS · BASETTE GROUP</h2>
            <p style="color:#8b949e; margin:5px 0 0 0; font-size:0.85rem;">Área de acceso restringido · Documentación confidencial</p>
        </div>
    """, unsafe_allow_html=True)

    # Botón cerrar sesión directivos
    col_cerrar = st.columns([5, 1])
    with col_cerrar[1]:
        if st.button("🔒 Cerrar sesión", key="cerrar_dir"):
            st.session_state["dir_auth"] = False
            st.rerun()

    # ── TABS PRINCIPALES ──
    tab_rrhh, tab_ret, tab_nom, tab_liq, tab_docs, tab_sop = st.tabs([
        "👥 PERSONAL",
        "💰 MARCOS RETRIBUTIVOS",
        "💼 NÓMINAS",
        "📊 LIQUIDACIONES",
        "📁 DOCS EMPRESA",
        "🛠️ SOPORTE"
    ])

    # ══════════════════════════════════════════════════════
    # ── GOOGLE DRIVE — ID raíz de BASETTE_DIRECTIVOS ──
    # ══════════════════════════════════════════════════════
    DRIVE_ROOT_ID = "1BC-HcnyFYnHZKM3BoOhKNkR4m7GSCVng"
    DRIVE_API_KEY = "AIzaSyC3IZUOEtnV9jr8wuKqZ6163Cf8DDjj0Wk"

    import urllib.request, urllib.parse, json as _json

    @st.cache_data(ttl=300, show_spinner=False)
    def drive_list_folder(folder_id):
        """Lista todo el contenido de una carpeta de Drive usando API Key."""
        try:
            q      = urllib.parse.quote(f"'{folder_id}' in parents and trashed=false")
            fields = urllib.parse.quote("files(id,name,mimeType,size)")
            url = (
                f"https://www.googleapis.com/drive/v3/files"
                f"?q={q}&fields={fields}&orderBy=name&key={DRIVE_API_KEY}"
            )
            with urllib.request.urlopen(url, timeout=10) as r:
                data = _json.loads(r.read())
            return data.get("files", [])
        except Exception:
            return []

    @st.cache_data(ttl=300, show_spinner=False)
    def drive_find_subfolder(parent_id, name):
        """Devuelve el ID de una subcarpeta por nombre (case-insensitive)."""
        items = drive_list_folder(parent_id)
        for item in items:
            if (item.get("mimeType") == "application/vnd.google-apps.folder"
                    and item.get("name", "").strip().upper() == name.strip().upper()):
                return item["id"]
        return None

    @st.cache_data(ttl=300, show_spinner=False)
    def drive_folder_id_by_path(path_tuple):
        """Navega la jerarquía por nombres. path_tuple = ("NOMINAS","2026","JUNIO")"""
        current_id = DRIVE_ROOT_ID
        for part in path_tuple:
            current_id = drive_find_subfolder(current_id, part)
            if not current_id:
                return None
        return current_id

    def mostrar_carpeta_drive(path_parts, icono="📄"):
        """Muestra archivos de una carpeta Drive con botón para abrirlos."""
        folder_id = drive_folder_id_by_path(tuple(path_parts))
        if not folder_id:
            st.caption(f"🚫 Carpeta no encontrada en Drive: {' / '.join(path_parts)}")
            st.info("Comprueba que la carpeta existe y que Drive está compartido como **Cualquiera con el enlace puede ver**.")
            return

        items    = drive_list_folder(folder_id)
        archivos = [f for f in items if f.get("mimeType") != "application/vnd.google-apps.folder"]

        if not archivos:
            st.info("📭 Carpeta vacía. Sube archivos a Drive para que aparezcan aquí.")
            return

        for f in archivos:
            fid      = f["id"]
            fname    = f["name"]
            size_kb  = int(f.get("size", 0)) // 1024 if f.get("size") else 0
            size_str = f" · {size_kb} KB" if size_kb else ""
            view_url = f"https://drive.google.com/file/d/{fid}/view"

            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(
                    f'<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; '
                    f'padding:8px 12px; margin-bottom:4px;">'
                    f'<span style="color:white; font-size:0.9rem;">{icono} {fname}</span>'
                    f'<span style="color:#8b949e; font-size:0.75rem;">{size_str}</span></div>',
                    unsafe_allow_html=True
                )
            with col_b:
                st.link_button("⬇️ Abrir", view_url, use_container_width=True)

    def mostrar_carpeta_dir(ruta_base, nombre_carpeta, icono="📄"):
        """Wrapper de compatibilidad: traduce rutas locales a path_parts de Drive."""
        parts = [p for p in nombre_carpeta.replace("\\", "/").split("/") if p]
        mostrar_carpeta_drive(parts, icono)


        # ── TAB PERSONAL ──
    with tab_rrhh:
        st.markdown('<div class="block-header">👥 GESTIÓN DE PERSONAL</div>', unsafe_allow_html=True)

        # Resumen de plantilla actual
        from datetime import date
        empleados_dir = {
            "RAQUEL GUADALUPE CASTILLO":  {"alta": date(2026, 3, 2),  "baja": None,           "estado": "✅ ACTIVA"},
            "MARIA JOSE ARACIL RUEDA":    {"alta": date(2026, 5,  4), "baja": None,           "estado": "✅ ACTIVA"},
            "BELEN TRONCOSO CAMPOS":      {"alta": date(2026, 3, 16), "baja": date(2026, 5, 20), "estado": "🔴 BAJA"},
            "DEBORAH RODRIGUEZ URBINA":   {"alta": date(2026, 3, 16), "baja": date(2026, 5, 13), "estado": "🔴 BAJA"},
            "LORENA POZO ALVAREZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 6, 17), "estado": "🔴 BAJA"},
            "MACARENA BACA LOPEZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 3, 19), "estado": "🔴 BAJA"},
            "LUIS RODRIGUEZ GOMEZ":       {"alta": date(2025, 4,  6), "baja": date(2026, 4, 24), "estado": "🔴 BAJA"},
            "MARIA JOSE MORENO":          {"alta": date(2026, 5,  4), "baja": date(2026, 5, 18), "estado": "🔴 BAJA"},
            "LAURA RUBIO GARCIA":         {"alta": date(2026, 5, 25), "baja": date(2026, 5, 27), "estado": "🔴 BAJA"},
        }

        activos = [k for k, v in empleados_dir.items() if v["baja"] is None]
        bajas_e = [k for k, v in empleados_dir.items() if v["baja"] is not None]

        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.markdown(f'<div style="background:#0d2818;border:2px solid #7ee787;border-radius:12px;padding:20px;text-align:center;"><p style="color:#7ee787;margin:0;font-weight:bold;font-size:0.85rem;">ACTIVOS</p><h1 style="color:white;margin:5px 0;">{len(activos)}</h1></div>', unsafe_allow_html=True)
        col_res2.markdown(f'<div style="background:#1a0a0a;border:2px solid #ff4b4b;border-radius:12px;padding:20px;text-align:center;"><p style="color:#ff4b4b;margin:0;font-weight:bold;font-size:0.85rem;">BAJAS HISTÓRICAS</p><h1 style="color:white;margin:5px 0;">{len(bajas_e)}</h1></div>', unsafe_allow_html=True)
        col_res3.markdown(f'<div style="background:#161b22;border:2px solid #FFD700;border-radius:12px;padding:20px;text-align:center;"><p style="color:#FFD700;margin:0;font-weight:bold;font-size:0.85rem;">TOTAL HISTORIAL</p><h1 style="color:white;margin:5px 0;">{len(empleados_dir)}</h1></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        df_personal = pd.DataFrame([
            {
                "Nombre": k,
                "Alta": v["alta"].strftime("%d/%m/%Y"),
                "Baja": v["baja"].strftime("%d/%m/%Y") if v["baja"] else "—",
                "Estado": v["estado"],
                "Días en empresa": (v["baja"] - v["alta"]).days if v["baja"] else (date.today() - v["alta"]).days
            }
            for k, v in empleados_dir.items()
        ])
        st.dataframe(df_personal, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown('<div class="block-header">📂 DOCUMENTACIÓN DE PERSONAL</div>', unsafe_allow_html=True)
        st.markdown("Los archivos se leen desde Google Drive · Carpeta **PERSONAL**")
        mostrar_carpeta_dir("directivos", "PERSONAL", "📋")

    # ── TAB MARCOS RETRIBUTIVOS ──
    with tab_ret:
        st.markdown('<div class="block-header">💰 MARCOS RETRIBUTIVOS</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background:#161b22; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                <p style="color:#FFD700; font-weight:bold; margin:0;">ℹ️ ÁREA CONFIDENCIAL</p>
                <p style="color:#8b949e; margin:5px 0 0 0; font-size:0.85rem;">Los documentos de estructura salarial, bandas retributivas y comisiones se gestionan aquí.</p>
            </div>
        """, unsafe_allow_html=True)
        col_ret1, col_ret2 = st.columns(2)
        with col_ret1:
            with st.expander("📈 Escala de Comisiones"):
                mostrar_carpeta_dir("directivos", "COMISIONES", "💰")
            with st.expander("🏷️ Bandas Salariales"):
                mostrar_carpeta_dir("directivos", "BANDAS_SALARIALES", "💼")
        with col_ret2:
            with st.expander("🎯 Objetivos e Incentivos"):
                mostrar_carpeta_dir("directivos", "INCENTIVOS", "🎯")
            with st.expander("📋 Contratos y Acuerdos"):
                mostrar_carpeta_dir("directivos", "CONTRATOS", "📋")

    # ── TAB NÓMINAS ──
    with tab_nom:
        st.markdown('<div class="block-header">💼 GESTIÓN DE NÓMINAS</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background:#161b22; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                <p style="color:#8b949e; margin:0; font-size:0.85rem;">Los archivos se leen desde Google Drive · Carpeta <b style="color:#FFD700;">NOMINAS / AÑO / MES</b></p>
            </div>
        """, unsafe_allow_html=True)

        meses_nom = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
                     "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
        col_nom_sel1, col_nom_sel2 = st.columns(2)
        anio_nom = col_nom_sel1.selectbox("📅 Año", ["2026", "2025", "2024"], key="anio_nom")
        mes_nom  = col_nom_sel2.selectbox("📅 Mes", meses_nom, index=datetime.now().month - 1, key="mes_nom")

        mostrar_carpeta_drive(["NOMINAS", anio_nom, mes_nom], "💼")

    # ── TAB LIQUIDACIONES ──
    with tab_liq:
        st.markdown('<div class="block-header">📊 LIQUIDACIONES AUTOMÁTICAS</div>', unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════
        # ── FUNCIONES DE CRUCE DE LIQUIDACIONES ──
        # ══════════════════════════════════════════════════════

        def normalize_cup(cup):
            """Normaliza CUP a 20 dígitos para comparación (si tiene 22, trunca)."""
            if cup is None or (hasattr(cup, '__class__') and cup.__class__.__name__ == 'float'):
                return None
            import math
            try:
                if math.isnan(float(str(cup))):
                    return None
            except (ValueError, TypeError):
                pass
            s = str(cup).strip().upper()
            if not s or s in ['NAN', 'NONE', '']:
                return None
            # Si tiene 22 chars, los primeros 20 son el CUP canónico
            if len(s) == 22:
                return s[:20]
            return s

        def extraer_meta_liquidacion(df_raw):
            """Extrae metadatos del encabezado de la liquidación."""
            meta = {'mes': '', 'anio': '', 'factura': '', 'nombre': '', 'empresa': ''}
            for i in range(0, 12):
                row = df_raw.iloc[i]
                vals = row.tolist()
                for j, v in enumerate(vals):
                    sv = str(v).strip()
                    if sv == 'Mes:' and j + 2 < len(vals):
                        try:
                            meta['mes'] = str(int(float(str(vals[j+2]))))
                        except Exception:
                            pass
                    if sv == 'Año:' and j + 2 < len(vals):
                        try:
                            meta['anio'] = str(int(float(str(vals[j+2]))))
                        except Exception:
                            pass
                    if sv == 'Nº Factura:' and j + 3 < len(vals):
                        nf = str(vals[j+3]).strip()
                        if nf not in ['nan', 'NaT', '']:
                            meta['factura'] = nf
                    if sv == 'Nombre:' and j + 6 < len(vals):
                        nb = str(vals[j+6]).strip()
                        if nb not in ['nan', 'NaT', '']:
                            meta['nombre'] = nb
                    if sv == 'Empresa:' and j + 6 < len(vals):
                        em = str(vals[j+6]).strip()
                        if em not in ['nan', 'NaT', '']:
                            meta['empresa'] = em
            return meta

        def leer_excel_safe(f, header=0, sheet_name=0):
            """
            Lee un xlsx usando solo librerias estandar (zipfile + xml.etree).
            No necesita openpyxl, xlrd ni ningun paquete externo.
            """
            import zipfile, io, re
            from xml.etree import ElementTree as ET

            raw = f.read() if hasattr(f, 'read') else f
            buf = io.BytesIO(raw)
            zf = zipfile.ZipFile(buf)

            # Shared strings
            shared_strings = []
            if 'xl/sharedStrings.xml' in zf.namelist():
                tree = ET.parse(zf.open('xl/sharedStrings.xml'))
                ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in tree.findall('.//s:si', ns):
                    parts = si.findall('.//s:t', ns)
                    shared_strings.append(''.join(p.text or '' for p in parts))

            # Encontrar hoja
            wb_tree = ET.parse(zf.open('xl/workbook.xml'))
            wb_ns = {'w': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            sheets = wb_tree.findall('.//w:sheet', wb_ns)
            sheet_el = sheets[sheet_name] if isinstance(sheet_name, int) else next(
                (s for s in sheets if s.get('name') == sheet_name), sheets[0])

            rels_tree = ET.parse(zf.open('xl/_rels/workbook.xml.rels'))
            rels_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            ns_rid = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            r_id = sheet_el.get(f'{{{ns_rid}}}id') or sheet_el.get('r:id')
            sheet_file = 'xl/worksheets/sheet1.xml'
            for rel in rels_tree.findall('r:Relationship', rels_ns):
                if rel.get('Id') == r_id:
                    t = rel.get('Target', '').lstrip('/')
                    sheet_file = t if t.startswith('xl/') else 'xl/' + t
                    break

            # Parsear celdas
            ws_tree = ET.parse(zf.open(sheet_file))
            ws_ns = {'w': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

            def col2idx(s):
                v = 0
                for ch in s:
                    v = v * 26 + (ord(ch) - 64)
                return v - 1

            rows_data, max_col = {}, 0
            for row_el in ws_tree.findall('.//w:row', ws_ns):
                r_num = int(row_el.get('r', 0))
                for c_el in row_el.findall('w:c', ws_ns):
                    ref = c_el.get('r', '')
                    m = re.match(r'([A-Z]+)', ref)
                    if not m:
                        continue
                    col_idx = col2idx(m.group(1))
                    max_col = max(max_col, col_idx)
                    t_attr = c_el.get('t', '')
                    v_el = c_el.find('w:v', ws_ns)
                    val = None
                    # Inline strings usan <is><t> en vez de <v>
                    is_el = c_el.find('w:is', ws_ns)
                    if is_el is not None:
                        t_parts = is_el.findall('.//w:t', ws_ns)
                        val = ''.join(p.text or '' for p in t_parts)
                    elif v_el is not None and v_el.text is not None:
                        if t_attr == 's':
                            i_s = int(v_el.text)
                            val = shared_strings[i_s] if i_s < len(shared_strings) else ''
                        elif t_attr in ('str', 'b', 'e'):
                            val = v_el.text
                        else:
                            try:
                                fv = float(v_el.text)
                                val = int(fv) if fv == int(fv) else fv
                            except (ValueError, OverflowError):
                                val = v_el.text
                    rows_data.setdefault(r_num, {})[col_idx] = val

            if not rows_data:
                return pd.DataFrame()

            n_cols = max_col + 1
            records = [[rows_data[r].get(c) for c in range(n_cols)]
                       for r in sorted(rows_data.keys())]
            df = pd.DataFrame(records)

            if header is None:
                return df

            if isinstance(header, int) and header < len(df):
                col_names = [str(v) if v is not None else f'col_{i}'
                             for i, v in enumerate(df.iloc[header].tolist())]
                df.columns = col_names
                df = df.iloc[header + 1:].reset_index(drop=True)
            return df


        def leer_liquidacion(uploaded_file):
            """Lee y limpia una liquidación de compañía (formato Naturgy y similares)."""
            df_raw = leer_excel_safe(uploaded_file, header=None)
            meta = extraer_meta_liquidacion(df_raw)

            # Detectar fila de cabecera buscando 'CIF/NIF' o 'CUPSElectricidad'
            header_row = None
            for i in range(0, 20):
                vals = [str(v) for v in df_raw.iloc[i].tolist()]
                if any('CIF' in v or 'CUPS' in v.upper() or 'CONTRATO' in v.upper() for v in vals):
                    header_row = i
                    break

            if header_row is None:
                return None, meta, "No se encontró la cabecera de datos en el archivo."

            rows = []
            for i in range(header_row + 1, len(df_raw)):
                row = df_raw.iloc[i]
                cif = row.iloc[5]
                if pd.isna(cif) or str(cif).strip() in ['nan', '', 'CIF/NIF']:
                    continue
                # Detectar Gas vs Luz por columna
                cups_gas_raw = row.iloc[15]
                cups_luz_raw = row.iloc[18]
                producto = str(row.iloc[19]).strip() if pd.notna(row.iloc[19]) else ''
                fecha_baja = row.iloc[14]
                comision = row.iloc[27]
                contrato_darwin = row.iloc[26]

                rows.append({
                    'CIF': str(cif).strip(),
                    'Fecha Alta': row.iloc[11],
                    'Fecha Baja': fecha_baja if fecha_baja is not None else None,
                    'CUPS Gas Raw': str(cups_gas_raw).strip() if pd.notna(cups_gas_raw) else None,
                    'CUPS Luz Raw': str(cups_luz_raw).strip() if pd.notna(cups_luz_raw) else None,
                    'CUPS Gas Norm': normalize_cup(cups_gas_raw),
                    'CUPS Luz Norm': normalize_cup(cups_luz_raw),
                    'Producto': producto,
                    'Tipo': 'GAS' if pd.notna(cups_gas_raw) and str(cups_gas_raw).strip() not in ['nan', ''] else 'LUZ',
                    'Contrato Darwin': str(contrato_darwin).strip() if pd.notna(contrato_darwin) else '',
                    'Comisión_liq': comision if comision is not None else 0,
                    'Descomisionado': pd.notna(fecha_baja),
                })
            df = pd.DataFrame(rows)
            return df, meta, None

        def cruzar_con_contratos(df_liq, df_contratos):
            """Cruza la liquidación con el Excel de contratos por CUP normalizado."""
            # Normalizar CUPs en contratos
            df_contratos = df_contratos.copy()
            df_contratos['CUPS Luz Norm'] = df_contratos['CUPS Luz'].apply(normalize_cup)
            df_contratos['CUPS Gas Norm'] = df_contratos['CUPS Gas'].apply(normalize_cup)

            # Separar registros de luz y gas en la liquidación
            df_luz = df_liq[df_liq['CUPS Luz Norm'].notna()].copy()
            df_gas = df_liq[df_liq['CUPS Gas Norm'].notna()].copy()

            cols_crm = ['ID', 'ID Contrato Externo', 'Cliente', 'Comercial', 'Estado',
                        'Comercializadora', 'Tarifa', 'DNI Cliente', 'CUPS Luz Norm', 'Comisión']

            # Merge LUZ
            if not df_luz.empty:
                crm_luz = df_contratos[df_contratos['CUPS Luz Norm'].notna()][
                    [c for c in cols_crm if c != 'CUPS Gas Norm']
                ].drop_duplicates('CUPS Luz Norm')
                df_luz = pd.merge(df_luz, crm_luz, on='CUPS Luz Norm', how='left', suffixes=('_liq', '_crm'))
                df_luz['CUP Cruce'] = df_luz['CUPS Luz Norm']
            else:
                df_luz['ID'] = None

            # Merge GAS
            cols_crm_gas = ['ID', 'ID Contrato Externo', 'Cliente', 'Comercial', 'Estado',
                            'Comercializadora', 'Tarifa', 'DNI Cliente', 'CUPS Gas Norm', 'Comisión']
            if not df_gas.empty:
                crm_gas = df_contratos[df_contratos['CUPS Gas Norm'].notna()][
                    [c for c in cols_crm_gas]
                ].drop_duplicates('CUPS Gas Norm')
                df_gas = pd.merge(df_gas, crm_gas, on='CUPS Gas Norm', how='left', suffixes=('_liq', '_crm'))
                df_gas['CUP Cruce'] = df_gas['CUPS Gas Norm']
            else:
                df_gas['ID'] = None

            # Unir
            df_resultado = pd.concat([df_luz, df_gas], ignore_index=True)

            # Clasificar cada registro
            def clasificar(row):
                try:
                    com_liq = float(row.get('Comisión_liq', 0) or 0)
                except (TypeError, ValueError):
                    com_liq = 0
                # Descomisionado: tiene fecha de baja O comisión negativa
                if row.get('Descomisionado') or com_liq < 0:
                    return '🔴 DESCOMISIONADO'
                # Sin match: no está en CRM (ID nulo o vacío)
                id_val = row.get('ID')
                sin_match = (id_val is None or
                             (hasattr(id_val, '__class__') and
                              id_val.__class__.__name__ == 'float' and
                              id_val != id_val) or  # NaN check
                             str(id_val).strip() in ['', 'nan', 'None'])
                if sin_match:
                    return '⚠️ SIN MATCH EN CRM'
                # Tiene match en CRM y comisión > 0: PAGADO
                if com_liq > 0:
                    return '✅ PAGADO'
                # Tiene match pero comisión 0: pendiente de revisar
                return '❓ PENDIENTE REVISAR'

            df_resultado['Estado Liquidación'] = df_resultado.apply(clasificar, axis=1)
            return df_resultado

        # ══════════════════════════════════════════════════════
        # ── INTERFAZ ──
        # ══════════════════════════════════════════════════════

        st.markdown("""
            <div style="background:#161b22; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                <p style="color:#FFD700; font-weight:bold; margin:0 0 6px 0;">⚙️ CRUCE AUTOMÁTICO DE LIQUIDACIONES</p>
                <p style="color:#8b949e; margin:0; font-size:0.85rem;">
                    Sube la liquidación de la compañía (ej: <b>liqui_naturgy_abril.xlsx</b>) y el Excel de contratos.
                    El sistema cruza por CUP (20 ó 22 dígitos), detecta lo pagado, lo descomisionado (gas y luz)
                    y lo pendiente de reclamar.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_up1, col_up2 = st.columns(2)
        with col_up1:
            st.markdown('<p style="color:#d2ff00; font-weight:bold; font-size:1rem; margin-bottom:4px;">📄 Liquidación compañía</p>', unsafe_allow_html=True)
            f_liquidacion = st.file_uploader(
                "Sube la liquidación (.xlsx)",
                type=['xlsx'],
                key="liq_upload",
                label_visibility="collapsed"
            )
        with col_up2:
            st.markdown('<p style="color:#d2ff00; font-weight:bold; font-size:1rem; margin-bottom:4px;">📋 Contratos Energía (CRM)</p>', unsafe_allow_html=True)
            f_contratos = st.file_uploader(
                "Sube contratos_energia.xlsx",
                type=['xlsx'],
                key="con_upload",
                label_visibility="collapsed"
            )

        if f_liquidacion and f_contratos:
            with st.spinner("⏳ Procesando cruce de liquidación..."):
                try:
                    # Leer archivos
                    df_liq_raw, meta, err = leer_liquidacion(f_liquidacion)
                    if err:
                        st.error(f"❌ Error leyendo liquidación: {err}")
                        st.stop()

                    df_con_raw = leer_excel_safe(f_contratos)
                    df_con_raw.columns = df_con_raw.columns.str.strip()

                    # Detectar nombre compañía del archivo
                    nombre_archivo = f_liquidacion.name.lower()
                    companias_conocidas = ['naturgy', 'endesa', 'gana', 'iberdrola', 'total', 'repsol']
                    compania_detectada = next((c.upper() for c in companias_conocidas if c in nombre_archivo), 'COMPAÑÍA')

                    # Filtrar contratos solo de esa compañía si aplica
                    if 'Comercializadora' in df_con_raw.columns and compania_detectada != 'COMPAÑÍA':
                        df_con_filtrado = df_con_raw[
                            df_con_raw['Comercializadora'].str.contains(compania_detectada, case=False, na=False)
                        ].copy()
                        n_total = len(df_con_raw)
                        n_filtrado = len(df_con_filtrado)
                    else:
                        df_con_filtrado = df_con_raw.copy()
                        n_total = n_filtrado = len(df_con_raw)

                    # Cruce
                    df_resultado = cruzar_con_contratos(df_liq_raw, df_con_filtrado)


                    # ── SVA: extraer de la misma liquidación (filas con producto SVA) ──
                    # Productos de energía pura vs SVA
                    PRODUCTOS_ENERGIA = {'TARIFA POR USO LUZ', 'PLAN FIJO LUZ 24H',
                                         'TARIFA POR USO GAS', 'TARIFA PLANA GAS'}
                    def es_sva(producto):
                        return (producto is not None and
                                str(producto).strip() != '' and
                                str(producto).strip().upper() not in PRODUCTOS_ENERGIA)

                    df_sva_resultado = pd.DataFrame()
                    sva_pagados_n, sva_descom_n, sva_sinmatch_n = 0, 0, 0
                    sva_total_pagado, sva_total_descom = 0.0, 0.0


                    # ── HEADER RESUMEN ──
                    meses_es = {'1':'Enero','2':'Febrero','3':'Marzo','4':'Abril','5':'Mayo','6':'Junio',
                                '7':'Julio','8':'Agosto','9':'Septiembre','10':'Octubre','11':'Noviembre','12':'Diciembre'}
                    mes_nombre = meses_es.get(meta.get('mes',''), meta.get('mes',''))
                    st.markdown(f"""
                        <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460); border:2px solid #FFD700;
                                    border-radius:12px; padding:18px 24px; margin:10px 0 20px 0;">
                            <h3 style="color:#FFD700; margin:0 0 4px 0;">⚡ {compania_detectada} · {mes_nombre} {meta.get('anio','')}</h3>
                            <p style="color:#8b949e; margin:0; font-size:0.82rem;">
                                Factura: <b style="color:white;">{meta.get('factura','-')}</b> &nbsp;·&nbsp;
                                Empresa: <b style="color:white;">{meta.get('nombre','-')}</b> &nbsp;·&nbsp;
                                Registros liquidación: <b style="color:white;">{len(df_liq_raw)}</b> &nbsp;·&nbsp;
                                Contratos {compania_detectada} en CRM: <b style="color:white;">{n_filtrado}</b>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                    # ── KPIs ──
                    pagados = df_resultado[df_resultado['Estado Liquidación'] == '✅ PAGADO']
                    descomisionados = df_resultado[df_resultado['Estado Liquidación'] == '🔴 DESCOMISIONADO']
                    sin_match = df_resultado[df_resultado['Estado Liquidación'] == '⚠️ SIN MATCH EN CRM']
                    pendientes = df_resultado[df_resultado['Estado Liquidación'] == '❓ PENDIENTE REVISAR']

                    pagados_luz = pagados[pagados['Tipo'] == 'LUZ']
                    pagados_gas = pagados[pagados['Tipo'] == 'GAS']
                    descom_luz = descomisionados[descomisionados['Tipo'] == 'LUZ']
                    descom_gas = descomisionados[descomisionados['Tipo'] == 'GAS']

                    total_cobrado = float(pagados['Comisión_liq'].sum()) if 'Comisión_liq' in pagados.columns else 0
                    total_descom = abs(float(descomisionados['Comisión_liq'].sum())) if 'Comisión_liq' in descomisionados.columns else 0
                    total_a_reclamar = float(sin_match['Comisión_liq'].sum()) + float(pendientes['Comisión_liq'].sum()) if 'Comisión_liq' in df_resultado.columns else 0

                    k1, k2, k3, k4, k5 = st.columns(5)
                    box_k = "border-radius:10px; padding:14px 8px; text-align:center; margin-bottom:10px;"
                    k1.markdown(f'<div style="background:#0d2818; border:2px solid #7ee787; {box_k}"><p style="color:#7ee787; font-size:0.72rem; font-weight:bold; margin:0;">✅ PAGADOS</p><h2 style="color:white; margin:4px 0;">{len(pagados)}</h2><p style="color:#7ee787; font-size:0.75rem; margin:0;">💡{len(pagados_luz)} 🔥{len(pagados_gas)}</p><p style="color:#7ee787; font-size:0.8rem; margin:4px 0 0 0;font-weight:bold;">{total_cobrado:,.0f}€</p></div>', unsafe_allow_html=True)
                    k2.markdown(f'<div style="background:#1a0a0a; border:2px solid #ff4b4b; {box_k}"><p style="color:#ff4b4b; font-size:0.72rem; font-weight:bold; margin:0;">🔴 DESCOMISIONADOS</p><h2 style="color:white; margin:4px 0;">{len(descomisionados)}</h2><p style="color:#ff4b4b; font-size:0.75rem; margin:0;">💡{len(descom_luz)} 🔥{len(descom_gas)}</p><p style="color:#ff4b4b; font-size:0.8rem; margin:4px 0 0 0;font-weight:bold;">-{total_descom:,.0f}€</p></div>', unsafe_allow_html=True)
                    k3.markdown(f'<div style="background:#1a1000; border:2px solid #ffaa00; {box_k}"><p style="color:#ffaa00; font-size:0.72rem; font-weight:bold; margin:0;">⚠️ SIN MATCH CRM</p><h2 style="color:white; margin:4px 0;">{len(sin_match)}</h2><p style="color:#ffaa00; font-size:0.75rem; margin:0;">Verificar manualmente</p></div>', unsafe_allow_html=True)
                    k4.markdown(f'<div style="background:#161b22; border:2px solid #8b949e; {box_k}"><p style="color:#8b949e; font-size:0.72rem; font-weight:bold; margin:0;">❓ PENDIENTE REVISAR</p><h2 style="color:white; margin:4px 0;">{len(pendientes)}</h2><p style="color:#8b949e; font-size:0.75rem; margin:0;"> </p></div>', unsafe_allow_html=True)
                    k5.markdown(f'<div style="background:linear-gradient(135deg,#1e3a1e,#0a280a); border:2px solid #d2ff00; {box_k}"><p style="color:#d2ff00; font-size:0.72rem; font-weight:bold; margin:0;">💰 A RECLAMAR</p><h2 style="color:#d2ff00; margin:4px 0;">{len(sin_match)+len(pendientes)}</h2><p style="color:#d2ff00; font-size:0.8rem; margin:0;font-weight:bold;">{total_a_reclamar:,.0f}€</p></div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # ── SVA: extraer filas SVA del df_resultado (ya cruzadas con CRM) ──
                    df_sva_resultado = df_resultado[df_resultado['Producto'].apply(es_sva)].copy()
                    df_energia_resultado = df_resultado[~df_resultado['Producto'].apply(es_sva)].copy()

                    # Recalcular subsets usando solo energía (sin SVA)
                    pagados       = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='✅ PAGADO']
                    descomisionados = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO']
                    sin_match     = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='⚠️ SIN MATCH EN CRM']
                    pendientes    = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='❓ PENDIENTE REVISAR']

                    pagados_luz   = pagados[pagados['Tipo'] == 'LUZ']
                    pagados_gas   = pagados[pagados['Tipo'] == 'GAS']
                    descom_luz    = descomisionados[descomisionados['Tipo'] == 'LUZ']
                    descom_gas    = descomisionados[descomisionados['Tipo'] == 'GAS']

                    total_cobrado     = float(pagados['Comisión_liq'].sum()) if 'Comisión_liq' in pagados.columns else 0
                    total_descom      = abs(float(descomisionados['Comisión_liq'].sum())) if 'Comisión_liq' in descomisionados.columns else 0
                    total_a_reclamar  = float(sin_match['Comisión_liq'].sum()) + float(pendientes['Comisión_liq'].sum()) if 'Comisión_liq' in df_resultado.columns else 0

                    # SVA stats
                    sva_pagados_n     = len(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO'])
                    sva_descom_n      = len(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO'])
                    sva_sinmatch_n    = len(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='⚠️ SIN MATCH EN CRM'])
                    sva_total_pagado  = float(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO']['Comisión_liq'].sum()) if not df_sva_resultado.empty else 0.0
                    sva_total_descom  = float(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO']['Comisión_liq'].sum()) if not df_sva_resultado.empty else 0.0

                    st.markdown("<br>", unsafe_allow_html=True)

                    # ── KPI SVA (si hay SVA en la liquidación) ──
                    if not df_sva_resultado.empty:
                        st.markdown('<p style="color:#a78bfa; font-weight:bold; font-size:0.85rem; margin:0 0 6px 0;">⚡ SVA</p>', unsafe_allow_html=True)
                        ks1, ks2, ks3, ks4 = st.columns(4)
                        box_ks = "border-radius:8px; padding:10px 8px; text-align:center; margin-bottom:12px;"
                        ks1.markdown(f'<div style="background:#0d1f2d; border:2px solid #a78bfa; {box_ks}"><p style="color:#a78bfa; font-size:0.7rem; font-weight:bold; margin:0;">⚡ SVA PAGADOS</p><h3 style="color:white; margin:4px 0;">{sva_pagados_n}</h3><p style="color:#a78bfa; font-size:0.8rem; margin:0;font-weight:bold;">{sva_total_pagado:,.0f}€</p></div>', unsafe_allow_html=True)
                        ks2.markdown(f'<div style="background:#1a0a0a; border:2px solid #ff4b4b; {box_ks}"><p style="color:#ff4b4b; font-size:0.7rem; font-weight:bold; margin:0;">🔴 SVA DESCOM</p><h3 style="color:white; margin:4px 0;">{sva_descom_n}</h3><p style="color:#ff4b4b; font-size:0.8rem; margin:0;font-weight:bold;">{sva_total_descom:,.0f}€</p></div>', unsafe_allow_html=True)
                        ks3.markdown(f'<div style="background:#1a1000; border:2px solid #ffaa00; {box_ks}"><p style="color:#ffaa00; font-size:0.7rem; font-weight:bold; margin:0;">⚠️ SVA SIN MATCH</p><h3 style="color:white; margin:4px 0;">{sva_sinmatch_n}</h3></div>', unsafe_allow_html=True)
                        ks4.markdown(f'<div style="background:#0d1f2d; border:2px solid #d2ff00; {box_ks}"><p style="color:#d2ff00; font-size:0.7rem; font-weight:bold; margin:0;">📋 SVA TOTAL</p><h3 style="color:white; margin:4px 0;">{len(df_sva_resultado)}</h3></div>', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                    # ── TABS DE DETALLE ──
                    _tab_labels = [
                        f"✅ PAGADOS ({len(pagados)})",
                        f"🔴 DESCOMISIONADOS ({len(descomisionados)})",
                        f"💰 A RECLAMAR ({len(sin_match)+len(pendientes)})",
                        f"⚠️ SIN MATCH ({len(sin_match)})",
                        f"📋 COMPLETO ({len(df_energia_resultado)})",
                    ]
                    if not df_sva_resultado.empty:
                        _tab_labels.append(f"⚡ SVA ({len(df_sva_resultado)})")

                    _tabs = st.tabs(_tab_labels)
                    t_pagado   = _tabs[0]
                    t_descom   = _tabs[1]
                    t_reclamar = _tabs[2]
                    t_sinmatch = _tabs[3]
                    t_todo     = _tabs[4]
                    t_sva      = _tabs[5] if not df_sva_resultado.empty else None


                    # Columnas a mostrar
                    cols_display = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                    'Producto', 'Comisión_liq', 'Fecha Alta', 'Fecha Baja']
                    cols_display = [c for c in cols_display if c in df_energia_resultado.columns]

                    def df_to_show(df_sub):
                        """Prepara dataframe para mostrar."""
                        df_s = df_sub[cols_display].copy()
                        if 'Fecha Alta' in df_s.columns:
                            df_s['Fecha Alta'] = pd.to_datetime(df_s['Fecha Alta'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                        if 'Fecha Baja' in df_s.columns:
                            df_s['Fecha Baja'] = pd.to_datetime(df_s['Fecha Baja'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                        if 'Comisión_liq' in df_s.columns:
                            df_s = df_s.rename(columns={'Comisión_liq': 'Comisión €'})
                        return df_s.reset_index(drop=True)

                    with t_pagado:
                        st.markdown(f'<p style="color:#7ee787;">Total cobrado: <b>{total_cobrado:,.0f} €</b> — Luz: {len(pagados_luz)} suministros | Gas: {len(pagados_gas)} suministros</p>', unsafe_allow_html=True)
                        if not pagados.empty:
                            st.dataframe(df_to_show(pagados), use_container_width=True, height=400)
                        else:
                            st.info("No hay registros pagados.")

                    with t_descom:
                        st.markdown(f'<p style="color:#ff4b4b;">Total descomisionado: <b>-{total_descom:,.0f} €</b> — Luz: {len(descom_luz)} | Gas: {len(descom_gas)}</p>', unsafe_allow_html=True)
                        if not descomisionados.empty:
                            st.dataframe(df_to_show(descomisionados), use_container_width=True, height=400)
                        else:
                            st.success("✅ Sin descomisiones en esta liquidación.")

                    with t_reclamar:
                        df_reclamar = pd.concat([sin_match, pendientes], ignore_index=True)
                        st.markdown(f'<p style="color:#d2ff00;">Importe total a reclamar: <b>{total_a_reclamar:,.0f} €</b></p>', unsafe_allow_html=True)
                        if not df_reclamar.empty:
                            st.dataframe(df_to_show(df_reclamar), use_container_width=True, height=400)
                        else:
                            st.success("✅ Todo está abonado o identificado.")

                    with t_sinmatch:
                        st.markdown('<p style="color:#ffaa00;">Estos CUPs de la liquidación no se encuentran en el Excel de contratos. Verificar si pertenecen a otra compañía o si faltan en el CRM.</p>', unsafe_allow_html=True)
                        if not sin_match.empty:
                            cols_sm = ['Tipo', 'CIF', 'CUP Cruce', 'Producto', 'Comisión_liq']
                            cols_sm = [c for c in cols_sm if c in sin_match.columns]
                            st.dataframe(sin_match[cols_sm].reset_index(drop=True), use_container_width=True)
                        else:
                            st.success("✅ Todos los CUPs están en el CRM.")

                    with t_todo:
                        cols_todo = cols_display + ['Estado Liquidación']
                        cols_todo = [c for c in cols_todo if c in df_resultado.columns]
                        df_todo_show = df_energia_resultado[cols_todo].copy()
                        if 'Fecha Alta' in df_todo_show.columns:
                            df_todo_show['Fecha Alta'] = pd.to_datetime(df_todo_show['Fecha Alta'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                        if 'Fecha Baja' in df_todo_show.columns:
                            df_todo_show['Fecha Baja'] = pd.to_datetime(df_todo_show['Fecha Baja'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                        if 'Comisión_liq' in df_todo_show.columns:
                            df_todo_show = df_todo_show.rename(columns={'Comisión_liq': 'Comisión €'})
                        st.dataframe(df_todo_show.reset_index(drop=True), use_container_width=True, height=500)


                    if t_sva is not None and not df_sva_resultado.empty:
                        with t_sva:
                            st.markdown('<p style="color:#a78bfa;">SVA extraídos de la misma liquidación (filas con producto distinto a energía), cruzados con contratos por su CUPS.</p>', unsafe_allow_html=True)

                            cols_sva_show = ['CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                             'Producto', 'Comisión_liq', 'Estado Liquidación']
                            cols_sva_show = [c for c in cols_sva_show if c in df_sva_resultado.columns]

                            # ── Pagados SVA ──
                            sva_p = df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO']
                            sva_d = df_sva_resultado[df_sva_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO']
                            sva_r = df_sva_resultado[~df_sva_resultado['Estado Liquidación'].isin(['✅ PAGADO','🔴 DESCOMISIONADO'])]

                            st.markdown(f'**✅ SVA PAGADOS** — {len(sva_p)} registros · {sva_p["Comisión_liq"].sum():,.0f}€')
                            if not sva_p.empty:
                                df_sp = sva_p[cols_sva_show].copy()
                                df_sp = df_sp.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                st.dataframe(df_sp.reset_index(drop=True), use_container_width=True, height=250)

                            if not sva_d.empty:
                                st.markdown(f'**🔴 SVA DESCOMISIONADOS** — {len(sva_d)} registros · {sva_d["Comisión_liq"].sum():,.0f}€')
                                df_sd = sva_d[cols_sva_show].copy()
                                df_sd = df_sd.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                st.dataframe(df_sd.reset_index(drop=True), use_container_width=True, height=200)

                            if not sva_r.empty:
                                st.markdown(f'**⚠️ SVA A RECLAMAR / SIN MATCH** — {len(sva_r)} registros · {sva_r["Comisión_liq"].sum():,.0f}€')
                                df_sr = sva_r[cols_sva_show].copy()
                                df_sr = df_sr.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                st.dataframe(df_sr.reset_index(drop=True), use_container_width=True, height=200)
                            else:
                                st.success("✅ Todos los SVA están abonados.")


                    # ── DESCARGA RESULTADO ──
                    st.markdown("---")
                    import io, importlib, zipfile as _zf, struct as _struct

                    def prep_df_export(df_in):
                        """Convierte datetime/Timestamp a string para exportar."""
                        df_out = df_in.copy()
                        for col in df_out.columns:
                            try:
                                df_out[col] = df_out[col].apply(
                                    lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else x
                                )
                            except Exception:
                                pass
                        return df_out

                    def hacer_xlsx_nativo(sheets_dict):
                        """
                        Genera un xlsx real (formato Office Open XML) usando solo stdlib.
                        sheets_dict = {'NombreHoja': dataframe, ...}
                        Soporta strings, números y celdas vacías. Sin estilos avanzados.
                        """
                        import zipfile as zf2, io as io2
                        from xml.etree.ElementTree import Element, SubElement, tostring

                        def esc(s):
                            return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;')

                        shared = []
                        shared_map = {}
                        def get_si(val):
                            s = str(val)
                            if s not in shared_map:
                                shared_map[s] = len(shared)
                                shared.append(s)
                            return shared_map[s]

                        # Pre-scan all data to build shared strings
                        sheet_data = {}
                        for sname, df in sheets_dict.items():
                            df2p = prep_df_export(df).reset_index(drop=True)
                            rows = [list(df2p.columns)]
                            for _, row in df2p.iterrows():
                                rows.append(list(row))
                            for row in rows:
                                for cell in row:
                                    if cell is not None and str(cell) not in ['', 'nan', 'None']:
                                        try:
                                            float(str(cell).replace(',','.'))
                                        except (ValueError, TypeError):
                                            get_si(cell)
                            sheet_data[sname] = rows

                        buf = io2.BytesIO()
                        with zf2.ZipFile(buf, 'w', zf2.ZIP_DEFLATED) as z:
                            # [Content_Types].xml
                            ct_parts = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
'''
                            for i in range(len(sheet_data)):
                                ct_parts += f'  <Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
                            ct_parts += '</Types>'
                            z.writestr('[Content_Types].xml', ct_parts)

                            # _rels/.rels
                            z.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''')

                            # xl/_rels/workbook.xml.rels
                            wb_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId_ss" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
  <Relationship Id="rId_st" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
'''
                            for i, sname in enumerate(sheet_data):
                                wb_rels += f'  <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>\n'
                            wb_rels += '</Relationships>'
                            z.writestr('xl/_rels/workbook.xml.rels', wb_rels)

                            # xl/workbook.xml
                            wb_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
'''
                            for i, sname in enumerate(sheet_data):
                                wb_xml += f'    <sheet name="{esc(sname)}" sheetId="{i+1}" r:id="rId{i+1}"/>\n'
                            wb_xml += '  </sheets>\n</workbook>'
                            z.writestr('xl/workbook.xml', wb_xml)

                            # xl/styles.xml (mínimo)
                            z.writestr('xl/styles.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
</styleSheet>''')

                            # xl/sharedStrings.xml
                            ss_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="''' + str(len(shared)) + '''" uniqueCount="''' + str(len(shared)) + '''">
'''
                            for s in shared:
                                ss_xml += f'  <si><t xml:space="preserve">{esc(s)}</t></si>\n'
                            ss_xml += '</sst>'
                            z.writestr('xl/sharedStrings.xml', ss_xml)

                            # xl/worksheets/sheetN.xml
                            col_letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
                                           'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                                           'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL',
                                           'AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX']

                            for si_idx, (sname, rows) in enumerate(sheet_data.items()):
                                ws_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
'''
                                for r_idx, row in enumerate(rows):
                                    ws_xml += f'    <row r="{r_idx+1}">\n'
                                    for c_idx, cell in enumerate(row):
                                        col = col_letters[c_idx] if c_idx < len(col_letters) else f'A{c_idx}'
                                        ref = f'{col}{r_idx+1}'
                                        if cell is None or str(cell) in ['', 'nan', 'None']:
                                            ws_xml += f'      <c r="{ref}"/>\n'
                                        else:
                                            try:
                                                num = float(str(cell).replace(',','.'))
                                                ws_xml += f'      <c r="{ref}" t="n"><v>{num}</v></c>\n'
                                            except (ValueError, TypeError):
                                                si_n = shared_map.get(str(cell), 0)
                                                ws_xml += f'      <c r="{ref}" t="s"><v>{si_n}</v></c>\n'
                                    ws_xml += '    </row>\n'
                                ws_xml += '  </sheetData>\n</worksheet>'
                                z.writestr(f'xl/worksheets/sheet{si_idx+1}.xml', ws_xml)

                        buf.seek(0)
                        return buf.read()

                    # ── Preparar DataFrames para exportar con columnas limpias y totales ──
                    def df_pagados_export(df_p):
                        """Pagados: columnas clave + importe abonado."""
                        cols = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                'Producto', 'Fecha Alta', 'Fecha Baja']
                        cols = [c for c in cols if c in df_p.columns]
                        df_e = prep_df_export(df_p[cols].copy())
                        # Añadir importe abonado
                        if 'Comisión_liq' in df_p.columns:
                            df_e['IMPORTE ABONADO €'] = df_p['Comisión_liq'].values
                        # Fila de total
                        total = df_p['Comisión_liq'].sum() if 'Comisión_liq' in df_p.columns else 0
                        total_row = {c: '' for c in df_e.columns}
                        total_row[df_e.columns[-2] if len(df_e.columns) > 1 else df_e.columns[0]] = 'TOTAL'
                        total_row['IMPORTE ABONADO €'] = round(total, 2)
                        df_e = pd.concat([df_e, pd.DataFrame([total_row])], ignore_index=True)
                        return df_e

                    def df_descom_export(df_d):
                        """Descomisionados: columnas clave + importe descomisión."""
                        cols = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                'Producto', 'Fecha Alta', 'Fecha Baja']
                        cols = [c for c in cols if c in df_d.columns]
                        df_e = prep_df_export(df_d[cols].copy())
                        if 'Comisión_liq' in df_d.columns:
                            df_e['IMPORTE DESCOMISIÓN €'] = df_d['Comisión_liq'].values
                        total = df_d['Comisión_liq'].sum() if 'Comisión_liq' in df_d.columns else 0
                        total_row = {c: '' for c in df_e.columns}
                        total_row[df_e.columns[-2] if len(df_e.columns) > 1 else df_e.columns[0]] = 'TOTAL'
                        total_row['IMPORTE DESCOMISIÓN €'] = round(total, 2)
                        df_e = pd.concat([df_e, pd.DataFrame([total_row])], ignore_index=True)
                        return df_e

                    def df_reclamar_export(df_r):
                        cols = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                'Producto', 'Comisión_liq', 'Fecha Alta', 'Fecha Baja']
                        cols = [c for c in cols if c in df_r.columns]
                        df_e = prep_df_export(df_r[cols].copy())
                        if 'Comisión_liq' in df_e.columns:
                            df_e = df_e.rename(columns={'Comisión_liq': 'IMPORTE A RECLAMAR €'})
                        return df_e

                    nombre_base = f"cruce_{compania_detectada.lower()}_{meta.get('mes','')}_{meta.get('anio','')}"
                    df_a_reclamar = pd.concat([sin_match, pendientes]) if (not sin_match.empty or not pendientes.empty) else pd.DataFrame()

                    # Intentar engine xlsx instalado; si no, usar generador nativo
                    _writer_engine = None
                    for _eng in ['xlsxwriter', 'openpyxl']:
                        try:
                            importlib.import_module(_eng)
                            _writer_engine = _eng
                            break
                        except ImportError:
                            pass

                    def df_sva_export(df_s):
                        """SVA export: CUP, cliente CRM, producto, importe pagado/descom."""
                        cols_s = ['Tipo','CIF','Cliente','Comercial','Estado','CUP Cruce',
                                  'Producto','Comisión_liq','Estado Liquidación']
                        cols_s = [c for c in cols_s if c in df_s.columns]
                        df_e = prep_df_export(df_s[cols_s].copy())
                        if 'Comisión_liq' in df_e.columns:
                            df_e = df_e.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                        # Fila total
                        total_sva = df_s['Comisión_liq'].sum() if 'Comisión_liq' in df_s.columns else 0
                        if not df_e.empty:
                            total_row = {c: '' for c in df_e.columns}
                            total_row[df_e.columns[-2] if len(df_e.columns) > 1 else df_e.columns[0]] = 'TOTAL'
                            total_row['IMPORTE SVA €'] = round(total_sva, 2)
                            df_e = pd.concat([df_e, pd.DataFrame([total_row])], ignore_index=True)
                        return df_e

                    sheets_export = {
                        'Cruce Completo':   prep_df_export(df_resultado),
                        'Pagados':          df_pagados_export(pagados),
                        'Descomisionados':  df_descom_export(descomisionados),
                        'A Reclamar':       df_reclamar_export(df_a_reclamar),
                    }
                    if not df_sva_resultado.empty:
                        sheets_export['SVA Cruce'] = df_sva_export(df_sva_resultado)
                        sheets_export['SVA Pagados'] = df_sva_export(
                            df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO'])
                        sva_reclamar = df_sva_resultado[
                            ~df_sva_resultado['Estado Liquidación'].isin(['✅ PAGADO','🔴 DESCOMISIONADO'])]
                        if not sva_reclamar.empty:
                            sheets_export['SVA A Reclamar'] = df_sva_export(sva_reclamar)

                    if _writer_engine:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine=_writer_engine) as writer:
                            for sname, df_s in sheets_export.items():
                                df_s.to_excel(writer, sheet_name=sname, index=False)
                        output.seek(0)
                        xlsx_bytes = output.read()
                    else:
                        xlsx_bytes = hacer_xlsx_nativo(sheets_export)

                    st.download_button(
                        label=f"⬇️ DESCARGAR RESULTADO EXCEL — {nombre_base}.xlsx",
                        data=xlsx_bytes,
                        file_name=f"{nombre_base}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    import traceback
                    st.error(f"❌ Error en el cruce: {e}")
                    st.code(traceback.format_exc())

        else:
            st.markdown("""
                <div style="background:#0d1117; border:2px dashed #30363d; border-radius:12px; padding:40px; text-align:center; margin-top:20px;">
                    <p style="color:#8b949e; font-size:1rem; margin:0;">
                        👆 Sube la <b style="color:#d2ff00;">liquidación de la compañía</b> y el archivo de 
                        <b style="color:#d2ff00;">contratos_energia.xlsx</b> para iniciar el cruce automático
                    </p>
                </div>
            """, unsafe_allow_html=True)

        # ── ARCHIVOS EN DRIVE ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="block-header">📁 LIQUIDACIONES EN DRIVE</div>', unsafe_allow_html=True)
        col_liq1, col_liq2 = st.columns(2)
        with col_liq1:
            with st.expander("⚡ Liquidaciones Energía"):
                mostrar_carpeta_dir("directivos", "LIQUIDACIONES/ENERGIA", "⚡")
            with st.expander("📶 Liquidaciones Telco"):
                mostrar_carpeta_dir("directivos", "LIQUIDACIONES/TELCO", "📶")
        with col_liq2:
            with st.expander("🛡️ Liquidaciones Alarmas"):
                mostrar_carpeta_dir("directivos", "LIQUIDACIONES/ALARMAS", "🛡️")
            with st.expander("📋 Liquidaciones Generales"):
                mostrar_carpeta_dir("directivos", "LIQUIDACIONES/GENERAL", "📋")

    # ── TAB DOCS EMPRESA ──
    with tab_docs:
        st.markdown('<div class="block-header">📁 DOCUMENTACIÓN DE EMPRESA</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background:#161b22; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                <p style="color:#8b949e; margin:0; font-size:0.85rem;">Escrituras, certificados, seguros, licencias y documentación oficial. Los archivos se leen desde Google Drive · Carpeta <b style="color:#FFD700;">EMPRESA</b></p>
            </div>
        """, unsafe_allow_html=True)
        col_doc1, col_doc2 = st.columns(2)
        with col_doc1:
            with st.expander("🏛️ Documentación Legal"):
                mostrar_carpeta_dir("directivos", "EMPRESA/LEGAL", "⚖️")
            with st.expander("🔏 Certificados y Licencias"):
                mostrar_carpeta_dir("directivos", "EMPRESA/CERTIFICADOS", "🔏")
        with col_doc2:
            with st.expander("🛡️ Seguros"):
                mostrar_carpeta_dir("directivos", "EMPRESA/SEGUROS", "🛡️")
            with st.expander("📑 Otros Documentos"):
                mostrar_carpeta_dir("directivos", "EMPRESA/OTROS", "📑")

    # ── TAB SOPORTE ──
    with tab_sop:
        st.markdown('<div class="block-header">🛠️ SOPORTE Y HERRAMIENTAS</div>', unsafe_allow_html=True)

        def render_links_dir(lista, ncols=3):
            cols = st.columns(ncols)
            for i, p in enumerate(lista):
                with cols[i % ncols]:
                    st.markdown(
                        f'<div style="background:#161b22; padding:14px; border-radius:10px; '
                        f'border:1px solid #30363d; text-align:center; margin-bottom:10px;">'
                        f'<p style="color:#FFD700; font-size:1.1rem; margin:0;">{p.get("ico","🔗")}</p>'
                        f'<h4 style="color:white; margin:4px 0 0 0; font-size:0.9rem;">{p["n"]}</h4></div>',
                        unsafe_allow_html=True
                    )
                    st.link_button("ENTRAR", p["u"], use_container_width=True)

        st.markdown("##### 🖥️ Gestión y soporte")
        render_links_dir([
            {"n": "NODO",                    "u": "https://optimum.nodogestion.com/",                                                                                                             "ico": "🖥️"},
            {"n": "SUBIR DOCU TOTAL ENERGY", "u": "https://contrato.totalenergies.es/",                                                                                                          "ico": "📤"},
            {"n": "INFOJOBS",                "u": "https://www.infojobs.net/employer-login.xhtml",                                                                                               "ico": "💼"},
            {"n": "SAUC NATURGY",            "u": "https://sauc.gestdocout360.es/ServiceTonic/xhtml/portal/portal_home.jsf",                                                                    "ico": "🔧"},
            {"n": "LIQUIDACION TOTAL ENERGY","u": "https://ipbuestotalenergies-ipbuestotalenergiesprod.eu.cloud.varicent.com/payeewebv2/login?nextPathname=%2FPresenterAdaptive%2F67",           "ico": "💰"},
        ], ncols=3)

        st.markdown("---")
        st.markdown("##### 💡 Energía")
        render_links_dir([
            {"n": "CRM BASETTE",   "u": "https://crm.grupobasette.eu/login",                                                                                                                     "ico": "🏢"},
            {"n": "GANA ENERGÍA",  "u": "https://colaboradores.ganaenergia.com/",                                                                                                                "ico": "⚡"},
            {"n": "NATURGY",       "u": "https://checkout.naturgy.es/backoffice",                                                                                                                "ico": "🔥"},
            {"n": "TOTAL ENERGY",  "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F",                                    "ico": "🌍"},
            {"n": "IBERDROLA",     "u": "https://crm.gesventas.eu/login.php",                                                                                                                    "ico": "💛"},
            {"n": "NIBA",          "u": "https://clientes.niba.es/",                                                                                                                             "ico": "🔵"},
            {"n": "ENDESA",        "u": "https://inergia.app",                                                                                                                                   "ico": "🔴"},
            {"n": "REPSOL",        "u": "https://inergia.app/login.php",                                                                                                                         "ico": "🛢️"},
        ], ncols=4)

        st.markdown("---")
        st.markdown("##### 🚨 Alarmas")
        render_links_dir([
            {"n": "SEGURMA", "u": "https://crm.segurma.com/web#action=619&cids=1&menu_id=200&model=sale.order&view_type=list", "ico": "🛡️"},
            {"n": "3D",      "u": "https://www.3dseguridad.es/reportes/menu.php",                                              "ico": "🔒"},
        ], ncols=3)

        st.markdown("---")
        st.markdown("##### 📶 Telecomunicaciones")
        render_links_dir([
            {"n": "O2",   "u": "https://o2online.es/auth/login/?next=%2Fventas%2F&type=retail", "ico": "📱"},
            {"n": "LOWI", "u": "https://vodafone.topgestion.es/login",                          "ico": "📡"},
        ], ncols=3)

        st.markdown("---")
        st.markdown("##### 📞 B2COM · Centralita")
        render_links_dir([
            {"n": "B2COM AGENTE",     "u": "https://grupobasette.vozipcenter.com/l/0/#/",                                                  "ico": "🎧"},
            {"n": "B2COM SUPERVISOR", "u": "https://grupobasette-super.vozipcenter.com/supervisor.html#/agentes",                          "ico": "👁️"},
            {"n": "B2COM ADMIN",      "u": "https://grupobasette-admin.vozipcenter.com/(X(9edb6d37-9516-4e3d-a150-1182e9197070))/",       "ico": "⚙️"},
            {"n": "B2COM PANEL",      "u": "https://pac.b2com.com/login",                                                                  "ico": "📊"},
        ], ncols=4)

        st.markdown("---")
        st.markdown("##### 🌐 RRSS y BBDD")
        render_links_dir([
            {"n": "IONOS", "u": "https://login.ionos.es/oauth-mandatorlogin?language=es_ES&redirect_url=https%3A%2F%2Fauth.ionos.es%2F1.0%2Foauth%2Fauth%2Fotk&oauthclient=Control+Panel+Webhosting&oauthinternal=true", "ico": "🌐"},
        ], ncols=3)

# ══════════════════════════════════════════════════════
