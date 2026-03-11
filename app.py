import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Basette Group | Hub", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .block-header { background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    pwd = st.text_input("Clave Comercial:", type="password")
    if st.button("ACCEDER"):
        if pwd == "Ventas2024*":
            st.session_state["password_correct"] = True
            st.rerun()
    st.stop()

# --- NAVEGACIÓN ---
with st.sidebar:
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📂 REPOSITORIO", "📈 DASHBOARD"])

# --- LÓGICA DE SECCIONES (Resumida para brevedad, mantén tu lógica de tarifas) ---

if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.link_button("ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    if os.path.exists("manuales"):
        for fn in os.listdir("manuales"):
            if fn.lower().endswith(('.pdf', '.docx', '.xlsx')):
                # SOLUCIÓN AL ERROR UNICODE: Leer siempre en modo binario "rb"
                with open(f"manuales/{fn}", "rb") as f:
                    st.download_button(f"📥 Descargar {fn}", f, file_name=fn)

elif menu == "📈 DASHBOARD":
    st.header("🏆 Análisis de Ventas")
    try:
        # Cargar credenciales desde Secrets (Formato TOML)
        info = st.secrets["gcp_service_account"]
        
        # Limpiar la clave privada por si acaso
        credentials_info = dict(info)
        credentials_info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # ID de tu hoja de cálculo
        sheet_id = "1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ"
        sh = client.open_by_key(sheet_id)
        worksheet = sh.get_worksheet(0) # Lee la primera pestaña
        
        df = pd.DataFrame(worksheet.get_all_records())
        
        if not df.empty:
            st.success("Sincronización exitosa")
            st.dataframe(df, use_container_width=True)
            # Gráfico simple de ventas por comercial
            if 'Comercial' in df.columns:
                st.bar_chart(df['Comercial'].value_counts())
        else:
            st.info("La hoja de cálculo está vacía.")
            
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        st.info("Asegúrate de que el bot tenga acceso de 'Editor' en el botón compartir del Excel.")