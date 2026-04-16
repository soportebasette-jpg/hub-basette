import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime, time, timedelta
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Función para convertir imagen a base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p { color: #d2ff00 !important; font-weight: 900 !important; font-size: 1.25rem !important; }
    button p, .stDownloadButton button p, .stButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button, .stButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    .block-header { background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem; }
    .winner-card { background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 25px; border-radius: 15px; color: white !important; text-align: center; font-weight: bold; font-size: 28px; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    .social-container { display: flex; justify-content: flex-end; align-items: center; gap: 20px; padding: 10px; }
    .social-icon { transition: transform 0.3s; }
    .social-icon:hover { transform: scale(1.1); }
    .price-card { background-color: #161b22; border: 2px solid #30363d; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px; transition: transform 0.3s; height: 100%; }
    .price-card:hover { border-color: #d2ff00; transform: translateY(-5px); }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.85rem; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")
URL_CONTROL = get_csv_url("https://docs.google.com/spreadsheets/d/175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    df_e = pd.read_csv(URL_ENE); df_e.columns = df_e.columns.str.strip()
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    df_e['REF_Ene'] = df_e['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_e.columns else 0
    
    df_t = pd.read_csv(URL_TEL); df_t.columns = df_t.columns.str.strip()
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    def get_telco_metrics(row):
        f, m = 0, 0
        t = str(row.get('Tipo Tarifa', '')).lower()
        if 'fibramovil' in t or ('fibra' in t and 'movil' in t): f, m = 1, 1
        elif 'fibra' in t: f = 1
        elif 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return f, m, (f + m)
    res = df_t.apply(get_telco_metrics, axis=1)
    df_t['V_Fibra'] = res.apply(lambda x: x[0]); df_t['V_Móvil'] = res.apply(lambda x: x[1]); df_t['Total_Tel'] = res.apply(lambda x: x[2])
    df_t['REF_Tel'] = df_t['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_t.columns else 0

    df_a = pd.read_csv(URL_ALA); df_a.columns = df_a.columns.str.strip()
    df_a['Fecha Creación'] = pd.to_datetime(df_a['Fecha Creación'], dayfirst=True, errors='coerce')
    df_a = df_a.dropna(subset=['Comercial', 'Fecha Creación'])
    df_a['Año'] = df_a['Fecha Creación'].dt.year.astype(str); df_a['Mes'] = df_a['Fecha Creación'].dt.strftime('%m - %B')
    df_a['V_Alarma'] = 1 
    df_a['REF_Ala'] = df_a['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_a.columns else 0
    return df_e, df_t, df_a

# --- BASE DE DATOS PRECIOS ACTUALIZADA ---
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.119, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,171/0,104/0,08", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
]

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
QR_PLAN_AMIGO = "anunciosbasette/qr-plan amigo.png"

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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "⏱️ CONTROL LABORAL", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- CRM ---
if menu == "🚀 CRM":
    col_t_izq, col_t_der = st.columns([2, 1])
    with col_t_izq: st.header("Portales de Gestión")
    with col_t_der:
        st.markdown(f"""<div class="social-container">
            <a href="https://www.facebook.com/share/1CqrZ4hGYp/?mibextid=wwXIfr" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" width="35" class="social-icon"></a>
            <a href="https://x.com/tecomparotodoes?s=21" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" width="35" class="social-icon"></a>
            <a href="https://www.instagram.com/tecomparotodoes?igsh=MXRkcTV2anJ6NmJkcA%3D%3D&utm_source=qr" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" width="35" class="social-icon"></a>
            <a href="http://www.tecomparotodo.es" target="_blank"><img src="data:image/jpeg;base64,{img_base64}" width="100" style="border-radius:8px; border: 2px solid #d2ff00;" class="social-icon"></a>
        </div>""", unsafe_allow_html=True)
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.link_button(f"REGISTRO DE JORNADA (FORMULARIO)", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, {"n": "NIBA", "u": "https://clientes.niba.es/"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]: st.link_button(p["n"], p["u"], use_container_width=True)

# --- PRECIOS (ACTUALIZADOS) ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        df_precios = pd.DataFrame(tarifas_luz).drop(columns=['logo'])
        st.dataframe(df_precios, use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([{"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"}, {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"}])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.write("Ver tarifas O2 y Fibra en el repositorio.")

# --- COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre", "Cliente")
        f_act = st.number_input("Factura actual (€)", value=0.0)
        consumo = st.number_input("Consumo (kWh)", value=0.0)
    with c2:
        comp_sel = st.selectbox("Compañía", sorted(list(set(t["COMPAÑÍA"] for t in tarifas_luz))))
        tarifa_sel_nombre = st.selectbox("Tarifa", [t["TARIFA"] for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel])
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tarifa_sel_nombre)
    p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    coste_total = (consumo * p_calc) * 1.21
    st.success(f"Ahorro Estimado: {f_act - coste_total:.2f} €")

# --- ANUNCIOS ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios")
    if os.path.exists(QR_PLAN_AMIGO): st.image(QR_PLAN_AMIGO, width=200)
    st.link_button("FORMULARIO PLAN AMIGO", "https://forms.gle/mU6XzRvywDoBQ5Q47")

# --- DASHBOARD RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.header("Ranking de Ventas")
    try:
        de, dt, da = load_and_clean_ranking()
        re = de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum()
        st.table(re)
    except: st.error("Error al cargar datos de ventas.")

# --- CONTROL LABORAL (NUEVO DASHBOARD) ---
elif menu == "⏱️ CONTROL LABORAL":
    st.header("📊 Dashboard de Control Laboral")
    
    # 1. Definir Horarios por Comercial (según imagen)
    # Formato: { 'Nombre': (hora_entrada, hora_salida) }
    HORARIOS = {
        'ANA BELEN': (time(9,0), time(15,0)),
        'ALVARO': (time(9,30), time(15,30)),
        'JUAN MANUEL': (time(9,30), time(15,30)),
        'MARIA': (time(10,0), time(14,0)),
        'JOSE ANTONIO': (time(10,0), time(14,0)),
        'RAFAEL': (time(10,0), time(14,0)),
        'FRANCISCO': (time(10,0), time(14,0))
    }
    
    # Festivos Sevilla 2026 (Ejemplo solicitado: Semana de Feria 20-26 Abril)
    FESTIVOS = ['2026-01-01', '2026-01-06', '2026-04-02', '2026-04-03', 
                '2026-04-20', '2026-04-21', '2026-04-22', '2026-04-23', '2026-04-24']

    try:
        df_c = pd.read_csv(URL_CONTROL)
        df_c.columns = ['Marca temporal', 'Comercial', 'Accion']
        df_c['Marca temporal'] = pd.to_datetime(df_c['Marca temporal'], dayfirst=True)
        df_c['Fecha'] = df_c['Marca temporal'].dt.date
        df_c['Hora'] = df_c['Marca temporal'].dt.time
        df_c['Mes'] = df_c['Marca temporal'].dt.strftime('%m - %B')
        
        # Eliminar fines de semana y festivos
        df_c = df_c[df_c['Marca temporal'].dt.weekday < 5]
        df_c = df_c[~df_c['Fecha'].astype(str).isin(FESTIVOS)]

        # Filtros
        colf1, colf2 = st.columns(2)
        with colf1:
            mes_sel = st.selectbox("Seleccionar Mes", sorted(df_c['Mes'].unique()), index=len(df_c['Mes'].unique())-1)
        with colf2:
            com_sel = st.multiselect("Comercial", df_c['Comercial'].unique(), default=df_c['Comercial'].unique())
        
        df_f = df_c[(df_c['Mes'] == mes_sel) & (df_c['Comercial'].isin(com_sel))]

        # Cálculo de Retrasos y Ausencias
        res_list = []
        for comercial in com_sel:
            df_user = df_f[df_f['Comercial'] == comercial]
            entradas = df_user[df_user['Accion'].str.contains('ENTRADA', case=False)]
            ausencias = df_user[df_user['Accion'].str.contains('AUSENCIA', case=False)].shape[0]
            
            retrasos_min = 0
            cont_retrasos = 0
            
            if comercial in HORARIOS:
                h_teorica = HORARIOS[comercial][0]
                for _, row in entradas.iterrows():
                    h_real = row['Hora']
                    # Convertir a datetime para restar
                    dt_real = datetime.combine(datetime.today(), h_real)
                    dt_teorica = datetime.combine(datetime.today(), h_teorica)
                    
                    if dt_real > dt_teorica + timedelta(minutes=5): # Margen 5 min
                        diff = (dt_real - dt_teorica).seconds / 60
                        retrasos_min += diff
                        cont_retrasos += 1
            
            res_list.append({
                'Comercial': comercial,
                'Días Fichados': df_user['Fecha'].nunique(),
                'Retrasos Totales': cont_retrasos,
                'Minutos Retraso': int(retrasos_min),
                'Ausencias/Permisos': ausencias
            })
        
        df_res = pd.DataFrame(res_list)
        
        # Visualización
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Resumen Mensual")
            st.dataframe(df_res, hide_index=True, use_container_width=True)
        with c2:
            fig_ret = px.bar(df_res, x='Comercial', y='Minutos Retraso', color='Retrasos Totales', title="Minutos de Retraso Acumulados")
            st.plotly_chart(fig_ret, use_container_width=True)
            
        st.markdown("---")
        st.subheader("Registro Detallado")
        st.write(df_f.sort_values('Marca temporal', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Error al conectar con el Drive de Control Laboral. Verifica el enlace y permisos. Detalles: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📁 DOCUMENTACIÓN LOWI"):
        archivo_lowi = "manuales/TARIFAS_LOWI_MARZO2026.pdf"
        if os.path.exists(archivo_lowi):
            with open(archivo_lowi, "rb") as f: st.download_button("Descargar Tarifas Lowi", f)