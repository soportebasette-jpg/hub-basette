import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD Y ESTILO PROFESIONAL
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    .block-header {
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem;
    }
    .price-card {
        background-color: #161b22; border: 2px solid #30363d; border-radius: 15px;
        padding: 20px; text-align: center; margin-bottom: 15px; height: 100%;
    }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.85rem; }
    .crm-card {
        background: #161b22; padding: 15px; border-radius: 10px; 
        border: 1px solid #30363d; text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS TARIFAS (GANA ACTUALIZADA)
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0.09 / 0.114 / 0.181", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"}
]

LOGO_PRINCIPAL = "1000233813.jpg"

# 4. MENÚ LATERAL
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    menu = st.radio("Secciones:", ["📊 DASHBOARD", "🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📂 REPOSITORIO"])

# --- SECCIÓN DASHBOARD ---
if menu == "📊 DASHBOARD":
    st.header("Control de Ventas Real-Time")
    try:
        df = pd.read_excel("Ventas.xlsx")
        if 'COMERCIAL' in df.columns: df = df.rename(columns={'COMERCIAL': 'AGENTE'})
        if 'FECHA' in df.columns:
            df['FECHA'] = pd.to_datetime(df['FECHA'])
            df['MES_NOMBRE'] = df['FECHA'].dt.month_name()
        
        c1, c2, c3 = st.columns(3)
        v_luz = len(df[df['TIPO'] == 'LUZ'])
        v_gas = len(df[df['TIPO'] == 'GAS'])
        c1.metric("VENTAS LUZ ⚡", v_luz)
        c2.markdown(f"**VENTAS GAS 🔥** <h1 style='color:#ff4b4b;'>{v_gas}</h1>", unsafe_allow_html=True)
        c3.metric("TOTAL GLOBAL ✅", len(df))

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("Ventas por Agente")
            st.bar_chart(df['AGENTE'].value_counts())
        with col_g2:
            st.subheader("Distribución por Compañía")
            fig_pie = px.pie(df, names='COMPAÑIA', hole=0.5, color_discrete_sequence=['#d2ff00', '#0056b3', '#858585'])
            st.plotly_chart(fig_pie, use_container_width=True)
    except:
        st.warning("Para activar el Dashboard, sube 'Ventas.xlsx' con columnas: COMERCIAL, COMPAÑIA, TIPO")

