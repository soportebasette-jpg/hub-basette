import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD (RESTURADO Y MEJORADO)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    button p { color: #000000 !important; font-weight: 900 !important; }
    
    /* Contenedor de Ranking para que no se peguen los datos */
    .ranking-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        color: black;
        margin-top: 20px;
    }
    
    .block-header {
        background-color: #d2ff00; color: black; padding: 8px 20px; border-radius: 5px;
        font-weight: bold; margin-bottom: 20px; margin-top: 25px; display: inline-block; font-size: 1.1rem;
    }
    
    .winner-card { 
        background: linear-gradient(90deg, #1e3a8a, #3b82f6); 
        padding: 20px; 
        border-radius: 15px; 
        color: white !important; 
        text-align: center; 
        font-weight: bold; 
        font-size: 24px; 
        margin-bottom: 25px;
    }

    .price-card {
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    # ENERGÍA
    df_e = pd.read_csv(URL_ENE)
    df_e.columns = df_e.columns.str.strip()
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    # CORRECCIÓN REF: Busca la palabra exacta REF sin importar mayúsculas o espacios
    df_e['REF_Ene'] = df_e['Canal'].astype(str).str.upper().str.strip().apply(lambda x: 1 if "REF" in x else 0) if 'Canal' in df_e.columns else 0
    
    # TELCO
    df_t = pd.read_csv(URL_TEL)
    df_t.columns = df_t.columns.str.strip()
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    df_t['REF_Tel'] = df_t['Canal'].astype(str).str.upper().str.strip().apply(lambda x: 1 if "REF" in x else 0) if 'Canal' in df_t.columns else 0
    
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
    df_t['V_Fibra'], df_t['V_Móvil'], df_t['Total_Tel'] = zip(*res)

    # ALARMAS
    df_a = pd.read_csv(URL_ALA)
    df_a.columns = df_a.columns.str.strip()
    df_a['Fecha Creación'] = pd.to_datetime(df_a['Fecha Creación'], dayfirst=True, errors='coerce')
    df_a = df_a.dropna(subset=['Comercial', 'Fecha Creación'])
    df_a['Año'] = df_a['Fecha Creación'].dt.year.astype(str)
    df_a['Mes'] = df_a['Fecha Creación'].dt.strftime('%m - %B')
    df_a['V_Alarma'] = 1 
    df_a['REF_Ala'] = df_a['Canal'].astype(str).str.upper().str.strip().apply(lambda x: 1 if "REF" in x else 0) if 'Canal' in df_a.columns else 0
    
    return df_e, df_t, df_a

# 3. BASE DE DATOS LUZ
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- SECCIONES CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.link_button(f"REGISTRO DE JORNADA", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [{"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, {"n": "GAS TOTAL", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, {"n": "LUZ TOTAL", "u": "https://agentes.totalenergies.es/#/resumen"}, {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, {"n": "NIBA", "u": "https://clientes.niba.es/"}, {"n": "ENDESA", "u": "https://inergia.app"}]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">{p["n"]}</h4></div>''', unsafe_allow_html=True)
            st.link_button(f"ENTRAR", p["u"], use_container_width=True)

elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        st.dataframe(pd.DataFrame(tarifas_luz).drop(columns=['logo']), use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([{"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"}])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro")
    st.info("Utiliza esta herramienta para comparar facturas de clientes.")

elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    if os.path.exists(QR_PLAN_AMIGO): st.image(QR_PLAN_AMIGO, width=250)

# --- DASHBOARD Y RANKING (CORREGIDO) ---
elif menu == "📈 DASHBOARD Y RANKING":
    st.header("📊 Dashboard y Ranking")
    try:
        df_e, df_t, df_a = load_and_clean_ranking()
        
        c_filt_1, c_filt_2, c_filt_3 = st.columns(3)
        anos = sorted(list(set(df_e['Año']) | set(df_t['Año']) | set(df_a['Año'])))
        meses = sorted(list(set(df_e['Mes']) | set(df_t['Mes']) | set(df_a['Mes'])))
        comerciales_lista = sorted(list(set(df_e['Comercial']) | set(df_t['Comercial']) | set(df_a['Comercial'])))
        
        with c_filt_1: f_ano = st.selectbox("📅 Año", anos, index=len(anos)-1)
        with c_filt_2: f_mes = st.selectbox("📆 Mes", meses, index=len(meses)-1)
        with c_filt_3: f_com = st.multiselect("👤 Comerciales", options=comerciales_lista, default=comerciales_lista)

        de = df_e[(df_e['Año'] == f_ano) & (df_e['Mes'] == f_mes) & (df_e['Comercial'].isin(f_com))]
        dt = df_t[(df_t['Año'] == f_ano) & (df_t['Mes'] == f_mes) & (df_t['Comercial'].isin(f_com))]
        da = df_a[(df_a['Año'] == f_ano) & (df_a['Mes'] == f_mes) & (df_a['Comercial'].isin(f_com))]

        tab_r, tab_e, tab_t, tab_a = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

        with tab_r:
            re = de.groupby('Comercial')[['V_Luz', 'V_Gas', 'REF_Ene']].sum()
            rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'REF_Tel']].sum()
            ra = da.groupby('Comercial')[['V_Alarma', 'REF_Ala']].sum()
            
            rank = pd.concat([re, rt, ra], axis=1).fillna(0)
            
            rank['TOTAL'] = rank['V_Luz'] + rank['V_Gas'] + rank['V_Fibra'] + rank['V_Alarma']
            rank['T+M'] = rank['TOTAL'] + rank['V_Móvil']
            rank['REF'] = rank['REF_Ene'] + rank['REF_Tel'] + rank['REF_Ala']
            rank['OBJ'] = 25
            rank['OBJ REF'] = 8
            rank['FALTA'] = (rank['OBJ'] - rank['TOTAL']).clip(lower=0)
            rank['%'] = ((rank['TOTAL'] / rank['OBJ']) * 100).fillna(0).astype(int)

            rank = rank.sort_values('TOTAL', ascending=False)

            if not rank.empty:
                ganador = rank.index[0]
                total_ganador = int(rank.iloc[0]['TOTAL'])
                st.markdown(f"""<div class="winner-card">👑 #1: {ganador.upper()} ({total_ganador} VENTAS SIN MÓVIL)</div>""", unsafe_allow_html=True)
                
                # ESTILO SEMÁFORO
                def semaforo_total(val):
                    if val >= 25: color = '#90EE90'
                    elif val >= 15: color = '#FFFFE0'
                    else: color = '#FFCCCB'
                    return f'background-color: {color}; color: black; font-weight: bold; border: 1px solid #ccc;'

                def semaforo_falta(val):
                    if val == 0: color = '#90EE90'
                    elif val <= 10: color = '#FFFFE0'
                    else: color = '#FFCCCB'
                    return f'background-color: {color}; color: black; font-weight: bold; border: 1px solid #ccc;'

                def semaforo_perc(val):
                    v = int(str(val).replace('%',''))
                    if v >= 100: color = '#90EE90'
                    elif v >= 60: color = '#FFFFE0'
                    else: color = '#FFCCCB'
                    return f'background-color: {color}; color: black; font-weight: bold; border: 1px solid #ccc;'

                rank_visual = rank.reset_index()
                rank_visual.insert(0, 'Pos', [("🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "⭐") for i in range(len(rank_visual))])
                
                # RENOMBRAR PARA TABLA
                df_tab = rank_visual[['Pos', 'Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Móvil', 'V_Alarma', 'TOTAL', 'T+M', 'OBJ', 'FALTA', 'REF', 'OBJ REF', '%']].rename(columns={
                    'V_Luz': 'Luz', 'V_Gas': 'Gas', 'V_Fibra': 'Fibra', 'V_Móvil': 'Móvil', 'V_Alarma': 'Alarma'
                })
                
                # Quitar decimales y añadir %
                num_cols = ['Luz', 'Gas', 'Fibra', 'Móvil', 'Alarma', 'TOTAL', 'T+M', 'OBJ', 'FALTA', 'REF', 'OBJ REF']
                df_tab[num_cols] = df_tab[num_cols].astype(int)
                df_tab['%'] = df_tab['%'].astype(str) + "%"

                st.markdown('<div class="ranking-box">', unsafe_allow_html=True)
                st.table(
                    df_tab.style
                    .map(semaforo_total, subset=['TOTAL'])
                    .map(semaforo_falta, subset=['FALTA'])
                    .map(semaforo_perc, subset=['%'])
                    .set_properties(**{'padding': '12px', 'text-align': 'center'})
                )
                st.markdown('</div>', unsafe_allow_html=True)

                # BOTONES CON GLOBOS
                st.write("---")
                st.subheader("🎯 Frases Motivadoras")
                cols_b = st.columns(4)
                for i, row in rank_visual.iterrows():
                    with cols_b[i % 4]:
                        nombre = row['Comercial'].split()[0]
                        total = row['TOTAL']
                        if total >= 25: frase = f"🥇 ¡{nombre}, ERES UNA MÁQUINA!"
                        elif total >= 15: frase = f"🚀 ¡{nombre}, VAS VOLANDO!"
                        elif total >= 5: frase = f"💪 ¡{nombre}, DALE DURO!"
                        else: frase = f"🎯 ¡{nombre}, A POR EL OBJETIVO!"
                        
                        if st.button(frase, key=f"btn_{i}"):
                            st.balloons()
                            st.toast(f"¡Vamos {nombre}! Tus Referidos: {int(row['REF'])}")

        with tab_e:
            if not de.empty:
                st.plotly_chart(px.bar(de.groupby('Comercial')['Total_Ene'].sum().reset_index(), x='Total_Ene', y='Comercial', orientation='h', title="Ventas Energía"), use_container_width=True)
        with tab_t:
            if not dt.empty:
                st.plotly_chart(px.bar(dt.groupby('Comercial')['Total_Tel'].sum().reset_index(), x='Total_Tel', y='Comercial', orientation='h', title="Ventas Telco"), use_container_width=True)
        with tab_a:
            if not da.empty:
                st.plotly_chart(px.bar(da.groupby('Comercial')['V_Alarma'].sum().reset_index(), x='V_Alarma', y='Comercial', orientation='h', title="Ventas Alarmas"), use_container_width=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    for c in ["GANA ENERGÍA", "NATURGY", "TOTAL", "ENDESA", "O2", "SEGURMA"]:
        with st.expander(f"📁 DOCUMENTACIÓN {c}"):
            st.write(f"Archivos de {c} disponibles.")