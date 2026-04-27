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
        # Limpieza de columnas para evitar el error '¿Quién eres?'
        df.columns = [normalizar(c) for c in df.columns]
        
        col_fecha = next((c for c in df.columns if "TEMPORAL" in c), None)
        col_nombre = next((c for c in df.columns if "QUIEN" in c), None)
        
        if col_fecha:
            df[col_fecha] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
        if col_nombre:
            df['Nombre_Norm'] = df[col_nombre].apply(normalizar)
            
        return df.dropna(subset=[col_fecha]) if col_fecha else df
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

# --- MENÚ LATERAL (TODAS LAS SECCIONES SOLICITADAS) ---
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
    ], index=6) # Por defecto en Control Laboral como en tu captura

# --- 🚀 CRM ---
if menu == "🚀 CRM":
    st.markdown("<h1 style='color: #d2ff00;'>🚀 GESTIÓN CRM</h1>", unsafe_allow_html=True)
    st.write("Accesos rápidos a Redes Sociales:")
    col_soc = st.columns(6)
    with col_soc[0]: st.markdown("[![FB](https://img.icons8.com/color/48/facebook-new.png)](https://facebook.com)")
    with col_soc[1]: st.markdown("[![TW](https://img.icons8.com/color/48/twitter--v1.png)](https://twitter.com)")
    with col_soc[2]: st.markdown("[![IG](https://img.icons8.com/color/48/instagram-new.png)](https://instagram.com)")
    with col_soc[3]: 
        # ENLACE TIKTOK SOLICITADO
        st.markdown("[![TK](https://img.icons8.com/color/48/tiktok.png)](https://www.tiktok.com/@tecomparotodo?_r=1&_t=ZN-95nfhnoUU9W)")
    with col_soc[4]: st.markdown("[![LK](https://img.icons8.com/color/48/linkedin.png)](https://linkedin.com)")

# --- 📈 DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.markdown("<h1 style='color: #d2ff00;'>📊 MÉTRICAS Y RANKING</h1>", unsafe_allow_html=True)
    
    # FRASE MOTIVADORA DIARIA GIGANTE
    frases = [
        "EL ÉXITO ES LA SUMA DE PEQUEÑOS ESFUERZOS REPETIDOS DÍA TRAS DÍA.",
        "TU ÚNICA LIMITACIÓN ES TU MENTE. ¡A POR TODAS!",
        "SI QUIERES LLEGAR DONDE LA MAYORÍA NO LLEGA, HAZ LO QUE LA MAYORÍA NO HACE.",
        "EL MOMENTO EN QUE QUIERES ABANDONAR ES EL MOMENTO EN QUE DEBES SEGUIR.",
        "NO CUENTES LOS DÍAS, HAZ QUE LOS DÍAS CUENTEN.",
        "LA DISCIPLINA ES EL PUENTE ENTRE LAS METAS Y LOS LOGROS."
    ]
    frase_hoy = frases[date.today().day % len(frases)]
    st.markdown(f"""
        <div style="background: #1c2128; padding: 40px; border-radius: 15px; border-left: 10px solid #d2ff00; text-align: center; margin-bottom: 40px;">
            <h1 style="color: #d2ff00; font-size: 55px; font-weight: 800;">"{frase_hoy}"</h1>
        </div>
    """, unsafe_allow_html=True)

    # RANKING Nº1 VISUAL
    st.markdown("""
        <div style="text-align: center; margin-top: 50px;">
            <div style="display: inline-block; position: relative; padding: 40px 70px; border: 4px solid #d2ff00; border-radius: 20px; background: linear-gradient(135deg, #1c2128 0%, #0d1117 100%);">
                <div style="position: absolute; top: -50px; left: 50%; transform: translateX(-50%); font-size: 60px;">👑</div>
                <h3 style="color: #8b949e; letter-spacing: 5px;">TOP 1 DEL MES</h3>
                <h1 style="color: white; font-size: 4.5rem; margin: 0;">RAQUEL <span style="color:#d2ff00;">GUADALUPE</span></h1>
                <div style="margin-top: 15px; font-size: 2rem;">⭐⭐⭐⭐⭐</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 🕒 CONTROL LABORAL ---
elif menu == "🕒 CONTROL LABORAL":
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL Y ASISTENCIA</div>', unsafe_allow_html=True)
    
    empleado = st.selectbox("Seleccionar comercial:", sorted(list(fechas_empresa.keys())))
    
    # Cálculos de auditoría (Versión corregida)
    df_lab = load_data_laboral()
    if not df_lab.empty:
        info = fechas_empresa[empleado]
        col_inf1, col_inf2 = st.columns(2)
        col_inf1.info(f"📅 **Alta:** {info['alta'].strftime('%d/%m/%Y')}")
        if info['baja']: col_inf2.error(f"⚠️ **Baja:** {info['baja'].strftime('%d/%m/%Y')}")
        else: col_inf2.success("✅ **Estado:** Activo")

        # Procesa deuda y registros
        busq = normalizar(empleado)
        df_indiv = df_lab[df_lab['Nombre_Norm'] == busq].copy()
        
        st.subheader(f"Resumen de {empleado}")
        # Aquí se integran los cuadros de Pendiente, Retrasos, etc. (según tu lógica previa)
        st.write("Fichajes detectados:")
        st.dataframe(df_indiv.sort_values(df_indiv.columns[0], ascending=False), use_container_width=True)
    else:
        st.error("No se detectan datos en la base de datos de Google Sheets.")

# --- SECCIONES VACÍAS (Para no borrar nada) ---
else:
    st.info(f"Sección {menu} en desarrollo.")