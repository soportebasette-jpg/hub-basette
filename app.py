import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Hub Basette", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
        color: black;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #d0d2d6;
        border-color: #f0f2f6;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(credentials)

def get_sheet_data(sheet_name):
    try:
        client = get_gspread_client()
        spreadsheet = client.open("Hub Basette Data")
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error cargando {sheet_name}: {e}")
        return pd.DataFrame()

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Hub Basette - Gestión Comercial")

tabs = st.tabs(["📊 Dashboard", "📝 Registro", "📂 Documentación", "🔗 Enlaces Rápidos"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    st.header("Dashboard de Rendimiento y Ranking")
    
    df_ventas = get_sheet_data("Ventas")
    
    if not df_ventas.empty:
        try:
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                años = sorted(df_ventas['Año'].unique(), reverse=True)
                año_sel = st.selectbox("📅 Año", años)
            with col2:
                meses = ["01 - January", "02 - February", "03 - March", "04 - April", "05 - May", "06 - June", 
                         "07 - July", "08 - August", "09 - September", "10 - October", "11 - November", "12 - December"]
                mes_sel = st.selectbox("🗓️ Mes", meses)
            with col3:
                comerciales = sorted(df_ventas['Comercial'].unique())
                comercial_sel = st.multiselect("👤 Comerciales", comerciales, default=comerciales)

            # Filtrar datos
            mask = (df_ventas['Año'] == año_sel) & (df_ventas['Mes'] == mes_sel) & (df_ventas['Comercial'].isin(comercial_sel))
            df_filtrado = df_ventas[mask]

            if not df_filtrado.empty:
                # Métricas principales
                total_ventas = len(df_filtrado)
                ventas_fibra = len(df_filtrado[df_filtrado['V_Fibra'] == 'SÍ'])
                ventas_movil = len(df_filtrado[df_filtrado['V_Movil'] == 'SÍ'])
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Ventas", total_ventas)
                m2.metric("Fibras", ventas_fibra)
                m3.metric("Líneas Móviles", ventas_movil)

                # Ranking
                st.subheader("🏆 Ranking de Comerciales")
                ranking = df_filtrado.groupby('Comercial').size().reset_index(name='Ventas totales')
                ranking = ranking.sort_values(by='Ventas totales', ascending=False)
                st.table(ranking)
            else:
                st.warning("No hay datos para los filtros seleccion Expanda su selección.")
        except Exception as e:
            st.error(f"Error cargando el Dashboard: {e}")
    else:
        st.info("Aún no hay datos registrados.")

# --- TAB 2: REGISTRO ---
with tabs[1]:
    st.header("Registro de Nueva Venta")
    with st.form("registro_venta"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fecha = st.date_input("Fecha de Venta", datetime.now())
            comercial_reg = st.selectbox("Comercial", ["RAQUEL GUADA...", "OTRO"]) # Añade tus nombres reales
            cliente = st.text_input("Nombre del Cliente")
        with col_f2:
            tipo_fibra = st.selectbox("¿Venta Fibra?", ["SÍ", "NO"])
            tipo_movil = st.selectbox("¿Venta Móvil?", ["SÍ", "NO"])
            observaciones = st.text_area("Observaciones")
        
        submit = st.form_submit_button("REGISTRAR EN EXCEL")
        
        if submit:
            try:
                client = get_gspread_client()
                sheet = client.open("Hub Basette Data").worksheet("Ventas")
                nueva_fila = [
                    fecha.strftime("%Y-%m-%d"),
                    fecha.year,
                    f"{fecha.strftime('%m')} - {fecha.strftime('%B')}",
                    comercial_reg,
                    cliente,
                    tipo_fibra,
                    tipo_movil,
                    observaciones
                ]
                sheet.append_row(nueva_fila)
                st.success("✅ Venta registrada correctamente")
            except Exception as e:
                st.error(f"Error al registrar: {e}")

# --- TAB 3: DOCUMENTACIÓN ---
with tabs[2]:
    st.header("Documentación")
    
    with st.expander("📂 DOCUMENTACIÓN LOWI"):
        st.write("Contenido de Lowi aquí...")

    with st.expander("📂 CAPTURAS O2 PARA ENVIAR A CLIENTES", expanded=True):
        st.write("Visualiza y descarga las tarifas actuales de O2 para enviar:")
        
        # Diccionario con los archivos corregidos apuntando a la carpeta 'manuales'
        archivos_o2 = {
            "Fibra 600Mb / 35Gb y TV": "manuales/600Mb_35Gb y TV.png",
            "Fibra 600Mb / 60Gb y TV": "manuales/600Mb_60Gb y TV.png",
            "Fibra 1Gb / 350Gb y TV": "manuales/1Gb_30Gb y TV.png",
            "Fibra 1Gb / 375Gb y TV": "manuales/1Gb_375Gb y TV.png",
            "Líneas Móviles Adicionales": "manuales/LINEAS MOVILES ADICIONALES.png"
        }
        
        cols = st.columns(2)
        for i, (nombre, ruta) in enumerate(archivos_o2.items()):
            with cols[i % 2]:
                if os.path.exists(ruta):
                    st.image(ruta, caption=nombre, use_container_width=True)
                    with open(ruta, "rb") as file:
                        st.download_button(
                            label=f"Descargar {nombre}",
                            data=file,
                            file_name=os.path.basename(ruta),
                            mime="image/png",
                            key=f"btn_{i}"
                        )
                else:
                    st.error(f"Imagen no encontrada: {os.path.basename(ruta)}")

# --- TAB 4: ENLACES RÁPIDOS ---
with tabs[3]:
    st.header("Enlaces de Interés")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.link_button("🌐 Portal Movistar", "https://www.movistar.es")
    with col_e2:
        st.link_button("🌐 Portal O2", "https://o2online.es")
    with col_e3:
        st.link_button("🌐 CRM Interno", "https://tucrm.com")