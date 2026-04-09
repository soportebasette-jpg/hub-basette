import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(
    page_title="Basette Group | Hub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1f1f1f;
        color: white;
        border: 1px solid #303030;
    }
    /* Estilo para los botones de navegación */
    .nav-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATOS DE EJEMPLO (Basados en tus capturas) ---
data = {
    'Comercial': ['BELEN TRONCOSO', 'DEBORAH RODRIGUEZ', 'LORENA POZO', 'LUIS RODRIGUEZ GOMEZ'],
    'V_Fibra': [5, 1, 2, 1],
    'V_Móvil': [7, 1, 2, 1],
    'V_Energia': [3, 2, 4, 1],
    'V_Alarmas': [2, 1, 3, 2],
    'Compañía': ['O2', 'O2', 'O2', 'O2']
}
df = pd.DataFrame(data)

# --- NAVEGACIÓN ---
tabs = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS", "🎯 OBJETIVOS", "🖼️ MATERIAL PUBLICITARIO"])

# --- TAB ENERGÍA ---
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cuota de Energía")
        fig_pie = px.pie(df, names='Compañía', title='Distribución por Compañía', hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.subheader("Mix de Energía")
        fig_bar = px.bar(df, x='Comercial', y='V_Energia', title='Ventas por Comercial')
        st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB TELCO ---
with tabs[2]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cuota de Telco")
        fig_pie_telco = px.pie(df, names='Compañía', values='V_Fibra', title='Cuota O2', hole=0.5)
        st.plotly_chart(fig_pie_telco, use_container_width=True)
    with col2:
        st.subheader("Mix de Telco")
        fig_bar_telco = px.bar(df, x='Comercial', y=['V_Fibra', 'V_Móvil'], barmode='group', title='Fibra vs Móvil')
        st.plotly_chart(fig_bar_telco, use_container_width=True)

# --- TAB ALARMAS (NUEVA CONFIGURACIÓN AZUL) ---
with tabs[3]:
    st.markdown("""<style> div[data-testid="stExpander"] { border: 1px solid #0000FF; } </style>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cuota de Alarmas")
        # Gráfico de Rosco (Azul)
        fig_pie_alarm = px.pie(df, names='Compañía', values='V_Alarmas', hole=0.5,
                             color_discrete_sequence=['#0000FF', '#4169E1'])
        st.plotly_chart(fig_pie_alarm, use_container_width=True)
    with col2:
        st.subheader("Mix de Alarmas")
        # Gráfico de Barras (Azul)
        fig_bar_alarm = px.bar(df, x='Comercial', y='V_Alarmas', title='Sistemas Instalados',
                             color_discrete_sequence=['#0000FF'])
        st.plotly_chart(fig_bar_alarm, use_container_width=True)

# --- TAB OBJETIVOS ---
with tabs[4]:
    st.header("Cumplimiento de Objetivos Mensuales")
    # Simulación de la tabla de objetivos de tu captura
    st.info("No se han encontrado objetivos configurados para el mes: MARCH")
    st.table(df[['Comercial', 'V_Fibra']].rename(columns={'V_Fibra': 'VENTAS_ACTUALES'}))

# --- TAB MATERIAL PUBLICITARIO (CON NUEVOS ANUNCIOS) ---
with tabs[5]:
    st.header("🖼️ MATERIAL PUBLICITARIO")
    
    # Carpeta donde están las imágenes
    img_path = "anunciosbasette/"
    
    # Lista de anuncios solicitada
    anuncios = [
        {"nombre": "Anuncio Alarma 1", "archivo": "anuncio alarma1.jpg"},
        {"nombre": "Anuncio 1", "archivo": "anuncio1.jpg"},
        {"nombre": "Anuncio 2", "archivo": "anuncio2.jpg"},
        {"nombre": "Anuncio QR 1", "archivo": "Anuncio1_qr.png"},
        {"nombre": "Anuncio QR 2", "archivo": "Anuncio2_qr.png"}
    ]
    
    cols = st.columns(3)
    for i, ad in enumerate(anuncios):
        full_path = os.path.join(img_path, ad["archivo"])
        with cols[i % 3]:
            if os.path.exists(full_path):
                st.image(full_path, caption=ad["nombre"])
                with open(full_path, "rb") as file:
                    st.download_button(
                        label=f"Descargar {ad['nombre']}",
                        data=file,
                        file_name=ad["archivo"],
                        mime="image/jpeg" if ".jpg" in ad["archivo"] else "image/png"
                    )
            else:
                st.error(f"Falta archivo: {ad['archivo']}")

# --- SECCIÓN DE TARIFAS (Basado en image_905fd9.png) ---
st.divider()
st.markdown("### 💰 TARIFARIO VIGENTE")
cat1, cat2, cat3 = st.columns(3)
with cat1:
    st.success("SOLO FIBRA")
    st.write("300 Mb - 23€")
    st.write("600 Mb - 27€")
    st.write("1 Gb - 31€")
with cat2:
    st.info("FIBRA Y MÓVIL")
    st.write("300 Mb + 1 Línea (40GB) - 30€")
    st.write("600 Mb + 1 Línea (60GB) - 35€")
with cat3:
    st.warning("LÍNEAS ADICIONALES")
    st.write("Móvil 40 GB - 5€")
    st.write("Móvil 150 GB - 10€")