import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS PERSONALIZADO (Estilo Basette)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p { color: #d2ff00 !important; font-weight: 900 !important; font-size: 1.25rem !important; }
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    .price-card { background-color: #161b22; border: 2px solid #30363d; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; transition: transform 0.3s; height: 100%; }
    .price-card:hover { border-color: #d2ff00; transform: translateY(-5px); }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.85rem; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,163/0,096/0,072", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"}
]

# 4. SISTEMA DE LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
        pwd = st.text_input("Clave de Acceso:", type="password")
        if st.button("ENTRAR AL HUB"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("❌ Contraseña Incorrecta")
    st.stop()

# 5. MENÚ LATERAL
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("MENÚ PRINCIPAL", ["🚀 CRM", "📈 DASHBOARD", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 TABLÓN", "📂 ARCHIVOS"], label_visibility="collapsed")

# --- SECCIÓN 1: CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button("ACCEDER AL MARCADOR VOZIP", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 ENERGÍA Y TELECO</div>', unsafe_allow_html=True)
    portales = [
        ("CRM BASETTE", "https://crm.grupobasette.eu/login"),
        ("GANA ENERGÍA", "https://colaboradores.ganaenergia.com/"),
        ("NATURGY", "https://checkout.naturgy.es/backoffice"),
        ("ENDESA", "https://inergia.app"),
        ("O2 ONLINE", "https://o2online.es/auth/login/")
    ]
    cols = st.columns(3)
    for i, (nombre, url) in enumerate(portales):
        with cols[i % 3]:
            st.link_button(nombre, url, use_container_width=True)

# --- SECCIÓN 2: DASHBOARD (Google Sheets) ---
elif menu == "📈 DASHBOARD":
    st.header("🏆 Rendimiento en Tiempo Real")
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=300)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            
            # Ranking del Mes
            st.markdown('<div class="block-header">🥇 RANKING DE COMERCIALES</div>', unsafe_allow_html=True)
            if 'Comercial' in df.columns:
                ranking = df.groupby('Comercial').size().reset_index(name='Ventas').sort_values('Ventas', ascending=False)
                st.table(ranking)

            # Cuota de Compañías
            st.markdown('<div class="block-header">📊 REPARTO POR COMPAÑÍA (%)</div>', unsafe_allow_html=True)
            if 'Compañia' in df.columns:
                pie_data = df['Compañia'].value_counts()
                st.bar_chart(pie_data)
        else:
            st.info("Aún no hay ventas registradas en Ventas_CRM.")
    except Exception as e:
        st.error("Error al conectar con Google Sheets. Revisa los Secrets.")

# --- SECCIÓN 3: PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifas Actualizadas")
    t1, t2 = st.tabs(["Luz", "Fibra/Móvil"])
    with t1:
        st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2:
        st.markdown('<div class="block-header">TARIFAS O2</div>', unsafe_allow_html=True)
        st.info("FIBRA 300Mb: 23€ | 600Mb: 27€ | 1Gb: 31€")

# --- SECCIÓN 4: COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Cliente", "Nombre")
        f_act = st.number_input("Factura Actual (€)", value=0.0)
    with c2:
        consumo = st.number_input("Consumo kWh", value=0.0)
        dias = st.number_input("Días Factura", value=30)
    
    # Cálculo rápido
    ahorro = f_act - ((consumo * 0.11) * 1.21)
    st.markdown(f'<div style="background:#d2ff00; color:black; padding:20px; border-radius:10px; text-align:center;"><h2>AHORRO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

# --- SECCIÓN 5: TABLÓN (Anuncios, Instagram, QR) ---
elif menu == "📢 TABLÓN":
    st.header("Comunicación Basette")
    col_ins, col_amigo = st.columns(2)
    with col_ins:
        st.markdown('<div class="block-header">📸 INSTAGRAM</div>', unsafe_allow_html=True)
        st.link_button("SÍGUENOS EN @BASETTE.EU", "https://www.instagram.com/basette.eu/", use_container_width=True)
    with col_amigo:
        st.markdown('<div class="block-header">🤝 PLAN AMIGO</div>', unsafe_allow_html=True)
        qr_path = "anunciosbasette/qr-plan amigo.png"
        if os.path.exists(qr_path):
            st.image(qr_path, width=200)
        else:
            st.warning("QR no encontrado en anunciosbasette/")

# --- SECCIÓN 6: ARCHIVOS ---
elif menu == "📂 ARCHIVOS":
    st.header("Descarga de Documentación")
    if os.path.exists("manuales"):
        for file in os.listdir("manuales"):
            if not file.endswith('.png'):
                with open(f"manuales/{file}", "rb") as f:
                    st.download_button(f"📥 {file}", f, file_name=file)