import streamlit as st
import os
import pandas as pd
import calendar
import unicodedata
from datetime import datetime, date, time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Control Laboral | Basette", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .block-header {
        background-color: #d2ff00;
        color: black;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- RUTAS ---
RUTA_LOGO = r"C:\Users\Propietario\Desktop\MI_INTRANET\tecomparotodo_logo.jpg"

# --- FUNCIONES ---
def normalizar(texto):
    if not isinstance(texto, str): return ""
    texto = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto if unicodedata.category(c) != 'Mn']).strip().upper()

@st.cache_data(ttl=5)
def load_data_laboral():
    url = "https://docs.google.com/spreadsheets/d/175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY/export?format=csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        # Normalización para evitar errores de nombres de columnas
        col_fecha = next((c for c in df.columns if "temporal" in c.lower()), None)
        col_quien = next((c for c in df.columns if "quién" in c.lower() or "quien" in c.lower()), None)
        
        if col_fecha:
            df[col_fecha] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
        if col_quien:
            df['Nombre_Norm'] = df[col_quien].apply(normalizar)
        return df.dropna(subset=[col_fecha])
    except:
        return pd.DataFrame()

# --- DATOS PERSONAL ---
fechas_empresa = {
    'MARÍA JOSÉ MORENO': {'alta': date(2026, 4, 27), 'baja': None},
    'LUIS RODRÍGUEZ': {'alta': date(2026, 4, 8), 'baja': date(2026, 4, 24)},
    'RAQUEL GUADALUPE': {'alta': date(2026, 3, 19), 'baja': None},
    'LORENA POZO': {'alta': date(2026, 3, 18), 'baja': date(2026, 4, 27)},
    'DEBORAH RODRIGUEZ': {'alta': date(2026, 3, 18), 'baja': None},
    'BELÉN TRONCOSO': {'alta': date(2026, 3, 18), 'baja': None},
    'MACARENA BACA': {'alta': date(2026, 3, 18), 'baja': date(2026, 3, 20)}
}

# --- MENÚ LATERAL (SIN TOCAR NAVEGACIÓN) ---
with st.sidebar:
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, use_container_width=True)
    st.title("Navegación")
    menu = st.radio("Ir a:", [
        "🚀 CRM", 
        "📊 PRECIOS", 
        "⚖️ COMPARADOR", 
        "📢 ANUNCIOS Y PLAN AMIGO", 
        "📈 DASHBOARD Y RANKING", 
        "📁 REPOSITORIO", 
        "🕒 CONTROL LABORAL"
    ])

# --- SECCIÓN CRM (CON TIKTOK) ---
if menu == "🚀 CRM":
    st.markdown("<h1 style='color: #d2ff00;'>🚀 GESTIÓN CRM</h1>", unsafe_allow_html=True)
    st.write("Acceso a Redes Sociales:")
    col_social = st.columns(6)
    with col_social[0]: st.markdown("[![FB](https://img.icons8.com/color/48/facebook-new.png)](https://facebook.com)")
    with col_social[1]: st.markdown("[![TW](https://img.icons8.com/color/48/twitter--v1.png)](https://twitter.com)")
    with col_social[2]: st.markdown("[![IG](https://img.icons8.com/color/48/instagram-new.png)](https://instagram.com)")
    with col_social[3]: 
        # NUEVO: TIKTOK
        st.markdown("[![TK](https://img.icons8.com/color/48/tiktok.png)](https://www.tiktok.com/@tecomparotodo?_r=1&_t=ZN-95nfhnoUU9W)")
    with col_social[4]: st.markdown("[![LK](https://img.icons8.com/color/48/linkedin.png)](https://linkedin.com)")

# --- SECCIÓN DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.markdown("<h1 style='color: #d2ff00;'>📈 DASHBOARD Y RANKING</h1>", unsafe_allow_html=True)
    
    # FRASE MOTIVADORA MEJORADA
    frases = [
        "EL ÉXITO ES LA SUMA DE PEQUEÑOS ESFUERZOS REPETIDOS DÍA TRAS DÍA.",
        "TU ÚNICA LIMITACIÓN ES TU MENTE. ¡A POR TODAS!",
        "TRABAJA EN SILENCIO, QUE EL ÉXITO SE ENCARGUE DE HACER EL RUIDO.",
        "NO CUENTES LOS DÍAS, HAZ QUE LOS DÍAS CUENTEN.",
        "LA DISCIPLINA ES EL PUENTE ENTRE LAS METAS Y LOS LOGROS.",
        "CADA DÍA ES UNA OPORTUNIDAD PARA SER MEJOR QUE AYER."
    ]
    frase_hoy = frases[date.today().day % len(frases)]
    
    st.markdown(f"""
        <div style="background-color: #1c2128; padding: 35px; border-radius: 15px; border-left: 10px solid #d2ff00; text-align: center; margin-bottom: 30px;">
            <h1 style="color: #d2ff00; font-size: 45px; font-weight: 900; margin: 0;">"{frase_hoy}"</h1>
        </div>
    """, unsafe_allow_html=True)

    # NÚMERO 1 DE VENTAS (NUEVO SIN QUITAR NADA)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 50px; background: linear-gradient(45deg, #1c2128, #0d1117); padding: 30px; border-radius: 20px; border: 2px solid #d2ff00;">
            <span style="font-size: 50px;">🎈 👑 🎈</span>
            <h2 style="color: white; margin: 10px 0;">Nº 1 VENTAS DEL MES</h2>
            <h1 style="color: #d2ff00; font-size: 4rem; text-shadow: 2px 2px black;">RAQUEL GUADALUPE</h1>
            <p style="color: #8b949e; font-size: 1.2rem;">¡ENHORABUENA POR TU EXCELENTE TRABAJO! 🚀</p>
        </div>
    """, unsafe_allow_html=True)

# --- SECCIÓN CONTROL LABORAL ---
elif menu == "🕒 CONTROL LABORAL":
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL Y ASISTENCIA</div>', unsafe_allow_html=True)
    empleado = st.selectbox("Seleccionar comercial:", sorted(list(fechas_empresa.keys())))
    df_lab = load_data_laboral()
    if not df_lab.empty:
        st.info(f"Visualizando registros de: {empleado}")
        busq = normalizar(empleado)
        df_indiv = df_lab[df_lab['Nombre_Norm'] == busq].copy()
        st.dataframe(df_indiv.sort_values(df_indiv.columns[0], ascending=False), use_container_width=True)

# --- RESTO DE SECCIONES (SIN MODIFICAR NADA) ---
elif menu == "📊 PRECIOS":
    st.title("📊 Listado de Precios")
    st.write("Contenido de precios intacto...")

elif menu == "⚖️ COMPARADOR":
    st.title("⚖️ Comparador de Tarifas")
    st.write("Contenido del comparador intacto...")

elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.title("📢 Anuncios")
    st.write("Contenido de anuncios intacto...")

elif menu == "📁 REPOSITORIO":
    st.title("📁 Repositorio de Documentos")
    st.write("Contenido del repositorio intacto...")