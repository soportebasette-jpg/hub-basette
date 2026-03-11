import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS GENERAL Y ESPECÍFICO PARA DASHBOARD (Reparado para visibilidad)
st.markdown("""
    <style>
    /* Estilos Generales (Mantenidos) */
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* Estilos de elementos globales (Mantenidos) */
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
    
    /* === CORRECCIÓN EXCLUSIVA DE COLORES PARA EL DASHBOARD === */
    /* Forzar color verde neón en las etiquetas de los filtros del Dashboard */
    .element-container div[data-testid="stMarkdownContainer"] h3 {
        color: #d2ff00 !important;
    }
    
    /* Estilo para las etiquetas (labels) de los inputs del Dashboard */
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
    }
    
    /* Fondo oscuro y texto blanco dentro de los selectores del Dashboard */
    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
        background-color: #161b22 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }
    
    /* Texto de las opciones dentro del desplegable */
    div[data-baseweb="popover"] ul {
        background-color: #161b22 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DATOS LUZ (Mantenida)
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

# 4. SISTEMA DE LOGIN (Mantenido)
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

# 5. BARRA LATERAL Y NAVEGACIÓN (Mantenida)
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    # Asegúrate de que ' DSHBOARD' (con el espacio inicial que tenía tu radio) coincide
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📈 DSHBOARD", "📂 REPOSITORIO"], label_visibility="collapsed")

# === SECCIONES DE LA APP ===

# --- CRM (Mantenido intacto) ---
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
        st.link_button("ENTRAR", "https://partners.segurma.com/", use_container_width=True)
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://o2online.es/auth/login/", use_container_width=True)

# --- PRECIOS (Mantenido intacto) ---
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
        for vel, pre in solo_fibra:
            st.markdown(f'<div class="price-card"><div class="price-title">FIBRA {vel}</div><div class="price-val">{pre}</div></div>', unsafe_allow_html=True)

# --- COMPARADOR (Mantenido intacto) ---
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
    p_calc = 0.11 # Simplificación para el ejemplo
    coste_total_iva = ((potencia * sel["P1"] * dias_factura) + (consumo * p_calc)) * 1.21
    ahorro = f_act - coste_total_iva
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

# === 📊 DASHBOARD PROFESIONAL (REPARADO Y MEJORADO) ===
elif menu == "📈 DSHBOARD":
    st.header("🏆 Dashboard Ejecutivo | Basette Group")
    st.markdown('<div class="block-header">📊 ESTADÍSTICAS EN TIEMPO REAL</div>', unsafe_allow_html=True)
    
    # Enlace CSV de tu Google Sheet (Asegúrate de que está compartido como 'Cualquier persona con el enlace')
    sheet_url = "https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/export?format=csv"
    
    try:
        # Carga de datos
        df = pd.read_csv(sheet_url)
        
        # --- PROCESAMIENTO DE DATOS ---
        # 1. Convertir 'FECHA DE CREACIÓN' a fecha real para extraer mes visual
        # Usamos errors='coerce' para manejar celdas vacías o formatos incorrectos
        df['FECHA DE CREACIÓN'] = pd.to_datetime(df['FECHA DE CREACIÓN'], errors='coerce', dayfirst=True)
        
        # Crear columna de Mes visual (Enero, Febrero...)
        # Reemplazamos los valores NaN por 'Sin Fecha' para que no den error en el filtro
        df['MES_VISUAL'] = df['FECHA DE CREACIÓN'].dt.month_name(locale='es_ES').fillna('Sin Fecha')
        
        # Crear columna de Año para filtrar
        df['AÑO'] = df['FECHA DE CREACIÓN'].dt.year.fillna(2026).astype(int)

        # --- SECCIÓN DE FILTROS PROFESIONALES (Reparada visualmente) ---
        with st.container():
            st.markdown("### 🔍 Filtros Avanzados")
            f1, f2, f3, f4 = st.columns(4)
            
            with f1:
                # Filtro de Mes visual (Ordenado cronológicamente de Enero a Diciembre)
                orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 'Sin Fecha']
                meses_disponibles = sorted(df['MES_VISUAL'].unique(), key=lambda x: orden_meses.index(x) if x in orden_meses else 99)
                meses_lista = ["Todos"] + meses_disponibles
                sel_mes = st.selectbox("Seleccionar Mes", meses_lista)
            
            with f2:
                # Filtro de Año (Empezando desde 2026 como solicitaste)
                años_disponibles = sorted([y for y in df['AÑO'].unique() if y >= 2026])
                if not años_disponibles: años_disponibles = [2026] # Fallback si no hay fechas
                años_lista = ["Todos"] + [str(y) for y in años_disponibles]
                sel_año = st.selectbox("Seleccionar Año", años_lista)
            
            with f3:
                # Filtro de Compañía (Columna 'Comercializadora' única y ordenada)
                comp_lista = ["Todas"] + sorted(df['Comercializadora'].dropna().unique().tolist())
                sel_comp = st.selectbox("Seleccionar Compañía", comp_lista)
            
            with f4:
                # Filtro de Comercial (Columna 'Comercial' única, sumando repetidos)
                # Usamos multiselect para que puedan elegir varios o todos a la vez
                agentes_lista = sorted(df['Comercial'].dropna().unique().tolist())
                sel_com = st.multiselect("Seleccionar Comerciales (Raquel aparecerá una vez)", agentes_lista, default=agentes_lista)

        # --- APLICACIÓN DE FILTROS ---
        df_filt = df.copy()
        
        if sel_mes != "Todos":
            df_filt = df_filt[df_filt['MES_VISUAL'] == sel_mes]
            
        if sel_año != "Todos":
            df_filt = df_filt[df_filt['AÑO'] == int(sel_año)]
            
        if sel_comp != "Todas":
            df_filt = df_filt[df_filt['Comercializadora'] == sel_comp]
            
        if sel_com:
            # Filtramos por la lista de comerciales seleccionados (isin maneja múltiples valores)
            df_filt = df_filt[df_filt['Comercial'].isin(sel_com)]
        else:
            # Si deseleccionan todo en multiselect, mostramos vacío para que no explote
            df_filt = df_filt.iloc[0:0]

        # --- 👑 RANKING DE VENTAS POR AGENTE (Sumando repetidos) ---
        st.markdown('<div class="block-header">👑 RANKING DE VENTAS POR COMERCIAL</div>', unsafe_allow_html=True)
        
        # Agrupamos por Comercial y sumamos las ventas (asumiendo que cada fila es 1 venta)
        # Si tienes una columna 'CANTIDAD' o 'IMPORTE', cámbialo por .sum()
        ranking = df_filt.groupby('Comercial').size().reset_index(name='TOTAL VENTAS')
        ranking = ranking.sort_values(by='TOTAL VENTAS', ascending=False)
        
        # Creamos el gráfico interactivo profesional
        fig_ranking = px.bar(ranking, x='Comercial', y='TOTAL VENTAS', 
                             title=f"Rendimiento Comercial (Filtro: {sel_mes})",
                             text='TOTAL VENTAS', # Muestra el número encima de la barra
                             color_discrete_sequence=['#d2ff00'], # Usamos tu verde neón
                             template="plotly_dark")
        
        # Ajustes visuales finos del gráfico
        fig_ranking.update_traces(texttemplate='%{text}', textposition='outside')
        fig_ranking.update_layout(xaxis_title="Nombre del Agente", yaxis_title="Ventas Totales Realizadas", plot_bgcolor='rgba(0,0,0,0)')
        
        # Mostramos el gráfico a ancho completo
        st.plotly_chart(fig_ranking, use_container_width=True)

        # --- 📋 CUADRO DE DETALLE FILTRADO ---
        st.markdown('<div class="block-header">📋 DETALLE DE OPERACIONES FILTRADAS</div>', unsafe_allow_html=True)
        # Mostramos la tabla de datos ya filtrada
        st.dataframe(df_filt, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error al conectar con los datos: Revisa que el enlace CSV es correcto y que las columnas coinciden (FECHA DE CREACIÓN, Comercializadora, Comercial).")
        st.info(f"Detalle técnico: {e}")

# --- REPOSITORIO (Mantenido intacto) ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 ARGUMENTARIOS DE VENTA"):
        st.write("Selecciona un archivo para descargar.")