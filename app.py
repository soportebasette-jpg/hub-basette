import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Función para convertir imagen a base64 y que se vea en el HTML
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Preparamos la imagen de Rosco
img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD (GENERAL)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #d2ff00 !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
    }
    button p, .stDownloadButton button p { color: #000000 !important; font-weight: 900 !important; }
    button, .stDownloadButton button { background-color: #ffffff !important; border: 2px solid #d2ff00 !important; }
    
    /* Estilos personalizados para las tarjetas de control laboral */
    .metric-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #30363d;
        text-align: center;
        min-height: 110px;
    }
    .metric-title {
        color: #8b949e;
        font-weight: bold;
        margin: 0;
        font-size: 0.8rem;
    }
    .metric-value {
        color: #ffffff;
        margin: 5px 0;
        font-size: 1.5rem;
    }
    .metric-sub {
        color: #8b949e;
        font-size: 0.65rem;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTENTICACIÓN SIMPLIFICADA (Para evitar bloqueos locales)
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        logo_path = "LOGO BASETTE GRUO EUROPA SL.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path)
        st.markdown("<h3 style='text-align: center; color: #d2ff00;'>ACCESO COMERCIAL</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Introduce Clave:", type="password")
        if st.button("ENTRAR AL HUB"):
            if pwd == "Ventas2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    st.stop()

# 4. NAVEGACIÓN Y LOGO EN SIDEBAR
with st.sidebar:
    logo_path = "LOGO BASETTE GRUO EUROPA SL.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path)
    st.markdown("<h3 style='text-align: center; color: #ffffff; margin-top: 0;'>MENÚ INTRANET</h3>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🚀 CRM", "📊 PRECIOS", "⚖️ COMPARADOR", "📢 ANUNCIOS Y PLAN AMIGO", "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO"])

# --- LÓGICA DE LAS SECCIONES ---

if menu == "🚀 CRM":
    st.header("Portales de Gestión")
    col_crm1, col_crm2, col_crm3 = st.columns(3)
    with col_crm1:
        st.link_button("🌐 CRM MASMOVIL", "https://portales.masmovil.com/")
    with col_crm2:
        st.link_button("🌐 CRM DIGI", "https://partner.digimobil.es/")
    with col_crm3:
        st.link_button("🌐 CRM FINETWORK", "https://crm.finetwork.com/")

elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    st.info("Consulta las últimas ofertas de Fibra, Luz y Gas vigentes en el mercado.")

elif menu == "⚖️ COMPARADOR":
    st.header("Estudio de Ahorro Energético")
    st.write("Introduce los datos de la factura para calcular la mejor opción para tu cliente.")
    
    # DATOS FIJOS DE COMPAÑÍAS ACTUALIZADOS
    precios_companias = {
        'Gana Energía': {'p1': 0.135, 'p2': 0.110, 'p3': 0.085, 'excedente': 0.06}, # MODIFICADO: Excedente antes 0.05 ahora 0.06
        'TotalEnergies': {'p1': 0.142, 'p2': 0.115, 'p3': 0.090, 'excedente': 0.05},
        'Iberdrola': {'p1': 0.155, 'p2': 0.125, 'p3': 0.095, 'excedente': 0.04},
        'Endesa': {'p1': 0.148, 'p2': 0.120, 'p3': 0.088, 'excedente': 0.045}
    }
    
    # DATOS DE GAS ACTUALIZADOS
    precios_gas = {
        'Gana Energía': {'RL1': 0.052, 'RL2': 0.049},
        'TotalEnergies': {'RL1': 0.08, 'RL2': 0.08}, # MODIFICADO: Antes 0.05 ahora 0.08
        'Iberdrola': {'RL1': 0.061, 'RL2': 0.058},
        'Endesa': {'RL1': 0.059, 'RL2': 0.055}
    }

    # Interfaz del comparador (Sin tocar fórmulas ni lógicas complejas)
    tipo_estudio = st.radio("Tipo de Suministro:", ["⚡ LUZ", "🔥 GAS"])
    
    if tipo_estudio == "⚡ LUZ":
        st.subheader("Cálculo de Ahorro Eléctrico")
        c1, c2, c3 = st.columns(3)
        with c1: kwh_p1 = st.number_input("Consumo P1 (kWh):", min_value=0.0, value=150.0)
        with c2: kwh_p2 = st.number_input("Consumo P2 (kWh):", min_value=0.0, value=120.0)
        with c3: kwh_p3 = st.number_input("Consumo P3 (kWh):", min_value=0.0, value=200.0)
        
        excedentes_kwh = st.number_input("Energía Volcada/Excedente (kWh):", min_value=0.0, value=0.0)
        
        st.markdown("### 📊 Resultados Comparativa Luz")
        resultados_luz = []
        for comp, precios in precios_companias.items():
            coste_p1 = kwh_p1 * precios['p1']
            coste_p2 = kwh_p2 * precios['p2']
            coste_p3 = kwh_p3 * precios['p3']
            total_consumo = coste_p1 + coste_p2 + coste_p3
            ahorro_solar = excedentes_kwh * precios['excedente']
            total_factura = max(0.0, total_consumo - ahorro_solar)
            resultados_luz.append({'Compañía': comp, 'Término Energía': f"{total_consumo:.2f} €", 'Ahorro Solar': f"{ahorro_solar:.2f} €", 'Total Estimado': total_factura})
            
        df_res_luz = pd.DataFrame(resultados_luz).sort_values('Total Estimado')
        df_res_luz['Total Estimado'] = df_res_luz['Total Estimated'] = df_res_luz['Total Estimado'].apply(lambda x: f"{x:.2f} €")
        st.dataframe(df_res_luz, use_container_width=True, hide_index=True)

    elif tipo_estudio == "🔥 GAS":
        st.subheader("Cálculo de Ahorro de Gas")
        tarifa_gas = st.selectbox("Tarifa de Gas actual:", ["RL1", "RL2"])
        kwh_gas = st.number_input("Consumo Total Gas (kWh):", min_value=0.0, value=500.0)
        
        st.markdown("### 📊 Resultados Comparativa Gas")
        resultados_gas = []
        for comp, tarifas in precios_gas.items():
            precio_kwh = tarifas[tarifa_gas]
            total_gas = kwh_gas * precio_kwh
            resultados_gas.append({'Compañía': comp, 'Tarifa Aplicada': tarifa_gas, 'Precio kWh': f"{precio_kwh:.3f} €", 'Total Estimado Gas': f"{total_gas:.2f} €"})
            
        df_res_gas = pd.DataFrame(resultados_gas)
        st.dataframe(df_res_gas, use_container_width=True, hide_index=True)

elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Canal Oficial de Comunicación")
    st.success("🔥 BONO MENSUAL: Supera tu objetivo mínimo del mes y llévate un bono extra en tu próxima liquidación.")
    st.markdown("---")
    st.subheader("🔗 Síguenos en Redes Sociales")
    
    # ICONOS CON NUEVO ENLACE DE FACEBOOK ACTUALIZADO
    col_icon1, col_icon2 = st.columns(2)
    with col_icon1:
        st.markdown(f'<a href="https://www.facebook.com/profile.php?id=61589358886498&locale=es_ES" target="_blank"><img src="data:image/png;base64,{get_base64_of_bin_file("facebook_logo.jpg") if os.path.exists("facebook_logo.jpg") else ""}" width="50"> Visitar Facebook Basette</a>', unsafe_allow_html=True)
    with col_icon2:
        st.markdown(f'<a href="https://www.instagram.com/" target="_blank"><img src="data:image/png;base64,{get_base64_of_bin_file("instagram_logo.jpg") if os.path.exists("instagram_logo.jpg") else ""}" width="50"> Visitar Instagram Basette</a>', unsafe_allow_html=True)

elif menu == "📈 DASHBOARD Y RANKING":
    # Inicialización de seguridad para evitar errores 'hf' al renderizar el bloque final común
    hf, mf, pend, p_col = 0, 0, 0, "#d2ff00" 
    justificantes = []
    l_deuda = []

    st.balloons() 
    st.markdown("<h1 style='color: #d2ff00;'>📈 Dashboard de Rendimiento - Abril</h1>", unsafe_allow_html=True)
    
    st.warning("🚀 **INCENTIVO ESPECIAL ABRIL:** Las ventas de **FIBRA** realizadas entre el **4 y el 14 de abril** computan doble (x2) para el ranking y objetivos.")

    try:
        url_ventas = "https://docs.google.com/spreadsheets/d/1vCBeO_X9IInN_U8m_r8_N27O-QvR16jYv0-p8qO-2W4/export?format=csv"
        dfv = pd.read_csv(url_ventas)
        dfv['Fecha'] = pd.to_datetime(dfv['Fecha'], dayfirst=True, errors='coerce')
        df_abril = dfv[dfv['Fecha'].dt.month == 4].copy()

        # Cálculo de puntos x2 para Fibra
        def calcular_puntos_fibra(row):
            if pd.notnull(row['Fecha']) and row['Fecha'].day >= 4 and row['Fecha'].day <= 14:
                return row['V_Fibra'] * 2
            return row['V_Fibra']

        df_abril['V_Fibra_Puntos'] = df_abril.apply(calcular_puntos_fibra, axis=1)

        # Forzar aparición de DEBORAH con 0 si no tiene ventas
        comerciales_en_lista = [str(c).upper() for c in df_abril['Comercial'].unique()]
        if 'DEBORAH' not in comerciales_en_lista:
            nueva_fila = pd.DataFrame({'Comercial': ['DEBORAH'], 'V_Fibra': [0], 'V_Fibra_Puntos': [0], 'V_Luz_Gas': [0], 'V_Alarma': [0], 'Fecha': [pd.Timestamp(2024,4,1)]})
            df_abril = pd.concat([df_abril, nueva_fila], ignore_index=True)

        # Agrupación para el Ranking
        ranking = df_abril.groupby('Comercial').agg({
            'V_Fibra_Puntos': 'sum',
            'V_Luz_Gas': 'sum',
            'V_Alarma': 'sum'
        }).reset_index()
        
        ranking['Total'] = ranking['V_Fibra_Puntos'] + ranking['V_Luz_Gas'] + ranking['V_Alarma']
        ranking = ranking.sort_values('Total', ascending=False)

        # Métricas principales (Objetivo 20)
        total_puntos_abril = ranking['Total'].sum()
        objetivo_total_servicio = 20 * len(ranking)
        faltan_total = max(0, objetivo_total_servicio - total_puntos_abril)

        m1, m2, m3 = st.columns(3)
        m1.metric("Puntos Totales Abril", int(total_puntos_abril))
        m2.metric("Objetivo Servicio (20/com)", objetivo_total_servicio)
        m3.metric("Faltan para Objetivo", int(faltan_total))

        st.markdown("---")

        # Visualización Ranking y Objetivos Individuales
        col_rank, col_det = st.columns([2, 1])
        with col_rank:
            st.subheader("🏆 Ranking de Puntos")
            fig_rank = px.bar(ranking, x='Total', y='Comercial', orientation='h', text_auto=True, color='Total', color_continuous_scale='Viridis')
            fig_rank.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_rank, use_container_width=True)

        with col_det:
            st.subheader("🎯 Faltan para 20")
            for _, row in ranking.iterrows():
                faltan_ind = max(0, 20 - row['Total'])
                color_txt = "#d2ff00" if faltan_ind == 0 else "#ff4b4b"
                st.markdown(f"**{row['Comercial']}**: {int(row['Total'])} pts (Faltan: <span style='color:{color_txt}'>{int(faltan_ind)}</span>)", unsafe_allow_html=True)

        # Las 3 pestañas solicitadas
        st.markdown("---")
        t1, t2, t3 = st.tabs(["🌐 FIBRA", "⚡ LUZ Y GAS", "🚨 ALARMAS"])

        with t1:
            st.markdown("### Ventas de Fibra (con x2 aplicado)")
            df_f = df_abril[df_abril['V_Fibra_Puntos'] > 0]
            if not df_f.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_f, x="Comercial", y="V_Fibra_Puntos", color="Compañia", title="Puntos Fibra por Comercial"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.pie(df_f, values="V_Fibra_Puntos", names="Compañia", title="Reparto por Compañía"), use_container_width=True)

        with t2:
            st.markdown("### Ventas de Luz y Gas")
            df_l = df_abril[df_abril['V_Luz_Gas'] > 0]
            if not df_l.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_l, x="Comercial", y="V_Luz_Gas", color="Compañia", title="Ventas Luz/Gas por Comercial"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.pie(df_l, values="V_Luz_Gas", names="Compañia", title="Reparto por Compañía"), use_container_width=True)

        with t3:
            st.markdown("### Ventas de Alarmas")
            df_a = df_abril[df_abril['V_Alarma'] > 0]
            if not df_a.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(px.bar(df_a, x="Comercial", y="V_Alarma", color="Compañia", title="Ventas Alarmas por Comercial"), use_container_width=True)
                with c2:
                    st.plotly_chart(px.pie(df_a, values="V_Alarma", names="Compañia", title="Reparto por Compañía"), use_container_width=True)

    except Exception as e:
        st.error(f"Error cargando el Dashboard: {e}")

elif menu == "📂 REPOSITORIO":
    st.header("Documentación")
    with st.expander("📂 MANUALES"):
        st.write("Archivos PDF disponibles para descarga.")

# --- BLOQUE FINAL DE SEGUIMIENTO LABORAL (CORREGIDO PARA EVITAR SQUASH DE VARIABLES) ---
# Solo ejecutamos la lógica de horas pendientes reales si existieron en el contexto de Control Laboral.
if menu != "📈 DASHBOARD Y RANKING" and 'hf' in locals() and hf > 0:
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown(f'<div class="metric-card" style="border:2px solid {p_col};"><p class="metric-title" style="color:{p_col};">PENDIENTE</p><h2 class="metric-value" style="color:{p_col};">{int(hf)}h {int(mf)}m</h2><p class="metric-sub">{pend} min</p></div>', unsafe_allow_html=True)