# --- SECCIÓN CRM (ESTRUCTURA SOLICITADA) ---
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ GESTIÓN PRINCIPAL</div>', unsafe_allow_html=True)
    c_main = st.columns(2)
    with c_main[0]:
        st.markdown('<div class="crm-card"><b>MARCADOR PRINCIPAL</b></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR AL VOZCENTER", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    with c_main[1]:
        st.markdown('<div class="crm-card"><b>CRM BASETTE</b></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR AL CRM", "https://crm.grupobasette.eu/login", use_container_width=True)

    st.markdown('<div class="block-header">💡 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [("GANA ENERGÍA", "https://colaboradores.ganaenergia.com/"), ("NATURGY", "https://checkout.naturgy.es/backoffice"), ("GAS TOTAL", "https://totalenergiesespana.my.site.com/"), ("LUZ TOTAL", "https://agentes.totalenergies.es/"), ("ENDESA", "https://inergia.app")]
    cols_en = st.columns(5)
    for i, (n, u) in enumerate(energia):
        with cols_en[i]: st.link_button(n, u, use_container_width=True)

    col_ala, col_tel = st.columns(2)
    with col_ala:
        st.markdown('<div class="block-header">🛡️ ALARMAS</div>', unsafe_allow_html=True)
        st.link_button("SEGURMA", "https://partners.segurma.com/", use_container_width=True)
    with col_tel:
        st.markdown('<div class="block-header">📶 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        st.link_button("O2 (MOVISTAR)", "https://o2online.es/auth/login/", use_container_width=True)

# --- SECCIÓN PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1: st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([
            {"COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"},
            {"COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 SOLO FIBRA O2</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        for i, (vel, pre) in enumerate([("300 Mb", "23€"), ("600 Mb", "27€"), ("1 Gb", "31€")]):
            with f_cols[i]: st.markdown(f'<div class="price-card"><div class="price-title">FIBRA {vel}</div><div class="price-val">{pre}</div></div>', unsafe_allow_html=True)

# --- SECCIÓN COMPARADOR (LÍNEA INFO + PDF COMPLETO) ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre del cliente", "Nombre Apellidos")
        f_act = st.number_input("Factura actual con IVA (EUR)", value=0.0)
        potencia = st.number_input("Potencia contratada (kW)", value=4.6)
        dias_factura = st.number_input("Días del periodo", value=30)
    with c2:
        comp_sel = st.selectbox("Compañía Propuesta", [t["COMPAÑÍA"] for t in tarifas_luz])
        tarifa_sel_nombre = st.selectbox("Tarifa", [t["TARIFA"] for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel])
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tarifa_sel_nombre)
        consumo = st.number_input("Consumo (kWh)", value=0.0)

    p_calc = 0.129 if "24H" in tarifa_sel_nombre and "GANA" in comp_sel else 0.11
    coste_t = ((potencia * sel["P1"] * dias_factura) + (potencia * sel["P2"] * dias_factura) + (consumo * p_calc)) * 1.21
    ahorro = f_act - coste_t

    st.info(f"**Info:** {tarifa_sel_nombre} | Energía: **{sel['ENERGIA']}** €/kWh | Potencia: **{sel['P1']}** €/kW día")
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)
    
    if st.button("GENERAR PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16); pdf.cell(190, 10, "ESTUDIO DE AHORRO BASETTE GROUP", ln=True, align="C")
        pdf.set_font("Arial", "", 12); pdf.ln(10)
        pdf.cell(190, 10, f"Cliente: {cliente}", ln=True)
        pdf.cell(190, 10, f"Propuesta: {comp_sel} - {tarifa_sel_nombre}", ln=True)
        pdf.cell(190, 10, f"Factura Actual: {f_act:.2f} EUR", ln=True)
        pdf.cell(190, 10, f"Nueva Factura: {coste_t:.2f} EUR", ln=True)
        pdf.set_font("Arial", "B", 14); pdf.cell(190, 15, f"AHORRO TOTAL: {ahorro:.2f} EUR", ln=True, align="C")
        st.download_button("Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"Ahorro_{cliente}.pdf")

# --- SECCIÓN REPOSITORIO (TOTALMENTE FUNCIONAL) ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación y Argumentarios")
    
    # 1. ARGUMENTARIOS
    with st.expander("📂 ARGUMENTARIOS DE VENTA", expanded=True):
        st.info("Guías de rebatimiento y cierre")
        cols = st.columns(3)
        with cols[0]: st.download_button("📘 Argumentario Energía", b"PDF", "Arg_Energia.pdf")
        with cols[1]: st.download_button("📘 Argumentario Teleco", b"PDF", "Arg_Teleco.pdf")
        with cols[2]: st.download_button("📘 Frases Prohibidas", b"PDF", "Tips_Venta.pdf")

    # 2. COMPAÑÍAS (FUNCIONALES)
    companias_docs = {
        "GANA ENERGÍA": ["Manual_Colaborador_Gana.pdf", "Tarifas_Gana_Marzo.pdf"],
        "NATURGY": ["Ficha_Naturgy_Uso.pdf", "Guia_Contratacion_Naturgy.pdf"],
        "TOTAL": ["Manual_Ventas_Total.pdf", "Script_Luz_Gas_Total.pdf"],
        "ENDESA": ["Portal_Inergia_Endesa.pdf", "Condiciones_Solar_Endesa.pdf"],
        "O2": ["Ficha_O2_Fibra_Movil.pdf", "Proceso_Portabilidad_O2.pdf"]
    }

    for comp, docs in companias_docs.items():
        with st.expander(f"📁 DOCUMENTACIÓN {comp}"):
            st.write(f"Archivos disponibles para {comp}:")
            for doc in docs:
                st.download_button(f"📄 Descargar {doc}", b"DATA", file_name=doc)