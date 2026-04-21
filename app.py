import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime, time, date
import calendar
import unicodedata
from fpdf import FPDF
from PIL import Image # Única línea añadida para que funcione el código de laboral

# 1. CONFIGURACIÓN (ORIGINAL)
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- FUNCIONES DE APOYO (ORIGINALES) ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

def normalizar(texto):
    if not isinstance(texto, str): return ""
    texto = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto if unicodedata.category(c) != 'Mn']).strip().upper()

# --- DATOS CONTROL LABORAL (INSERTADOS TAL CUAL) ---
festivos_2026 = ["2026-01-01", "2026-01-06", "2026-02-28", "2026-04-02", "2026-04-03", "2026-04-22", "2026-05-01", "2026-06-04", "2026-08-15", "2026-10-12", "2026-11-02", "2026-12-07", "2026-12-08", "2026-12-25"]
fechas_empresa = {
    'LUIS RODRÍGUEZ': {'alta': date(2026, 4, 8), 'baja': None},
    'RAQUEL GUADALUPE': {'alta': date(2026, 3, 19), 'baja': None},
    'LORENA POZO': {'alta': date(2026, 3, 18), 'baja': None},
    'DEBORAH RODRIGUEZ': {'alta': date(2026, 3, 18), 'baja': None},
    'BELÉN TRONCOSO': {'alta': date(2026, 3, 18), 'baja': None},
    'MACARENA BACA': {'alta': date(2026, 3, 18), 'baja': date(2026, 3, 20)}
}
excepciones_laboral = {
    'LORENA POZO': {date(2026, 4, 17): "Día libre por objetivo conseguido"}
}
recuperadas_manual = {'LORENA POZO': 2.0, 'BELÉN TRONCOSO': 3.33, 'DEBORAH RODRIGUEZ': 0.5}

@st.cache_data(ttl=5)
def load_data_laboral():
    url = "https://docs.google.com/spreadsheets/d/175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY/export?format=csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], dayfirst=True, errors='coerce')
        df['Nombre_Norm'] = df['¿Quién eres?'].apply(normalizar)
        df['Accion_Norm'] = df['¿Qué vas a hacer?'].astype(str).str.upper()
        df['Fecha'] = df['Marca temporal'].dt.date
        df['Hora_f'] = df['Marca temporal'].dt.time
        return df.dropna(subset=['Marca temporal'])
    except: return pd.DataFrame()

# Preparamos la imagen de Rosco (ORIGINAL)
img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD (ORIGINAL)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. MENU LATERAL (AÑADIDA OPCIÓN CONTROL LABORAL)
with st.sidebar:
    if os.path.exists("rosco.jpg"):
        st.image("rosco.jpg")
    else:
        st.title("BASETTE HUB")
    st.markdown("---")
    menu = st.radio(
        "NAVEGACIÓN",
        ["📊 DASHBOARD VENTAS", "🕒 CONTROL LABORAL", "📂 REPOSITORIO"],
        index=0
    )

# --- PESTAÑA 1: DASHBOARD VENTAS (ORIGINAL SIN CAMBIOS) ---
if menu == "📊 DASHBOARD VENTAS":
    st.title("🚀 Panel de Control de Ventas")
    try:
        sheet_id = "1nC_rA571-R5_x6S7Ube33W89pE3N3q9L2p5N7H-Yc8Q"
        url_v = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        dv = pd.read_csv(url_v)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL VENTAS", len(dv))
        c2.metric("FIBRA/MOVIL", len(dv[dv['Producto'].isin(['FIBRA', 'MOVIL', 'CONVERGENTE'])]))
        if 'V_Alarma' in dv.columns:
            c3.metric("ALARMAS", int(dv['V_Alarma'].sum()))
        else:
            c3.metric("ALARMAS", 0)
        c4.metric("ENERGÍA", len(dv[dv['Producto'] == 'LUZ/GAS']))
        t1, t2 = st.tabs(["Análisis por Comercial", "Ventas Alarmas"])
        with t1:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                fig_v = px.pie(dv, names='Comercial', title="Reparto de Ventas", hole=0.4)
                fig_v.update_traces(textposition='inside', textinfo='label+percent')
                st.plotly_chart(fig_v, use_container_width=True)
            with col_b2:
                fig_p = px.bar(dv, x='Producto', color='Comercial', title="Productos por Comercial", barmode='group')
                st.plotly_chart(fig_p, use_container_width=True)
        with t2:
            if 'V_Alarma' in dv.columns:
                da = dv[dv['V_Alarma'] > 0]
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    fig_a_pie = px.pie(da, names='Comercial', values='V_Alarma', title="% Alarmas por Comercial")
                    fig_a_pie.update_traces(textposition='outside', textinfo='label+percent')
                    st.plotly_chart(fig_a_pie, use_container_width=True)
                with col_a2:
                    if not da.empty:
                        fig_a_bar = px.bar(da.groupby('Comercial')['V_Alarma'].sum().reset_index().sort_values('V_Alarma'), x='V_Alarma', y='Comercial', orientation='h', text_auto=True, title="Ventas de Alarmas", color_discrete_sequence=['#0000FF']) 
                        st.plotly_chart(fig_a_bar, use_container_width=True)
    except Exception as e:
        st.error(f"Error cargando el Dashboard: {e}")

