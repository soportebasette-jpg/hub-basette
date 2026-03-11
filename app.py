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

# 2. CSS DE ALTA VISIBILIDAD (Corregido para legibilidad total)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* Estilo para etiquetas de filtros */
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
    }
    
    /* Arreglo para que el texto de los selectores se vea siempre */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #161b22 !important;
        color: white !important;
        border: 1px solid #d2ff00 !important;
    }
    
    /* Botones */
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

# --- CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
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
        st.link_button("ENTRAR", "https://partners.segurma.com/", use_container_width=True)
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://o2online.es/auth/login/", use_container_width=True)

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
            {"PRIORIDAD": 3, "COMPAÑÍA": "GANA ENERGÍA", "FIJO RL1": "3,93 €", "ENERGIA RL1": "VARIABLE", "FIJO RL2": "8,11 €", "ENERGIA RL2": "VARIABLE"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 SOLO FIBRA</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        for i, (vel, pre) in enumerate([("300 Mb", "23€"), ("600 Mb", "27€"), ("1 Gb", "31€")]):
            with f_cols[i]: st.markdown(f'<div class="price-card"><div class="price-title">FIBRA {vel}</div><div class="price-val">{pre}</div></div>', unsafe_allow_html=True)

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

    p_calc = 0.11 # Simplificación para el cálculo
    coste_total_iva = ((potencia * sel["P1"] * dias_factura) + (consumo * p_calc)) * 1.21
    ahorro = f_act - coste_total_iva
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

# --- DASHBOARD PROFESIONAL (ARREGLADO) ---
elif menu == "📈 DASHBOARD":
    st.header("🏆 Dashboard de Ventas | Basette Group")
    
    # Enlace al CSV de tu Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        # Carga de datos con limpieza de nombres de columnas
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip().str.upper() # Normalizamos nombres de columnas
        
        # Intentar procesar fecha
        if 'FECHA' in df.columns:
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
            df['MES'] = df['FECHA'].dt.month_name().fillna('Sin Mes')
            df['AÑO'] = df['FECHA'].dt.year.fillna(2026).astype(int)
        else:
            df['MES'] = 'Datos'
            df['AÑO'] = 2026

        # --- FILTROS MEJORADOS ---
        with st.container():
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                meses = ["Todos"] + sorted(df['MES'].unique().tolist())
                sel_mes = st.selectbox("Mes", meses)
            with f2:
                años = ["Todos"] + sorted([str(a) for a in df['AÑO'].unique().tolist()])
                sel_año = st.selectbox("Año", años)
            with f3:
                comp_col = 'COMPAÑIA' if 'COMPAÑIA' in df.columns else (df.columns[1] if len(df.columns)>1 else df.columns[0])
                comps = ["Todas"] + sorted(df[comp_col].dropna().unique().tolist())
                sel_comp = st.selectbox("Compañía", comps)
            with f4:
                agente_col = 'AGENTE' if 'AGENTE' in df.columns else (df.columns[0])
                agentes = sorted(df[agente_col].dropna().unique().tolist())
                sel_com = st.multiselect("Comerciales", agentes, default=agentes)

        # Aplicar filtros
        df_filt = df.copy()
        if sel_mes != "Todos": df_filt = df_filt[df_filt['MES'] == sel_mes]
        if sel_año != "Todos": df_filt = df_filt[df_filt['AÑO'] == int(sel_año)]
        if sel_comp != "Todas": df_filt = df_filt[df_filt[comp_col] == sel_comp]
        if sel_com: df_filt = df_filt[df_filt[agente_col].isin(sel_com)]

        # --- CUADRO DE TOTALES ---
        st.markdown('<div class="block-header">📊 RESUMEN GENERAL</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        # Buscamos columnas de CUPS LUZ y GAS o similares
        luz_col = [c for c in df.columns if 'LUZ' in c]
        gas_col = [c for c in df.columns if 'GAS' in c]
        
        v_luz = df_filt[luz_col[0]].count() if luz_col else 0
        v_gas = df_filt[gas_col[0]].count() if gas_col else 0
        
        c1.metric("VENTAS LUZ", f"{v_luz} ⚡")
        c2.metric("VENTAS GAS", f"{v_gas} 🔥")
        c3.metric("TOTAL VENTAS", f"{v_luz + v_gas} 🏆")

        # --- RANKING COMERCIAL ---
        st.markdown('<div class="block-header">👑 RANKING POR COMERCIAL</div>', unsafe_allow_html=True)
        
        # Agrupamos para el ranking
        ranking = df_filt.groupby(agente_col).size().reset_index(name='TOTAL')
        ranking = ranking.sort_values(by='TOTAL', ascending=False)
        
        fig = px.bar(ranking, x=agente_col, y='TOTAL', 
                     text='TOTAL',
                     color_discrete_sequence=['#d2ff00'],
                     template="plotly_dark")
        fig.update_layout(xaxis_title="Comercial", yaxis_title="Ventas Totales", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # --- TABLA DE DETALLE ---
        st.markdown('<div class="block-header">📋 DETALLE DE OPERACIONES</div>', unsafe_allow_html=True)
        st.dataframe(df_filt, use_container_width=True)

    except Exception as e:
        st.error("No se pudo conectar con el Google Sheet. Verifica que esté compartido como 'Cualquier persona con el enlace'.")
        st.info(f"Error: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 ARGUMENTARIOS DE VENTA"):
        st.write("Selecciona un archivo para descargar.")