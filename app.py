import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 2. CSS DE ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
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

# 3. BASE DE DATOS LUZ
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.111, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,163/0,096/0,072", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
]

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
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
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 PLANES Y ANUNCIOS", "📂 REPOSITORIO"], label_visibility="collapsed")

# --- CRM ---
if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#161b22; padding:15px; border-radius:10px; border:2px solid #d2ff00; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">MARCADOR PRINCIPAL</h4></div>''', unsafe_allow_html=True)
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
        st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">SEGURMA</h4></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://partners.segurma.com/", use_container_width=True)
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#161b22; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:white; margin:0;">O2</h4></div>', unsafe_allow_html=True)
        st.link_button("ENTRAR", "https://o2online.es/auth/login/", use_container_width=True)

# --- PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    t1, t2, t3 = st.tabs(["⚡ LUZ", "🔥 GAS", "📶 O2 / FIBRA"])
    with t1:
        df_precios = pd.DataFrame(tarifas_luz).drop(columns=['logo'])
        st.dataframe(df_precios, use_container_width=True, hide_index=True)
    with t2:
        df_gas = pd.DataFrame([
            {"PRIORIDAD": 1, "COMPAÑÍA": "TOTAL GAS", "FIJO RL1": "9,50 €", "ENERGIA RL1": "0,059 €/kWh", "FIJO RL2": "14,50 €", "ENERGIA RL2": "0,057 €/kWh"},
            {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "FIJO RL1": "5,34 €", "ENERGIA RL1": "0,084 €/kWh", "FIJO RL2": "10,03 €", "ENERGIA RL2": "0,081 €/kWh"},
            {"PRIORIDAD": 3, "COMPAÑÍA": "GANA ENERGÍA", "FIJO RL1": "3,93 €", "ENERGIA RL1": "VARIABLE (BENEF. 0,11€)", "FIJO RL2": "8,11 €", "ENERGIA RL2": "VARIABLE (BENEF. 0,006€)"}
        ])
        st.dataframe(df_gas, use_container_width=True, hide_index=True)
    with t3:
        st.markdown('<div class="block-header">📡 SOLO FIBRA</div>', unsafe_allow_html=True)
        f_cols = st.columns(3)
        solo_fibra = [("300 Mb", "23€"), ("600 Mb", "27€"), ("1 Gb", "31€")]
        for i, (vel, pre) in enumerate(solo_fibra):
            with f_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">FIBRA {vel}</div><div class="price-val">{pre}</div><div class="price-sub">Precio Final / Mes</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">🌐 FIBRA Y MÓVIL</div>', unsafe_allow_html=True)
        fm_cols = st.columns(4)
        fibra_movil = [("300 Mb", "40 GB", "30€", "1 LÍNEA"), ("600 Mb", "10+40 GB", "35€", "2 LÍNEAS"), ("600 Mb", "60 GB", "35€", "1 LÍNEA"), ("1 Gb", "120 GB", "38€", "1 LÍNEA")]
        for i, (vel, gb, pre, lin) in enumerate(fibra_movil):
            with fm_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{vel} + {lin}</div><div class="price-val">{pre}</div><div class="price-sub">{gb} de Datos</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">📺 TELEVISIÓN Y PACKS TV</div>', unsafe_allow_html=True)
        tv_cols = st.columns(5)
        packs_tv = [("SOLO TV", "", "9.99€", "M+ Suscripción"), ("600 Mb + TV", "35 GB", "38€", "M+ Incluido"), ("600 Mb + TV", "60 GB", "45€", "M+ / Netflix"), ("1 Gb + TV", "350 GB", "50€", "M+ Incluido"), ("1 Gb + TV", "375 GB", "56€", "M+ / Netflix")]
        for i, (tit, gb, pre, extra) in enumerate(packs_tv):
            with tv_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{tit}</div><div class="price-val">{pre}</div><div class="price-sub">{gb if gb else extra}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="block-header">➕ LÍNEAS ADICIONALES</div>', unsafe_allow_html=True)
        ad_cols = st.columns(3)
        ad_list = [("Móvil 40 GB", "5€"), ("Móvil 150 GB", "10€"), ("Móvil 300 GB", "15€")]
        for i, (lin, pre) in enumerate(ad_list):
            with ad_cols[i]:
                st.markdown(f'<div class="price-card"><div class="price-title">{lin}</div><div class="price-val">{pre}</div><div class="price-sub">Pago Mensual</div></div>', unsafe_allow_html=True)

