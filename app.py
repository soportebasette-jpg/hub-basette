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

# 2. CSS DE ALTA VISIBILIDAD (MEJORADO)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* Resaltado de etiquetas de los filtros */
    label[data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        background-color: #d2ff00 !important;
        padding: 5px 15px !important;
        border-radius: 5px !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
    }
    
    /* Fondo para los contenedores de filtros (selectbox) para que no sean negros */
    div[data-testid="stSelectbox"] > div {
        background-color: #1c2128 !important; /* Gris muy oscuro */
        border: 1px solid #30363d !important;
        border-radius: 5px !important;
    }

    /* Estilo de métricas Premium */
    [data-testid="stMetricValue"] { 
        font-size: 3rem !important; 
        font-weight: 900 !important; 
        color: black !important;
    }
    [data-testid="stMetricLabel"] p { 
        color: #333333 !important; 
        font-size: 1.1rem !important; 
        font-weight: bold !important; 
        text-transform: uppercase;
        background-color: transparent !important; /* Quitar fondo verde flúor aquí */
        padding: 0 !important;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #d2ff00 0%, #afff00 100%);
        border-radius: 15px;
        padding: 20px;
        border: None;
        box-shadow: 0px 8px 20px rgba(210, 255, 0, 0.4);
        text-align: center;
    }

    /* Botones y otros */
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    
    /* Tablas blancas para legibilidad */
    .stDataFrame table { background-color: white !important; color: black !important; }
    .stDataFrame table th, .stDataFrame table td { color: black !important; }

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
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,163/0,096/0,072", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DASHBOARD", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- SECCIÓN CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
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
        st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">O2</h4></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://o2online.es/auth/login/", use_container_width=True)

# --- SECCIÓN PRECIOS ---
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

        st.markdown('<div class="block-header">🌐 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        fm_cols = st.columns(4)
        fibra_movil = [("300 Mb", "40 GB", "30€", "1 LÍNEA"), ("600 Mb", "10+40 GB", "35€", "2 LÍNEAS"), ("600 Mb", "60 GB", "35€", "1 LÍNEA"), ("1 Gb", "120 GB", "38€", "1 LÍNEA")]
        for i, (vel, gb, pre, lin) in enumerate(fibra_movil):
            with fm_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel} + {lin}</div><div class="price-val">{pre}</div><div class="price-sub">{gb} de Datos</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="block-header">📺 TELEVISIÓN Y PACKS TV</div>', unsafe_allow_html=True)
        tv_cols = st.columns(5)
        packs_tv = [
            ("SOLO TV", "", "9.99€", "M+ Suscripción"),
            ("600 Mb + TV", "35 GB", "38€", "M+ Incluido"),
            ("600 Mb + TV", "60 GB", "45€", "M+ / Netflix"),
            ("1 Gb + TV", "350 GB", "50€", "M+ Incluido"),
            ("1 Gb + TV", "375 GB", "56€", "M+ / Netflix")
        ]
        for i, (tit, gb, pre, extra) in enumerate(packs_tv):
            with tv_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{tit}</div><div class="price-val">{pre}</div><div class="price-sub">{gb if gb else extra}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES</div>', unsafe_allow_html=True)
        ad_cols = st.columns(3)
        ad_list = [("Móvil 40 GB", "5€"), ("Móvil 150 GB", "10€"), ("Móvil 300 GB", "15€")]
        for i, (lin, pre) in enumerate(ad_list):
            with ad_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{lin}</div><div class="price-val">{pre}</div><div class="price-sub">Pago Mensual</div></div>', unsafe_allow_html=True)

# --- SECCIÓN COMPARADOR ---
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
        # pdf.ln(30); pdf.set_font("Arial", "B", 18); pdf.cell(190, 10, "ESTUDIO COMPARATIVO DE AHORRO", ln=True, align="C")
        # st.download_button(label="📥 DESCARGAR ESTUDIO PDF", data=pdf.output(dest='S').encode('latin-1', 'replace'), file_name=f"Estudio_{cliente}.pdf")
        st.warning("Función de PDF en desarrollo")

