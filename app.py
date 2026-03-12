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
        height: 100%;
    }
    .price-title { color: #d2ff00; font-size: 1.1rem; font-weight: bold; margin-bottom: 5px; }
    .price-val { color: white; font-size: 1.8rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.8rem; }
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR LUZ", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD ENERGIA", "📂 DOCUMENTACIÓN"], label_visibility="collapsed")

# --- CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    en = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, {"n": "NIBA", "u": "https://clientes.niba.es/"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols = st.columns(3)
    for i, p in enumerate(en):
        with cols[i % 3]:
            st.link_button(p["n"], p["u"], use_container_width=True)
    st.markdown('<div class="block-header">🛡️ 🚨 OTROS</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.link_button("SEGURMA", "https://partners.segurma.com/", use_container_width=True)
    with c2: st.link_button("O2 ONLINE", "https://o2online.es/auth/login/", use_container_width=True)

# --- PRECIOS (RESTAURADOS CUADROS EXACTOS) ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 FIBRA Y TV"])
    with t1: st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([
            {"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"},
            {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">⚡ SOLO FIBRA</div>', unsafe_allow_html=True)
        c_sf = st.columns(3)
        sf = [("FIBRA 300 Mb", "23€"), ("FIBRA 600 Mb", "27€"), ("FIBRA 1 Gb", "31€")]
        for i, (v, p) in enumerate(sf):
            with c_sf[i]: st.markdown(f'<div class="price-card"><div class="price-title">{v}</div><div class="price-val">{p}</div><div class="price-sub">Precio Final / Mes</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="block-header">🌐 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        c_fm = st.columns(4)
        fm = [("300 Mb + 1 LÍNEA", "30€", "40 GB"), ("600 Mb + 2 LÍNEAS", "35€", "10+40 GB"), ("600 Mb + 1 LÍNEA", "35€", "60 GB"), ("1 Gb + 1 LÍNEA", "38€", "120 GB")]
        for i, (v, p, d) in enumerate(fm):
            with c_fm[i]: st.markdown(f'<div class="price-card"><div class="price-title">{v}</div><div class="price-val">{p}</div><div class="price-sub">{d} de Datos</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="block-header">📺 TELEVISIÓN Y PACKS TV</div>', unsafe_allow_html=True)
        c_tv = st.columns(5)
        tv = [("SOLO TV", "9.99€", "M+ Suscripción"), ("600 Mb + TV", "38€", "35 GB"), ("600 Mb + TV", "45€", "60 GB"), ("1 Gb + TV", "50€", "350 GB"), ("1 Gb + TV", "56€", "375 GB")]
        for i, (v, p, d) in enumerate(tv):
            with c_tv[i]: st.markdown(f'<div class="price-card"><div class="price-title">{v}</div><div class="price-val">{p}</div><div class="price-sub">{d}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES</div>', unsafe_allow_html=True)
        c_ad = st.columns(3)
        ad = [("Móvil 40 GB", "5€"), ("Móvil 150 GB", "10€"), ("Móvil 300 GB", "15€")]
        for i, (v, p) in enumerate(ad):
            with c_ad[i]: st.markdown(f'<div class="price-card"><div class="price-title">{v}</div><div class="price-val">{p}</div><div class="price-sub">Pago Mensual</div></div>', unsafe_allow_html=True)

# --- COMPARADOR LUZ ---
elif menu == "⚖️ COMPARADOR LUZ":
    st.header("Estudio de Ahorro Personalizado")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre del cliente", "Nombre Apellidos")
        f_act = st.number_input("Factura actual con IVA (EUR)", value=0.0)
        consumo = st.number_input("Consumo del periodo (kWh)", value=0.0)
        dias = st.number_input("Días del periodo", value=30)
    with c2:
        comp_sel = st.selectbox("Compañía", sorted(list(set(t["COMPAÑÍA"] for t in tarifas_luz))))
        tar_sel = st.selectbox("Tarifa", [t["TARIFA"] for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel])
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tar_sel)
        st.markdown(f"**Potencia P1:** {sel['P1']} | **Potencia P2:** {sel['P2']}")
        potencia = st.number_input("Potencia contratada (kW)", value=4.6)

    p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    coste = ((potencia * sel["P1"] * dias) + (potencia * sel["P2"] * dias) + (consumo * p_calc)) * 1.21
    ahorro = f_act - coste
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("Promociones y Redes")
    st.markdown('<div class="block-header">🎁 PLAN AMIGO</div>', unsafe_allow_html=True)
    st.code("https://forms.gle/mU6XzRvywDoBQ5Q47")
    st.link_button("IR AL FORMULARIO", "https://forms.gle/mU6XzRvywDoBQ5Q47")
    
    st.markdown('<div class="block-header">📸 ANUNCIOS INSTAGRAM</div>', unsafe_allow_html=True)
    st.link_button("VER INSTAGRAM BASETTE", "https://www.instagram.com/basette.eu/", use_container_width=True)

# --- DASHBOARD (FIXED) ---
elif menu == "📈 DASHBOARD ENERGIA":
    st.header("Dashboard Energía | Basette Group")
    url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    try:
        df = pd.read_csv(url)
        # Fix de Fechas
        df['FECHA_DT'] = pd.to_datetime(df['FECHA DE CREACIÓN'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['FECHA_DT'])
        df['AÑO_INT'] = df['FECHA_DT'].dt.year.astype(int)
        meses_dict = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
        df['MES_NOMBRE'] = df['FECHA_DT'].dt.month.map(meses_dict)

        f1, f2 = st.columns(2)
        with f1: sel_mes = st.multiselect("Filtrar Meses", list(meses_dict.values()), default="Marzo")
        with f2: sel_año = st.selectbox("Año", sorted(df['AÑO_INT'].unique()))

        df_f = df[(df['MES_NOMBRE'].isin(sel_mes)) & (df['AÑO_INT'] == sel_año)]
        
        st.markdown('<div class="block-header">📊 RESUMEN DE CIFRAS</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        l = df_f['CUPS LUZ'].count() if 'CUPS LUZ' in df_f.columns else 0
        g = df_f['CUPS GAS'].count() if 'CUPS GAS' in df_f.columns else 0
        m1.metric("VENTAS LUZ", f"{l} ⚡")
        m2.metric("VENTAS GAS", f"{g} 🔥")
        m3.metric("TOTAL GLOBAL", f"{l+g} ✅")
        
        c_r1, c_r2 = st.columns(2)
        with c_r1: st.plotly_chart(px.bar(df_f.groupby('COMERCIAL').size().reset_index(name='V'), x='COMERCIAL', y='V', title="Ranking", color_discrete_sequence=['#d2ff00'], template="plotly_dark"), use_container_width=True)
        with c_r2: st.plotly_chart(px.pie(df_f.groupby('COMPAÑIA').size().reset_index(name='V'), values='V', names='COMPAÑIA', hole=.5, title="Porcentaje", color_discrete_sequence=['#d2ff00', '#7f8c8d']), use_container_width=True)
        st.dataframe(df_f, use_container_width=True)
    except Exception as e: st.error(f"Error: {e}")

# --- DOCUMENTACIÓN (RESTAURADA) ---
elif menu == "📂 DOCUMENTACIÓN":
    st.header("Documentación y Argumentarios")
    folders = ["📂 ARGUMENTARIOS DE VENTA", "📂 DOCUMENTACIÓN GANA ENERGÍA", "📂 DOCUMENTACIÓN NATURGY", "📂 DOCUMENTACIÓN TOTAL", "📂 DOCUMENTACIÓN ENDESA", "📂 DOCUMENTACIÓN O2"]
    for f in folders:
        with st.expander(f):
            st.write(f"Archivos disponibles para {f[2:]}...")
            # Aquí se añadirían st.download_button si los archivos existen en el servidor