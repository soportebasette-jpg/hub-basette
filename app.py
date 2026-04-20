import streamlit as st
import os
import pandas as pd
import plotly.express as px
import base64
import calendar
import unicodedata
from datetime import datetime, time, date

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Función para normalizar nombres
def normalizar(texto):
    if not isinstance(texto, str): return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
    return texto.strip().upper()

# Función para convertir imagen a base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1117; color: #ffffff; }}
    header {{ visibility: hidden; }}
    label[data-testid="stWidgetLabel"] p {{
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }}
    /* Estilos para el Control Laboral */
    .metric-card {{
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATOS CONTROL LABORAL ---
festivos_2026 = ["2026-01-01", "2026-01-06", "2026-02-28", "2026-04-02", "2026-04-03", "2026-04-22", "2026-05-01", "2026-06-04", "2026-08-15", "2026-10-12", "2026-11-02", "2026-12-07", "2026-12-08", "2026-12-25"]
vacaciones_junio = [date(2026, 6, d) for d in range(22, 29)]

fechas_empresa = {
    'LUIS RODRÍGUEZ': {'alta': date(2026, 4, 8), 'baja': None},
    'RAQUEL GUADALUPE': {'alta': date(2026, 3, 19), 'baja': None},
    'LORENA POZO': {'alta': date(2026, 3, 18), 'baja': None},
    'DEBORAH RODRIGUEZ': {'alta': date(2026, 3, 18), 'baja': None},
    'BELÉN TRONCOSO': {'alta': date(2026, 3, 18), 'baja': None},
    'MACARENA BACA': {'alta': date(2026, 3, 18), 'baja': date(2026, 3, 20)}
}

excepciones_laborales = {
    'LORENA POZO': {date(2026, 4, 17): "Día libre por objetivo conseguido"},
    'BELÉN TRONCOSO': {date(2026, 4, 17): "SI pendiente recuperar"},
    'LUIS RODRÍGUEZ': {date(2026, 4, 16): "SI pendiente recuperar"}
}

@st.cache_data(ttl=5)
def load_laboral_data():
    file_id = "175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
    try:
        df = pd.read_csv(sheet_url)
        df.columns = [c.strip() for c in df.columns]
        df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], dayfirst=True, errors='coerce')
        df['Nombre_Norm'] = df['¿Quién eres?'].apply(normalizar)
        df['Accion_Norm'] = df['¿Qué vas a hacer?'].astype(str).str.upper()
        df['Fecha_f'] = df['Marca temporal'].dt.date
        df['Hora_f'] = df['Marca temporal'].dt.time
        return df.dropna(subset=['Marca temporal'])
    except:
        return pd.DataFrame()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("rosco.jpg", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #d2ff00;'>BASSETTE GROUP</h2>", unsafe_allow_html=True)
    menu = st.radio(
        "NAVEGACIÓN",
        ["🏠 INICIO", "📊 DASHBOARD", "📅 CONTROL LABORAL", "📂 REPOSITORIO"],
        index=0
    )

# --- 5. LÓGICA DE PÁGINAS ---

# --- INICIO ---
if menu == "🏠 INICIO":
    st.title("Bienvenido al Hub")
    st.write("Selecciona una opción en el menú lateral para comenzar.")

# --- DASHBOARD (TU CÓDIGO ORIGINAL) ---
elif menu == "📊 DASHBOARD":
    st.title("Dashboard de Ventas")
    # (Aquí iría el contenido de tu dashboard que ya tienes en app.py)
    st.info("Carga aquí la lógica de tus gráficas de Google Sheets.")

# --- CONTROL LABORAL (NUEVA PESTAÑA) ---
elif menu == "📅 CONTROL LABORAL":
    st.markdown("<h1 style='color: #d2ff00;'>Control de Jornada Laboral</h1>", unsafe_allow_html=True)
    
    df_lab = load_laboral_data()
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        comercial_lab = st.selectbox("👤 Comercial", sorted(list(fechas_empresa.keys())))
    with col_sel2:
        meses_lab = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_lab_sel = st.selectbox("📅 Mes", meses_lab, index=3) # Abril
        m_num = meses_lab.index(mes_lab_sel) + 1

    # Procesamiento de días
    num_dias = calendar.monthrange(2026, m_num)[1]
    dias_mes = [date(2026, m_num, d) for d in range(1, num_dias + 1) 
                if date(2026, m_num, d).weekday() < 5 and date(2026, m_num, d).strftime("%Y-%m-%d") not in festivos_2026]
    
    df_final_lab = pd.DataFrame({'Fecha': dias_mes})
    nombre_norm_sel = normalizar(comercial_lab)
    df_com_lab = df_lab[df_lab['Nombre_Norm'] == nombre_norm_sel] if not df_lab.empty else pd.DataFrame()

    def procesar_fila_lab(row):
        f = row['Fecha']
        info = fechas_empresa.get(comercial_lab)
        datos_dia = df_com_lab[df_com_lab['Fecha_f'] == f] if not df_com_lab.empty else pd.DataFrame()
        
        es_baja = f < info['alta'] or (info['baja'] is not None and f >= info['baja'])
        es_vaca = (f in vacaciones_junio)
        
        entrada, salida = "-", "-"
        if not datos_dia.empty:
            for _, r in datos_dia.iterrows():
                if "ENTRADA" in r['Accion_Norm']: entrada = r['Hora_f']
                if "SALIDA" in r['Accion_Norm']: salida = r['Hora_f']

        # Horarios Especiales
        if (date(2026, 4, 20) <= f <= date(2026, 4, 26)): # Semana Feria
            h_ini, h_fin = time(9, 0), time(13, 30)
        elif (date(2026, 3, 30) <= f < date(2026, 4, 20)): # Feria antigua / SS
            h_ini, h_fin = time(9, 30), time(13, 30)
        elif comercial_lab == 'RAQUEL GUADALUPE':
            h_ini, h_fin = time(9, 0), time(14, 30)
        else:
            h_ini, h_fin = time(9, 30), time(14, 30)

        # Estado y Excepciones
        hoy = date.today()
        excep_com = excepciones_laborales.get(comercial_lab, {})
        
        if f in excep_com:
            estado = excep_com[f]
        elif es_baja: estado = "BAJA/NO ALTA"
        elif es_vaca: estado = "VACACIONES"
        elif entrada == "-" and salida == "-" and f <= hoy: estado = "SI pendiente recuperar"
        else: estado = "-"
        
        retraso = 0
        if estado == "-" and isinstance(entrada, time):
            e_m = entrada.hour * 60 + entrada.minute
            i_m = h_ini.hour * 60 + h_ini.minute
            if e_m > i_m: retraso = e_m - i_m

        return pd.Series([
            entrada.strftime("%H:%M") if isinstance(entrada, time) else "-",
            salida.strftime("%H:%M") if isinstance(salida, time) else "-",
            estado, retraso, f"{h_ini.strftime('%H:%M')} - {h_fin.strftime('%H:%M')}", es_baja
        ])

    df_final_lab[['ENTRADA', 'SALIDA', 'AUSENCIA', 'MIN_RETRASO', 'HORARIO', 'ES_BAJA']] = df_final_lab.apply(procesar_fila_lab, axis=1)

    # KPIs
    k1, k2, k3 = st.columns(3)
    with k1: st.metric("Ausencias/Pendientes", len(df_final_lab[df_final_lab['AUSENCIA'].str.contains("SI", na=False)]))
    with k2: st.metric("Minutos Retraso", int(df_final_lab['MIN_RETRASO'].sum()))
    with k3: st.metric("Vacaciones", len(df_final_lab[df_final_lab['AUSENCIA'] == "VACACIONES"]))

    # Tabla con estilo
    def style_lab(row):
        val = str(row['AUSENCIA'])
        if "objetivo" in val.lower(): return ['background-color: #1b4332; color: #d4edda'] * len(row)
        if row['ES_BAJA']: return ['color: #555; background-color: #161b22'] * len(row)
        if val == "VACACIONES": return ['background-color: #0d3049; color: #e7f3ff'] * len(row)
        if "pendiente" in val: return ['background-color: #4c1d24; color: #f8d7da'] * len(row)
        if row['MIN_RETRASO'] > 0: return ['background-color: #4a3701; color: #fff3cd'] * len(row)
        return [''] * len(row)

    df_view_lab = df_final_lab.copy()
    df_view_lab['Retraso'] = df_view_lab['MIN_RETRASO'].apply(lambda x: f"{int(x)} min" if x > 0 else "-")
    
    st.dataframe(
        df_view_lab[['Fecha', 'ENTRADA', 'SALIDA', 'AUSENCIA', 'Retraso', 'HORARIO']].style.apply(style_lab, axis=1),
        use_container_width=True, hide_index=True
    )

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación y Manuales")
    # (Aquí va tu lógica de descarga de PDFs original)
    st.write("Archivos disponibles para descarga.")