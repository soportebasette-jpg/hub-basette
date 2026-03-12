import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import base64

# Configuración de la página
st.set_page_config(page_title="Hub Basette", layout="wide")

# Estilo CSS para los botones y tarjetas (Basado en tus imágenes)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
    }
    .main-header {
        font-size: 25px;
        font-weight: bold;
        color: #DFFF00;
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS Y SESIÓN ---
if 'df_ausencias' not in st.session_state:
    st.session_state.df_ausencias = pd.DataFrame(columns=["Comercial", "Fecha Inicio", "Fecha Fin", "Nº DE DIAS", "Motivo"])

# --- PESTAÑAS PRINCIPALES ---
tab_r, tab_e, tab_t = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO"])

with tab_r:
    st.write("Contenido de Ranking")

with tab_e:
    st.write("Contenido de Energía")

with tab_t:
    st.markdown('<div class="main-header">📺 TELEVISIÓN Y PACKS TV</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="card"><strong>SOLO TV</strong><br><h2>9.99€</h2><small>M+ Suscripción</small></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><strong>600 Mb + TV</strong><br><h2>38€</h2><small>35 GB</small></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><strong>600 Mb + TV</strong><br><h2>45€</h2><small>60 GB</small></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="card"><strong>1 Gb + TV</strong><br><h2>50€</h2><small>350 GB</small></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="card"><strong>1 Gb + TV</strong><br><h2>56€</h2><small>375 GB</small></div>', unsafe_allow_html=True)

    st.markdown('<div class="main-header">➕ LÍNEAS ADICIONALES</div>', unsafe_allow_html=True)
    cola1, cola2, cola3 = st.columns(3)
    with cola1:
        st.markdown('<div class="card"><strong>Móvil 40 GB</strong><br><h2>5€</h2><small>Pago Mensual</small></div>', unsafe_allow_html=True)
    with cola2:
        st.markdown('<div class="card"><strong>Móvil 150 GB</strong><br><h2>10€</h2><small>Pago Mensual</small></div>', unsafe_allow_html=True)
    with cola3:
        st.markdown('<div class="card"><strong>Móvil 300 GB</strong><br><h2>15€</h2><small>Pago Mensual</small></div>', unsafe_allow_html=True)

# --- SECCIÓN DE AUSENCIAS (MANTENIDA SEGÚN TUS IMÁGENES) ---
st.divider()
st.subheader("Gestión de Ausencias")

with st.expander("Registrar Nueva Ausencia"):
    with st.form("form_ausencia"):
        comercial = st.text_input("Comercial")
        f_inicio = st.date_input("Fecha Inicio", value=datetime.now())
        f_fin = st.date_input("Fecha Fin", value=datetime.now())
        motivo = st.text_area("Motivo de la ausencia")
        
        submitted = st.form_submit_button("REGISTRAR EN EXCEL")
        if submitted:
            dias = (f_fin - f_inicio).days + 1
            nueva_fila = pd.DataFrame([[comercial, f_inicio, f_fin, dias, motivo]], 
                                     columns=["Comercial", "Fecha Inicio", "Fecha Fin", "Nº DE DIAS", "Motivo"])
            st.session_state.df_ausencias = pd.concat([st.session_state.df_ausencias, nueva_fila], ignore_index=True)
            st.success(f"Días calculados: {dias}")

st.info("⚠️ Paso Final: Para que se guarde en tu Excel, rellena los datos en este enlace:")
st.link_button("IR AL FORMULARIO DE REGISTRO", "https://tu-enlace-de-formulario.com")

if not st.session_state.df_ausencias.empty:
    df_v = st.session_state.df_ausencias
    st.table(df_v[["Comercial", "Fecha Inicio", "Fecha Fin", "Nº DE DIAS", "Motivo"]])
    
    # Gráfico de barras (Gantt simplificado)
    fig = px.bar(df_v, x="Fecha Fin", y="Comercial", base="Fecha Inicio", orientation='h',
                 color="Comercial", title="Próximas Ausencias por Comercial",
                 hover_data=["Fecha Inicio", "Fecha Fin", "Nº DE DIAS", "Motivo"])
    st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN DE ANUNCIOS Y PLAN AMIGO ---
st.divider()
col_anuncios, col_amigo = st.columns(2)

with col_anuncios:
    st.header("📢 ANUNCIOS")
    st.write("Descarga los materiales oficiales:")
    
    # Carpeta donde están las imágenes (Asegúrate de que la ruta sea correcta en tu entorno)
    path = "anunciosbasette/"
    anuncios = [
        {"file": "Anuncio1_qr.png", "label": "Anuncio 1 QR"},
        {"file": "Anuncio2_qr.png", "label": "Anuncio 2 QR"},
        {"file": "PUBLI3.jpg", "label": "Publicidad 3"}
    ]
    
    cols_img = st.columns(3)
    for idx, item in enumerate(anuncios):
        with cols_img[idx]:
            try:
                # Mostrar imagen pequeña
                st.image(f"{path}{item['file']}", use_column_width=True)
                
                # Botón de descarga
                with open(f"{path}{item['file']}", "rb") as file:
                    btn = st.download_button(
                        label=f"Descargar",
                        data=file,
                        file_name=item['file'],
                        mime="image/png" if "png" in item['file'] else "image/jpeg"
                    )
            except:
                st.error(f"No se encontró {item['file']}")

with col_amigo:
    st.header("👥 PLAN AMIGO")
    st.write("Comparte los beneficios con tus conocidos y obtén recompensas.")
    # URL de Instagram eliminada como solicitaste
    st.info("Consulta las bases del Plan Amigo con tu supervisor.")