# --- PESTAÑA 2: CONTROL LABORAL (INSERTADO TAL CUAL) ---
elif menu == "🕒 CONTROL LABORAL":
    df_raw_lab = load_data_laboral()
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros Laboral")
    comercial_lab = st.sidebar.selectbox("Seleccionar Comercial", sorted(list(fechas_empresa.keys())))
    meses_lab = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_lab = st.sidebar.selectbox("Seleccionar Mes", meses_lab, index=datetime.now().month - 1)
    m_num = meses_lab.index(mes_lab) + 1

    dias_mes = [date(2026, m_num, d) for d in range(1, calendar.monthrange(2026, m_num)[1] + 1) 
                if date(2026, m_num, d).weekday() < 5 and date(2026, m_num, d).strftime("%Y-%m-%d") not in festivos_2026]
    df_lab_f = pd.DataFrame({'Fecha': dias_mes})

    def calc_lab(row):
        f = row['Fecha']
        info = fechas_empresa[comercial_lab]
        excep = excepciones_laboral.get(comercial_lab, {})
        dia_data = df_raw_lab[(df_raw_lab['Nombre_Norm'] == normalizar(comercial_lab)) & (df_raw_lab['Fecha'] == f)] if not df_raw_lab.empty else pd.DataFrame()
        fuera = f < info['alta'] or (info['baja'] and f >= info['baja'])
        v_h = 4.5 if (date(2026, 4, 20) <= f <= date(2026, 4, 26)) else (8.0 if comercial_lab == 'RAQUEL GUADALUPE' else 5.0)
        e, s = "-", "-"
        for _, r in dia_data.iterrows():
            if "ENTRADA" in r['Accion_Norm']: e = r['Hora_f']
            if "SALIDA" in r['Accion_Norm']: s = r['Hora_f']
        if f in excep: estado = excep[f]
        elif fuera: estado = "BAJA/NO ALTA"
        elif e == "-" and f <= date.today(): estado = "SI pendiente recuperar"
        else: estado = "-"
        ret = 0
        if estado == "-" and isinstance(e, time):
            h_ref = time(9,0) if v_h == 4.5 or comercial_lab == 'RAQUEL GUADALUPE' else time(9,30)
            diff = (e.hour*60 + e.minute) - (h_ref.hour*60 + h_ref.minute)
            if diff > 0: ret = diff
        return pd.Series([e.strftime("%H:%M") if isinstance(e, time) else "-", s.strftime("%H:%M") if isinstance(s, time) else "-", estado, ret, v_h, fuera])

    df_lab_f[['ENTRADA', 'SALIDA', 'AUSENCIA', 'MIN_RETRASO', 'Jornada_h', 'ES_BAJA']] = df_lab_f.apply(calc_lab, axis=1)
    h_aus = df_lab_f[df_lab_f['AUSENCIA'] == "SI pendiente recuperar"]['Jornada_h'].sum()
    h_ret = df_lab_f['MIN_RETRASO'].sum() / 60
    total_p = round(max(0.0, (h_aus + h_ret) - recuperadas_manual.get(comercial_lab, 0)), 2)

    col_l1, col_l2, col_l3 = st.columns([2, 3, 2.5])
    with col_l1:
        ruta_logo = r"C:\Users\Propietario\Desktop\MI_INTRANET\tecomparotodo_logo.jpg"
        if os.path.exists(ruta_logo): st.image(Image.open(ruta_logo), width=220)
    with col_l2:
        st.markdown(f"<h1 style='text-align: center; color: #d2ff00;'>{comercial_lab}</h1>", unsafe_allow_html=True)
    with col_l3:
        st.markdown(f"""<div style="border: 4px solid #FF0000; border-radius: 10px; padding: 15px; background-color: #FFF5F5; text-align: center;">
            <p style="margin: 0; color: #FF0000; font-size: 1.1em; font-weight: bold;">⚠️ HORAS A RECUPERAR</p>
            <p style="margin: 5px 0 0 0; color: #000000; font-size: 2.2em; font-weight: 900;">{total_p} h</p>
            </div>""", unsafe_allow_html=True)
    st.divider()
    def style_lab(data):
        style_df = pd.DataFrame('', index=data.index, columns=data.columns)
        for i, row in data.iterrows():
            c = ""
            aus = str(row['AUSENCIA'])
            if "objetivo" in aus.lower(): c = "background-color: #dcfce7; color: #166534"
            elif row['ES_BAJA']: c = "background-color: #333; color: #999"
            elif "SI" in aus: c = "background-color: #fee2e2; color: #991b1b"
            elif row['MIN_RETRASO'] > 0: c = "background-color: #fef9c3; color: #000"
            if c: style_df.loc[i, :] = c
        return style_df
    df_view = df_lab_f.copy()
    df_view['Retraso'] = df_view['MIN_RETRASO'].apply(lambda x: f"{int(x)} min" if x > 0 else "-")
    df_view['Jornada'] = df_view['Jornada_h'].map('{:,.1f}h'.format)
    st.dataframe(df_view[['Fecha', 'ENTRADA', 'SALIDA', 'AUSENCIA', 'Retraso', 'Jornada', 'ES_BAJA', 'MIN_RETRASO']].style.apply(style_lab, axis=None), column_config={"ES_BAJA": None, "MIN_RETRASO": None}, use_container_width=True, hide_index=True)

# --- PESTAÑA 3: REPOSITORIO (ORIGINAL SIN CAMBIOS) ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 MANUAL DEL MARCADOR"):
        manual_path = "manuales/Manual_Premiumnumber_Agente.pdf"
        if os.path.exists(manual_path):
            with open(manual_path, "rb") as f:
                st.download_button("📖 DESCARGAR MANUAL", f, file_name="Manual_Marcador.pdf")
    st.markdown("---")
    with st.expander("📁 DOCUMENTACIÓN LOWI"):
        archivo_lowi = "manuales/TARIFAS_LOWI_MARZO2026.pdf"
        if os.path.exists(archivo_lowi):
             with open(archivo_lowi, "rb") as f:
                st.download_button("📄 TARIFAS LOWI", f, file_name="Tarifas_Lowi.pdf")