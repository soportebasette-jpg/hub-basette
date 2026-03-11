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

# 2. CSS DE ALTA VISIBILIDAD (Con ajustes para CRM compacto)
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
        background-color: #d2ff00; color: black; padding: 5px 15px; border-radius: 5px;
        font-weight: bold; margin-bottom: 10px; margin-top: 15px; display: inline-block; font-size: 1rem;
    }
    /* Estilo CRM Compacto */
    .crm-card {
        background: #161b22; 
        padding: 10px; 
        border-radius: 8px; 
        border: 1px solid #30363d; 
        text-align: center; 
        margin-bottom: 5px;
    }
    .crm-title { color: white; margin: 0; font-size: 0.9rem; font-weight: bold; }
    
    /* Precios Fibra */
    .price-card {
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
    }
    .price-title { color: #d2ff00; font-size: 1.1rem; font-weight: bold; }
    .price-val { color: white; font-size: 1.8rem; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATOS
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,163/0,096/0,072", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"}
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
    menu = st.radio("Secciones:", ["📊 DASHBOARD", "🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📂 REPOSITORIO"])

# --- DASHBOARD (ARREGLADO CON ROSCO Y COLORES) ---
if menu == "📊 DASHBOARD":
    st.header("Control de Ventas Real-Time")
    try:
        # Carga de datos (simulada o desde Excel)
        df = pd.read_excel("Ventas.xlsx")
        
        # Métricas principales
        c1, c2, c3 = st.columns(3)
        v_luz = len(df[df['TIPO'] == 'LUZ'])
        v_gas = len(df[df['TIPO'] == 'GAS'])
        
        c1.markdown(f'<div style="text-align:center;"><h3>⚡ VENTAS LUZ</h3><h1 style="color:#d2ff00;">{v_luz}</h1></div>', unsafe_allow_html=True)
        # GAS EN ROJO COMO PEDISTE
        c2.markdown(f'<div style="text-align:center;"><h3>🔥 VENTAS GAS</h3><h1 style="color:#ff4b4b;">{v_gas}</h1></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="text-align:center;"><h3>🏆 TOTAL</h3><h1 style="color:white;">{len(df)}</h1></div>', unsafe_allow_html=True)
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("Ventas por Comercial")
            fig_bar = px.bar(df, x='COMERCIAL', color='TIPO', barmode='group',
                             color_discrete_map={'LUZ': '#d2ff00', 'GAS': '#ff4b4b'})
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_graf2:
            st.subheader("Ventas por Compañía (%)")
            # ROSCO DE VENTAS CON COLOR GANA PERSONALIZADO
            fig_pie = px.pie(df, names='COMPAÑIA', hole=0.5,
                             color='COMPAÑIA',
                             color_discrete_map={'GANA ENERGIA': '#d2ff00', 'ENDESA': '#0056b3', 'NATURGY': '#858585'})
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

    except:
        st.warning("Para ver el Dashboard, sube el archivo 'Ventas.xlsx' con columnas: COMERCIAL, COMPAÑIA, TIPO")

# --- CRM (MÁS PEQUEÑO Y RECOGIDO) ---
elif menu == "🚀 CRM":
    st.header("Portales de Gestión")
    
    st.markdown('<div class="block-header">⭐ MARCADOR PRINCIPAL</div>', unsafe_allow_html=True)
    st.link_button("ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [
        {"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"},
        {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"},
        {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"},
        {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/"},
        {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"},
        {"n": "ENDESA", "u": "https://inergia.app"}
    ]
    
    cols_en = st.columns(4) # Más columnas para que sean más pequeños
    for i, p in enumerate(energia):
        with cols_en[i % 4]:
            st.markdown(f'<div class="crm-card"><p class="crm-title">{p["n"]}</p></div>', unsafe_allow_html=True)
            st.link_button("ACCEDER", p["u"], use_container_width=True)

    st.markdown('<div class="block-header">🛡️ ALARMAS Y OTROS</div>', unsafe_allow_html=True)
    c_extra = st.columns(4)
    with c_extra[0]:
        st.markdown(f'<div class="crm-card"><p class="crm-title">SEGURMA</p></div>', unsafe_allow_html=True)
        st.link_button("ACCEDER", "https://partners.segurma.com/", use_container_width=True)
    with c_extra[1]:
        st.markdown(f'<div class="crm-card"><p class="crm-title">O2 ONLINE</p></div>', unsafe_allow_html=True)
        st.link_button("ACCEDER", "https://o2online.es/auth/login/", use_container_width=True)

# --- PRECIOS (COMPLETADOS FIBRA) ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([
            {"COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"},
            {"COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 OFERTA FIBRA Y MÓVIL COMPLETA</div>', unsafe_allow_html=True)
        f_cols = st.columns(4)
        # Datos completados según lo pedido
        ofertas = [
            ("FIBRA 300Mb", "23€", "Solo Fibra"),
            ("FIBRA 600Mb", "27€", "Solo Fibra"),
            ("FIBRA 1Gb", "31€", "Solo Fibra"),
            ("300Mb + 40GB", "30€", "Fibra + Móvil"),
            ("600Mb + 60GB", "35€", "Fibra + Móvil"),
            ("1Gb + 120GB", "38€", "Fibra + Móvil"),
            ("600Mb + TV", "38€", "Pack M+ Incluido"),
            ("1Gb + TV", "50€", "Pack M+ Incluido")
        ]
        for i, (tit, pre, sub) in enumerate(ofertas):
            with f_cols[i % 4]:
                st.markdown(f'<div class="price-card"><div class="price-title">{tit}</div><div class="price-val">{pre}</div><div class="price-sub">{sub}</div></div>', unsafe_allow_html=True)

# --- COMPARADOR (VUELVE A SER EL ORIGINAL) ---
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

    # Cálculo simple para el PDF
    try: p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    except: p_calc = 0.11
    
    coste_total_iva = ((potencia * sel["P1"] * dias_factura * 2) + (consumo * p_calc)) * 1.21
    ahorro = f_act - coste_total_iva

    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)
    
    if st.button("GENERAR ESTUDIO PDF PROFESIONAL"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ESTUDIO COMPARATIVO DE AHORRO - BASETTE GROUP", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, f"Cliente: {cliente}", ln=True)
        pdf.cell(190, 10, f"Ahorro mensual estimado: {ahorro:.2f} EUR", ln=True)
        st.download_button(label="📥 DESCARGAR PDF", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Estudio_{cliente}.pdf")

# --- REPOSITORIO (VUELVE A SER EL ORIGINAL CON CARPETAS) ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación y Argumentarios")
    
    with st.expander("📂 ARGUMENTARIOS DE VENTA"):
        docs = ["ARGUMENTARIO_ENERGÍA.docx", "ARGUMENTARIO_TELECO.docx", "OBJECIONES.docx"]
        for d in docs:
            st.write(f"📘 {d}")
            
    for c in ["GANA ENERGÍA", "NATURGY", "TOTAL", "ENDESA", "O2"]:
        with st.expander(f"📁 DOCUMENTACIÓN {c}"):
            st.write(f"Archivos disponibles para {c}...")
            # Aquí buscaría archivos reales en la carpeta manuales si existen