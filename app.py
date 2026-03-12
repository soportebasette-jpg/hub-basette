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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD ENERGIA", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    
    st.markdown('<div class="block-header">⭐ GESTIÓN PRINCIPAL</div>', unsafe_allow_html=True)
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid #d2ff00; text-align:center;"><h4 style="color:white; margin:0;">MARCADOR PRINCIPAL</h4></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    with c_p2:
        st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid #ffffff; text-align:center;"><h4 style="color:white; margin:0;">CRM BASETTE</h4></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR AL CRM", "https://crm.grupobasette.eu/login", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia_links = [
        ("GANA ENERGÍA", "https://colaboradores.ganaenergia.com/"),
        ("NATURGY", "https://checkout.naturgy.es/backoffice"),
        ("GAS TOTAL", "https://totalenergiesespana.my.site.com/"),
        ("LUZ TOTAL", "https://agentes.totalenergies.es/"),
        ("IBERDROLA", "https://crm.gesventas.eu/login.php"),
        ("NIBA", "https://clientes.niba.es/"),
        ("ENDESA", "https://inergia.app")
    ]
    cols_en = st.columns(3)
    for i, (nombre, url) in enumerate(energia_links):
        with cols_en[i % 3]:
            st.link_button(nombre, url, use_container_width=True)

    st.markdown("---")
    c_ext1, c_ext2 = st.columns(2)
    with c_ext1:
        st.markdown('<div class="block-header">🛡️ 🚨 ALARMAS</div>', unsafe_allow_html=True)
        st.link_button("SEGURMA", "https://partners.segurma.com/", use_container_width=True)
    with c_ext2:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        st.link_button("O2 ONLINE", "https://o2online.es/auth/login/", use_container_width=True)

# --- PRECIOS (SIN TOCAR) ---
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
        st.markdown('<div class="block-header">🚀 SOLO FIBRA</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        solo_fibra = [("FIBRA 300 Mb", "23€"), ("FIBRA 600 Mb", "27€"), ("FIBRA 1 Gb", "31€")]
        for i, (vel, pre) in enumerate(solo_fibra):
            with f_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel}</div><div class="price-val">{pre}</div><div class="price-sub">Precio Final / Mes</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="block-header">🌐 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        fm_cols = st.columns(4)
        fibra_movil = [("300 Mb + 1 LÍNEA", "40 GB", "30€"), ("600 Mb + 2 LÍNEAS", "10+40 GB", "35€"), ("600 Mb + 1 LÍNEA", "60 GB", "35€"), ("1 Gb + 1 LÍNEA", "120 GB", "38€")]
        for i, (vel, gb, pre) in enumerate(fibra_movil):
            with fm_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel}</div><div class="price-val">{pre}</div><div class="price-sub">{gb} de Datos</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="block-header">📺 TELEVISIÓN Y PACKS TV</div>', unsafe_allow_html=True)
        tv_cols = st.columns(5)
        packs_tv = [("SOLO TV", "M+ Suscripción", "9.99€"), ("600 Mb + TV", "35 GB", "38€"), ("600 Mb + TV", "60 GB", "45€"), ("1 Gb + TV", "350 GB", "50€"), ("1 Gb + TV", "375 GB", "56€")]
        for i, (title, sub, pre) in enumerate(packs_tv):
            with tv_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{title}</div><div class="price-val">{pre}</div><div class="price-sub">{sub}</div></div>', unsafe_allow_html=True)

# --- COMPARADOR (SIN TOCAR) ---
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
        tarifa_sel_nombre = st.selectbox("Tarifa Seleccionada", [t["TARIFA"] for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel])
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tarifa_sel_nombre)
        if os.path.exists(sel["logo"]): st.image(sel["logo"], width=120)
        consumo = st.number_input("Consumo del periodo (kWh)", value=0.0)

    try: p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    except: p_calc = 0.11

    coste_total_iva = ((potencia * sel["P1"] * dias_factura) + (potencia * sel["P2"] * dias_factura) + (consumo * p_calc)) * 1.21
    ahorro = f_act - coste_total_iva
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