# --- COMPARADOR ---
elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro Personalizado")
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Nombre del cliente", "Nombre Apellidos")
        f_act = st.number_input("Factura actual con IVA (EUR)", value=0.0)
        potencia = st.number_input("Potencia contratada (kW)", value=4.6)
        dias_factura = st.number_input("Días del periodo de factura", value=30)
    with c2:
        comp_sel = st.selectbox("Compañía Propuesta", sorted(list(set(t["COMPAÑÍA"] for t in tarifas_luz))))
        tarifas_f = [t["TARIFA"] for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel]
        tarifa_sel_nombre = st.selectbox("Tarifa Seleccionada", tarifas_f)
        sel = next(t for t in tarifas_luz if t["COMPAÑÍA"] == comp_sel and t["TARIFA"] == tarifa_sel_nombre)
        if os.path.exists(sel["logo"]): st.image(sel["logo"], width=120)
        consumo = st.number_input("Consumo del periodo (kWh)", value=0.0)
    try:
        p_calc = float(str(sel['ENERGIA']).split('/')[0].replace(',', '.')) if isinstance(sel['ENERGIA'], str) else sel['ENERGIA']
    except:
        p_calc = 0.11
    coste_p = (potencia * sel["P1"] * dias_factura) + (potencia * sel["P2"] * dias_factura)
    coste_e = consumo * p_calc
    coste_total_iva = (coste_p + coste_e) * 1.21
    ahorro = f_act - coste_total_iva
    st.info(f"**Tarifa Seleccionada:** {tarifa_sel_nombre} | Energía: **{sel['ENERGIA']}** €/kWh | Potencia: **{sel['P1']}** €/kW día")
    st.markdown(f'<div style="background:#d2ff00; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:black;">AHORRO ESTIMADO: {ahorro:.2f} €</h2></div>', unsafe_allow_html=True)
    if st.button("GENERAR ESTUDIO PDF PROFESIONAL"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists(LOGO_PRINCIPAL): pdf.image(LOGO_PRINCIPAL, 10, 8, 33)
        if os.path.exists(sel["logo"]): pdf.image(sel["logo"], 165, 8, 30)
        pdf.ln(30); pdf.set_font("Arial", "B", 18); pdf.cell(190, 10, "ESTUDIO COMPARATIVO DE AHORRO", ln=True, align="C")
        pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 8, f" DATOS DEL CLIENTE: {cliente.upper()}", ln=True, fill=True)
        pdf.set_font("Arial", "", 10); pdf.cell(95, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", border=1)
        pdf.cell(95, 8, f"Periodo: {dias_factura} dias", border=1, ln=True); pdf.ln(5)
        pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, " DETALLE DE LA PROPUESTA", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        for d, v in [("Compania", comp_sel), ("Tarifa", tarifa_sel_nombre), ("Potencia", f"{potencia} kW"), ("Energia", f"{sel['ENERGIA']} EUR/kWh")]:
            pdf.cell(95, 8, d, border=1); pdf.cell(95, 8, str(v), border=1, ln=True)
        pdf.ln(10); pdf.set_font("Arial", "B", 12); pdf.cell(95, 10, "Factura Actual", border=1); pdf.cell(95, 10, f"{f_act:.2f} EUR", border=1, ln=True)
        pdf.cell(95, 10, "Nueva Factura", border=1); pdf.cell(95, 10, f"{coste_total_iva:.2f} EUR", border=1, ln=True)
        pdf.ln(10); pdf.set_fill_color(210, 255, 0); pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 15, f"AHORRO TOTAL: {ahorro:.2f} EUR", ln=True, align="C", fill=True)
        st.download_button(label="📥 DESCARGAR ESTUDIO PDF", data=pdf.output(dest='S').encode('latin-1', 'replace'), file_name=f"Estudio_{cliente}.pdf")

