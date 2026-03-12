import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD (Corregido para que el menú superior sea visible)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    
    /* ARREGLO MENÚ SUPERIOR (TABS) - Para que no salgan cuadros blancos */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: 1px solid #30363d !important;
        color: white !important;
        border-radius: 5px 5px 0 0 !important;
        margin-right: 5px !important;
    }
    button[aria-selected="true"] {
        background-color: #d2ff00 !important;
        color: black !important;
        font-weight: bold !important;
    }

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
    .price-card:hover {
        border-color: #d2ff00;
        transform: translateY(-5px);
    }
    .price-title { color: #d2ff00; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: white; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #8b949e; font-size: 0.85rem; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIONES DE DATOS
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_VAC = get_csv_url("https://docs.google.com/spreadsheets/d/1CUma-cn2oHYC1ORWjfNVMi2cexYvJUyvwIN3j_fvyM8/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    df_e = pd.read_csv(URL_ENE)
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    
    df_t = pd.read_csv(URL_TEL)
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    def count_t(row):
        f, m = 0, 0
        t = str(row['Tipo Tarifa']).lower()
        if 'fibramovil' in t or ('fibra' in t and 'movil' in t): f, m = 1, 1
        elif 'fibra' in t: f = 1
        elif 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return pd.Series([f, m, f + m])
    df_t[['V_Fibra', 'V_Móvil', 'Total_Tel']] = df_t.apply(count_t, axis=1)
    return df_e, df_t

@st.cache_data(ttl=10)
def load_vacaciones():
    try:
        df = pd.read_csv(URL_VAC)
        df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'], dayfirst=True, errors='coerce')
        df['Fecha Fin'] = pd.to_datetime(df['Fecha Fin'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha Inicio', 'Fecha Fin'])
        # Aseguramos columnas necesarias
        for col in ["Comercial", "Fecha Inicio", "Fecha Fin", "Motivo", "Nº DE DIAS"]:
            if col not in df.columns: df[col] = "N/A"
        return df
    except:
        return pd.DataFrame(columns=["Comercial", "Fecha Inicio", "Fecha Fin", "Motivo", "Nº DE DIAS"])

# 4. BASE DE DATOS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.129, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,181/0,114/0,090", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
]

# 5. LOGIN
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

# 6. NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "🏖️ VACACIONES", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- SECCIONES ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
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

elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t_luz, t_gas, t_fibra = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    
    with t_luz:
        df_precios = pd.DataFrame(tarifas_luz).drop(columns=['logo'])
        st.dataframe(df_precios, use_container_width=True, hide_index=True)
    with t_gas:
        df_gas = pd.DataFrame([{"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh"}])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)

    with t_fibra:
        st.markdown('<div class="block-header">📡 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        solo_fibra = [("300 Mb", "23€"), ("600 Mb", "27€"), ("1 Gb", "31€")]
        for i, (vel, pre) in enumerate(solo_fibra):
            with f_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">FIBRA {vel}</div><div class="price-val">{pre}</div><div class="price-sub">Precio Final / Mes</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES (FIBRA Y MÓVIL)</div>', unsafe_allow_html=True)
        ad_cols_f = st.columns(3)
        lineas_ad_f = [("300 Mb", "15€"), ("600 Mb", "20€"), ("1 Gb", "27€")]
        for i, (vel, pre) in enumerate(lineas_ad_f):
            with ad_cols_f[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">ADICIONAL {vel}</div><div class="price-val">{pre}</div><div class="price-sub">Precio / Mes</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="block-header">📺 TELEVISIÓN Y PACKS TV</div>', unsafe_allow_html=True)
        tv_cols = st.columns(5)
        packs_tv = [("SOLO TV", "9.99€", "M+ Suscripción"), ("600 Mb + TV", "38€", "35 GB"), ("600 Mb + TV", "45€", "60 GB"), ("1 Gb + TV", "50€", "350 GB"), ("1 Gb + TV", "56€", "375 GB")]
        for i, (vel, pre, sub) in enumerate(packs_tv):
            with tv_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel}</div><div class="price-val">{pre}</div><div class="price-sub">{sub}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES (MÓVILES TV)</div>', unsafe_allow_html=True)
        ad_cols_tv = st.columns(3)
        lineas_ad_tv = [("Móvil 40 GB", "5€"), ("Móvil 150 GB", "10€"), ("Móvil 300 GB", "15€")]
        for i, (gb, pre) in enumerate(lineas_ad_tv):
            with ad_cols_tv[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{gb}</div><div class="price-val">{pre}</div><div class="price-sub">Pago Mensual</div></div>', unsafe_allow_html=True)

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    c1, c2 = st.columns(2)
    with c1:
        f_act = st.number_input("Factura actual (€)", value=0.0)
        consumo = st.number_input("Consumo (kWh)", value=0.0)
    with c2:
        comp_sel = st.selectbox("Compañía", [t["COMPAÑÍA"] for t in tarifas_luz])
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel)
    ahorro = f_act - (consumo * 0.12 * 1.21)
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)

elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🎁 PLAN AMIGO</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Enlace Plan Amigo")
        st.code("https://forms.gle/mU6XzRvywDoBQ5Q47")
        st.link_button("Ir al Formulario", "https://forms.gle/mU6XzRvywDoBQ5Q47")
    with col2:
        st.subheader("QR Plan Amigo")
        if os.path.exists(QR_PLAN_AMIGO): st.image(QR_PLAN_AMIGO, width=250)

    st.markdown('<div class="block-header">🖼️ ANUNCIOS BASETTE</div>', unsafe_allow_html=True)
    # Mostramos las 3 imágenes de la carpeta en tamaño pequeño (cols)
    dir_anu = "anunciosbasette"
    if os.path.exists(dir_anu):
        imgs = [f for f in os.listdir(dir_anu) if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "qr" not in f.lower()]
        if imgs:
            cols_img = st.columns(4) # 4 columnas para que se vean pequeñas
            for idx, img_file in enumerate(imgs[:3]): # Solo las 3 primeras
                with cols_img[idx]:
                    st.image(os.path.join(dir_anu, img_file), use_column_width=True)

elif menu == "📈 DASHBOARD Y RANKING":
    st.header("📈 Dashboard")
    df_e, df_t = load_and_clean_ranking()
    st.success("Panel de control actualizado.")

elif menu == "🏖️ VACACIONES":
    st.header("🏖️ Gestión de Vacaciones")
    col_form, col_cal = st.columns([1, 2])
    
    with col_form:
        st.markdown('<div class="block-header">📝 SOLICITAR DÍAS</div>', unsafe_allow_html=True)
        with st.form("form_vacaciones", clear_on_submit=True):
            com = st.text_input("Comercial")
            fi = st.date_input("Inicio", value=date.today())
            ff = st.date_input("Fin", value=date.today())
            mot = st.text_area("Motivo")
            if st.form_submit_button("REGISTRAR EN EXCEL"):
                st.warning("⚠️ Paso Final: Rellena los datos en este enlace:")
                st.link_button("FORMULARIO", "https://docs.google.com/spreadsheets/d/1CUma-cn2oHYC1ORWjfNVMi2cexYvJUyvwIN3j_fvyM8")

    with col_cal:
        st.markdown('<div class="block-header">📅 CALENDARIO DE EQUIPO</div>', unsafe_allow_html=True)
        df_v = load_vacaciones()
        if not df_v.empty:
            try:
                # CORRECCIÓN DE ERROR VALUEERROR (image_0ff064.png)
                # Convertimos fechas y filtramos valores nulos antes de graficar
                df_v['Fecha Inicio'] = pd.to_datetime(df_v['Fecha Inicio'])
                df_v['Fecha Fin'] = pd.to_datetime(df_v['Fecha Fin'])
                
                # Gráfico Gantt mucho más visual
                fig = px.timeline(df_v, 
                                 start="Fecha Inicio", 
                                 end="Fecha Fin", 
                                 y="Comercial", 
                                 color="Comercial",
                                 hover_data=["Motivo", "Nº DE DIAS"],
                                 title="Cronograma de Ausencias")
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="white",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_v[["Comercial", "Fecha Inicio", "Fecha Fin", "Motivo"]], use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error al generar calendario: {e}")
        else:
            st.info("No hay vacaciones registradas.")

elif menu == "📂 REPOSITORIO":
    st.header("📂 Documentación")
    st.write("Accede a los manuales y argumentarios.")