# --- ANUNCIOS (SIN TOCAR) ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🎁 PLAN AMIGO</div>', unsafe_allow_html=True)
    if os.path.exists(QR_PLAN_AMIGO):
        st.image(QR_PLAN_AMIGO, width=250)
        with open(QR_PLAN_AMIGO, "rb") as f: st.download_button("Descargar QR", f, "qr-plan-amigo.png")
    st.link_button("VER ANUNCIOS INSTAGRAM", "https://www.instagram.com/basette.eu/", use_container_width=True)

# --- DASHBOARD ENERGIA (ARREGLADO) ---
elif menu == "📈 DASHBOARD ENERGIA":
    st.header("📈 Dashboard Energia | Basette Group")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        df_raw = pd.read_csv(sheet_url)
        # Limpiar filas completamente vacías para evitar errores de tipo en fechas
        df_raw = df_raw.dropna(how='all')
        
        if 'FECHA DE CREACIÓN' in df_raw.columns:
            df_raw['FECHA_DT'] = pd.to_datetime(df_raw['FECHA DE CREACIÓN'], dayfirst=True, errors='coerce')
            df_raw = df_raw.dropna(subset=['FECHA_DT'])
            df_raw['AÑO_INT'] = df_raw['FECHA_DT'].dt.year.astype(int)
            meses_dict = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
            df_raw['MES_NOMBRE'] = df_raw['FECHA_DT'].dt.month.map(meses_dict)
            
            f1, f2 = st.columns(2)
            with f1: sel_mes = st.multiselect("Filtrar Meses", list(meses_dict.values()), default=["Marzo"])
            with f2: sel_año = st.selectbox("Seleccionar Año", sorted(df_raw['AÑO_INT'].unique()))
            
            df = df_raw[(df_raw['MES_NOMBRE'].isin(sel_mes)) & (df_raw['AÑO_INT'] == sel_año)]
            
            m1, m2, m3 = st.columns(3)
            m1.metric("VENTAS LUZ", f"{df['CUPS LUZ'].count() if 'CUPS LUZ' in df.columns else 0} ⚡")
            m2.metric("VENTAS GAS", f"{df['CUPS GAS'].count() if 'CUPS GAS' in df.columns else 0} 🔥")
            m3.metric("TOTAL", len(df))
            
            st.plotly_chart(px.bar(df.groupby('COMERCIAL').size().reset_index(name='V'), x='COMERCIAL', y='V', color_discrete_sequence=['#d2ff00'], template="plotly_dark"), use_container_width=True)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# --- REPOSITORIO (ACTUALIZADO) ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación y Argumentarios")
    
    # Carpeta específica para Argumentarios
    with st.expander("📂 ARGUMENTARIOS DE VENTA"):
        archivos_arg = [
            "ARGUMENTARIO_ENERGÍA (Venta Fría) + Venta Cruzada Teleco.docx",
            "ARGUMENTARIO_TELECO (Clientes Movistar a O2) + Venta Cruzada Energía.docx",
            "FRASES PROHIBIDAS,PODER EN LA VENTA y REBATE OBJECIONES.docx"
        ]
        for arg in archivos_arg:
            path = f"manuales/{arg}"
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(f"📘 {arg}", f, file_name=arg, key=f"arg_{arg}")
            else:
                st.warning(f"Archivo no encontrado: {arg}")

    # Resto de carpetas de Compañías (sin logos)
    for c in ["GANA ENERGÍA", "NATURGY", "TOTAL", "ENDESA", "O2"]:
        with st.expander(f"📁 DOCUMENTACIÓN {c}"):
            if os.path.exists("manuales"):
                busq = c.split()[0].lower()
                # Filtramos para NO mostrar archivos .png ni los argumentarios ya listados arriba
                archivos = [f for f in os.listdir("manuales") if busq in f.lower() and not f.lower().endswith('.png') and "argumentario" not in f.lower()]
                for fn in archivos:
                    with open(f"manuales/{fn}", "rb") as f:
                        st.download_button(f"📥 {fn}", f, file_name=fn, key=f"f_{fn}")