# --- PLANES Y ANUNCIOS ---
elif menu == "📢 PLANES Y ANUNCIOS":
    st.header("Planes y Comunicación")
    
    st.markdown('<div class="block-header">📢 ANUNCIOS BASETTE</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'''<div style="background:#161b22; padding:20px; border-radius:10px; border:1px solid #30363d; text-align:center;">
            <h4 style="color:#d2ff00;">TABLÓN DE ANUNCIOS Y REDES</h4>
            <p style="color:white;">Consulta novedades y síguenos en nuestras redes sociales.</p>
        </div>''', unsafe_allow_html=True)
        c_an1, c_an2 = st.columns(2)
        with c_an1:
            st.link_button("VER ANUNCIOS", "https://forms.gle/CyBfXF9SDqCsq9tx8", use_container_width=True)
        with c_an2:
            st.link_button("📸 INSTAGRAM", "https://www.instagram.com/basette.eu/", use_container_width=True)

    st.markdown("---")

    st.markdown('<div class="block-header">🤝 PLAN AMIGO</div>', unsafe_allow_html=True)
    col_info, col_qr = st.columns([2, 1])
    
    with col_info:
        st.markdown(f'''<div style="background:#161b22; padding:20px; border-radius:10px; border:1px solid #30363d; height:100%;">
            <h4 style="color:#d2ff00;">¡GANA RECOMENDANDO!</h4>
            <p style="color:white;">Utiliza tu enlace o el código QR para registrar tus recomendaciones.</p>
            <br>
        </div>''', unsafe_allow_html=True)
        st.link_button("🔗 ENLACE FORMULARIO PLAN AMIGO", "https://forms.gle/mU6XzRvywDoBQ5Q47", use_container_width=True)

    with col_qr:
        # RUTA CORREGIDA PARA GITHUB (MI_INTRANET es la raíz, no parte de la ruta interna si estás ejecutando desde ahí)
        qr_path = "anunciosbasette/qr-plan amigo.png"
        if os.path.exists(qr_path):
            st.image(qr_path, caption="QR Plan Amigo", use_container_width=True)
            with open(qr_path, "rb") as file:
                st.download_button(label="📥 DESCARGAR QR", data=file, file_name="QR_Plan_Amigo.png", mime="image/png", use_container_width=True)
        else:
            st.error(f"Archivo no encontrado en: {qr_path}")

# --- REPOSITORIO ---
elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 MANUAL DEL MARCADOR"):
        manual_path = "manuales/Manual_Premiumnumber_Agente.pdf"
        if os.path.exists(manual_path):
            with open(manual_path, "rb") as f:
                st.download_button("📖 DESCARGAR MANUAL MARCADOR", f, file_name="Manual_Marcador_Agente.pdf", key="manual_marcador")
        else:
            st.warning("Archivo no encontrado en manuales.")
    with st.expander("📂 ARGUMENTARIOS DE VENTA"):
        docs = ["ARGUMENTARIO_ENERGÍA (Venta Fría) + Venta Cruzada Teleco.docx", "ARGUMENTARIO_TELECO (Clientes Movistar a O2) + Venta Cruzada Energía.docx", "FRASES PROHIBIDAS,PODER EN LA VENTA y REBATE OBJECIONES.docx"]
        for d in docs:
            if os.path.exists(f"manuales/{d}"):
                with open(f"manuales/{d}", "rb") as f: st.download_button(f"📘 {d}", f, file_name=d, key=d)
    st.markdown("---")
    for c in ["GANA ENERGÍA", "NATURGY", "TOTAL", "ENDESA", "O2"]:
        with st.expander(f"📁 DOCUMENTACIÓN {c}"):
            if os.path.exists("manuales"):
                busq = "total" if c == "TOTAL" else c.split()[0].lower()
                archivos = [f for f in os.listdir("manuales") if busq in f.lower() and "argumentario" not in f.lower() and not f.lower().endswith('.png')]
                for fn in archivos:
                    with open(f"manuales/{fn}", "rb") as f: st.download_button(f"📥 {fn}", f, file_name=fn, key=f"b_{fn}")