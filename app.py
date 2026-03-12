import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard Basette Group", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    .status-error { background-color: #3e1919; color: #ff4b4b; padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DE TARIFAS (COMPLETA) ---
# Se han añadido todos los tramos según la documentación visual
tarifas_fibra = [
    {"nombre": "Tarifa 24 horas", "antiguo": "0,111€", "nuevo": "0,129€"},
    {"nombre": "Tarifa Tramos (Valle)", "antiguo": "0,072€", "nuevo": "0,090€"},
    {"nombre": "Tarifa Tramos (Llano)", "antiguo": "0,096€", "nuevo": "0,114€"},
    {"nombre": "Tarifa Tramos (Punta)", "antiguo": "0,163€", "nuevo": "0,181€"}
]

# --- LÓGICA DEL DASHBOARD ---
st.title("🏆 Dashboard Ejecutivo | Basette Group")

# Simulación de carga y manejo de errores de columnas
try:
    # Nota: Aquí deberías tener tu lógica de st.file_uploader o conexión a Sheets
    # Para el ejemplo, definimos las columnas requeridas para que no falle el renderizado
    uploaded_file = st.sidebar.file_uploader("Subir archivo de ventas", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        
        # Corrección de errores 'MES_NOMBRE' y 'AÑO_INT':
        # Si las columnas no existen, las creamos a partir de 'FECHA DE CREACIÓN'
        if 'FECHA DE CREACIÓN' in df.columns:
            df['FECHA DE CREACIÓN'] = pd.to_datetime(df['FECHA DE CREACIÓN'])
            if 'MES_NOMBRE' not in df.columns:
                df['MES_NOMBRE'] = df['FECHA DE CREACIÓN'].dt.month_name()
            if 'AÑO_INT' not in df.columns:
                df['AÑO_INT'] = df['FECHA DE CREACIÓN'].dt.year

        # --- FILTROS ---
        with st.expander("🔍 FILTROS AVANZADOS", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                meses = df['MES_NOMBRE'].unique().tolist() if 'MES_NOMBRE' in df.columns else []
                mes_sel = st.multiselect("Filtrar Meses", options=meses, default=meses)
            with col_f2:
                años = df['AÑO_INT'].unique().tolist() if 'AÑO_INT' in df.columns else [2026]
                año_sel = st.selectbox("Seleccionar Año", options=años)

        # --- RESUMEN DE CIFRAS ---
        st.markdown("### 📊 RESUMEN DE CIFRAS")
        c1, c2, c3 = st.columns(3)
        
        # Ejemplo de conteo (ajusta 'TIPO' según tu Excel: Luz/Gas)
        luz = len(df[df['TIPO'].str.contains('LUZ', case=False, na=False)])
        gas = len(df[df['TIPO'].str.contains('GAS', case=False, na=False)])
        
        c1.metric("VENTAS LUZ", f"{luz} ⚡")
        c2.metric("VENTAS GAS", f"{gas} 🔥")
        c3.metric("TOTAL GLOBAL", f"{luz + gas} ✅")

        # --- GRÁFICOS ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("### 👑 RANKING POR COMERCIAL")
            fig_rank = px.bar(df, x='COMERCIAL', color='TIPO', barmode='group', template="plotly_dark")
            st.plotly_chart(fig_rank, use_container_width=True)
        
        with col_g2:
            st.markdown("### 🏢 VENTAS POR COMPAÑÍA (%)")
            fig_pie = px.pie(df, names='COMPAÑÍA', hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("👋 Por favor, sube el archivo 'Ventas.xlsx' para visualizar los datos.")
        st.warning("Asegúrate de que el Excel contenga las columnas: 'FECHA DE CREACIÓN', 'COMERCIAL', 'COMPAÑÍA' y 'TIPO'.")

except Exception as e:
    st.markdown(f'<div class="status-error"><b>Error al cargar dashboard:</b> {str(e)}</div>', unsafe_allow_html=True)

# --- SECCIÓN DE PRECIOS (CAPTACIÓN) ---
st.divider()
st.subheader("📋 Nuevo precio fijo para captación")

cols_precios = st.columns(len(tarifas_fibra))

for i, tarifa in enumerate(tarifas_fibra):
    with cols_precios[i]:
        st.markdown(f"""
            <div style="background-color:#f0f9f6; padding:20px; border-radius:15px; text-align:center; border:1px solid #b2dfdb; color:#2c3e50;">
                <p style="margin:0; font-weight:bold; font-size:14px;">{tarifa['nombre']}</p>
                <div style="display:flex; align-items:center; justify-content:center; gap:10px; margin-top:10px;">
                    <span style="color:#00897b; font-size:18px; font-weight:bold; opacity:0.5;">{tarifa['antiguo']}</span>
                    <span style="color:#2c3e50;">→</span>
                    <span style="color:#00897b; font-size:22px; font-weight:bold; background:#b2dfdb; padding:5px 10px; border-radius:8px;">{tarifa['nuevo']}</span>
                </div>
                <p style="margin:0; font-size:12px; color:#00897b;">/kWh</p>
            </div>
        """, unsafe_allow_html=True)

# --- ACCESOS DIRECTOS ---
st.divider()
st.markdown("### 🛡️ ALARMAS Y OTROS")
ca1, ca2 = st.columns(2)
ca1.button("ACCEDER SEGURMA", use_container_width=True)
ca2.button("ACCEDER O2 ONLINE", use_container_width=True)