# --- SECCIÓN DASHBOARD (MEJORADA) ---
elif menu == "📈 DASHBOARD":
    st.header("🏆 Dashboard Ejecutivo | Basette Group")
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        # ARREGLO DE FECHA:dayfirst=True para DD/MM/AAAA
        df_raw = pd.read_csv(sheet_url)
        df_raw['Fecha Creación'] = pd.to_datetime(df_raw['Fecha Creación'], dayfirst=True, errors='coerce')
        
        # Traducción de meses
        meses_traduccion = {
            "Enero": "January", "Febrero": "February", "Marzo": "March", "Abril": "April",
            "Mayo": "May", "Junio": "June", "Julio": "July", "Agosto": "August",
            "Septiembre": "September", "Octubre": "October", "Noviembre": "November", "Diciembre": "December"
        }
        
        df_raw['MES_NOMBRE'] = df_raw['Fecha Creación'].dt.month_name()
        df_raw['AÑO'] = df_raw['Fecha Creación'].dt.year
        df_raw['Venta_Luz'] = df_raw['CUPS Luz'].notna().astype(int)
        df_raw['Venta_Gas'] = df_raw['CUPS Gas'].notna().astype(int)
        df_raw['TOTAL_VENTAS'] = df_raw['Venta_Luz'] + df_raw['Venta_Gas']

        # FILTROS DIRECTOS (CON CSS APLICADO)
        f1, f2, f3, f4 = st.columns(4)
        with f1: sel_mes_esp = st.selectbox("Mes", ["Todos"] + list(meses_traduccion.keys()))
        with f2:
            años_disponibles = sorted(list(df_raw['AÑO'].dropna().unique().astype(int)), reverse=True)
            sel_año = st.selectbox("Año", ["Todos"] + [str(a) for a in años_disponibles])
        with f3:
            comercializadoras = ["Todas"] + sorted(list(df_raw['Comercializadora'].dropna().unique()))
            sel_comp = st.selectbox("Compañía", comercializadoras)
        with f4:
            comerciales = ["Todos"] + sorted(list(df_raw['Comercial'].dropna().unique()))
            sel_com = st.selectbox("Comercial", comerciales)

        df = df_raw.copy()
        if sel_mes_esp != "Todos": df = df[df['MES_NOMBRE'] == meses_traduccion[sel_mes_esp]]
        if sel_año != "Todos": df = df[df['AÑO'] == int(sel_año)]
        if sel_comp != "Todas": df = df[df['Comercializadora'] == sel_comp]
        if sel_com != "Todos": df = df[df['Comercial'] == sel_com]

        # --- MÉTRICAS RESALTADAS PREMIUN ---
        st.markdown('<div class="block-header">📊 RESUMEN DE CIFRAS</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        total_luz = df['Venta_Luz'].sum()
        total_gas = df['Venta_Gas'].sum()
        total_global = df['TOTAL_VENTAS'].sum()
        m1.metric("VENTAS LUZ", f"{total_luz} ⚡")
        m2.metric("VENTAS GAS", f"{total_gas} 🔥")
        m3.metric("TOTAL GLOBAL", f"{total_global} ✅")

        # --- GRÁFICOS PARALELOS ---
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown('<div class="block-header">👑 RANKING POR COMERCIAL</div>', unsafe_allow_html=True)
            if not df.empty:
                ranking = df.groupby('Comercial').agg(Luz=('Venta_Luz', 'sum'), Gas=('Venta_Gas', 'sum'), Total=('TOTAL_VENTAS', 'sum')).reset_index().sort_values(by='Total', ascending=False)
                fig_ranking = px.bar(ranking, x='Comercial', y=['Luz', 'Gas'], title=f"Ventas - {sel_mes_esp}", color_discrete_map={'Luz': '#d2ff00', 'Gas': '#ffffff'}, template="plotly_dark", barmode='stack')
                st.plotly_chart(fig_ranking, use_container_width=True)
            else: st.warning("No hay datos")

        with col_g2:
            st.markdown('<div class="block-header">🏢 VENTAS POR COMPAÑÍA (%)</div>', unsafe_allow_html=True)
            if not df.empty:
                df_comp = df.groupby('Comercializadora')['TOTAL_VENTAS'].sum().reset_index()
                df_comp = df_comp.sort_values(by='TOTAL_VENTAS', ascending=False)
                fig_pie = px.pie(df_comp, values='TOTAL_VENTAS', names='Comercializadora', 
                                 hole=0.4, title="Mix de Ventas por Compañía",
                                 color_discrete_sequence=['#d2ff00', '#ffffff', '#888888', '#333333'],
                                 template="plotly_dark")
                # Mostrar % y cantidad
                fig_pie.update_traces(textposition='inside', textinfo='percent+label+value', textfont_size=14)
                st.plotly_chart(fig_pie, use_container_width=True)
            else: st.warning("Sin datos")

        # --- TABLA ---
        st.markdown('<div class="block-header">📋 DETALLE DE OPERACIONES</div>', unsafe_allow_html=True)
        st.dataframe(df[['Fecha Creación', 'Estado', 'Comercial', 'Comercializadora', 'Cliente', 'CUPS Luz', 'CUPS Gas']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error: {e}")

# --- SECCIÓN REPOSITORIO (IGUAL) ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 ARGUMENTARIOS DE VENTA"):
        st.button("📘 ARGUMENTARIO ENERGÍA")
        st.button("📙 ARGUMENTARIO TELECO")