import streamlit as st
import pandas as pd
import datetime

# Configuración de la página
st.set_page_config(page_title="Dashboard Comercial Basette", layout="wide")

# --- FUNCIONES DE CARGA DE DATOS ---
def cargar_objetivos():
    # Enlace de Google Sheets en formato exportable
    sheet_url = "https://docs.google.com/spreadsheets/d/1RSvqNHuymjYKVZ0QHgTKrLEl4xuSPVeS/export?format=xlsx"
    try:
        df_obj = pd.read_excel(sheet_url)
        # Limpieza de nombres de columnas por si acaso hay espacios
        df_obj.columns = df_obj.columns.str.strip()
        return df_obj
    except Exception as e:
        st.error(f"Error al conectar con Drive: {e}")
        return pd.DataFrame()

# Simulación de carga de ventas (aquí deberías tener tu conexión actual a la base de datos o CSV)
# Esta función es un ejemplo, asegúrate de que use tu fuente de datos real
def cargar_ventas_reales():
    # Placeholder: Datos de ejemplo basados en tus capturas
    data = {
        'COMERCIAL': ['BELEN TRONCOSO', 'DEBORAH RODRIGUEZ', 'LORENA POZO', 'LUIS RODRIGUEZ GOMEZ'],
        'V_Fibra': [5, 1, 2, 1],
        'V_Móvil': [7, 1, 2, 1],
        'TIPO': ['Fibra', 'Fibra', 'Fibra', 'Móvil'] # Esto es para el filtro de conteo
    }
    return pd.DataFrame(data)

# --- INTERFAZ DEL DASHBOARD ---

# Menú superior
tabs = st.tabs(["RANKING", "ENERGÍA", "TELCO", "ALARMAS", "OBJETIVO MENSUAL"])

# --- TAB RANKING, ENERGÍA, TELCO, ALARMAS (Mantenidos sin cambios según instrucción) ---
with tabs[0]:
    st.header("Ranking de Ventas")
    # Aquí iría tu código actual de Ranking

with tabs[1]:
    st.header("Ventas Energía")
    # Aquí iría tu código actual de Energía

with tabs[2]:
    st.header("Estadísticas Telco")
    # Código para mostrar gráficos de Telco como en image_9f0626.png
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cuota de Telco")
        # Tu gráfico circular aquí
    with col2:
        st.subheader("Mix de Telco")
        # Tu gráfico de barras aquí

with tabs[3]:
    st.header("Gestión de Alarmas y Publicidad")
    
    # CORRECCIÓN DE RUTAS DE ANUNCIOS
    # Se añade el prefijo de la carpeta 'anunciosbasette/' para evitar los errores de carga
    col_an1, col_an2, col_pub = st.columns(3)
    
    with col_an1:
        st.image("anunciosbasette/anuncio1.jpg", caption="Anuncio 1", use_container_width=True)
        st.download_button("Descargar Anuncio 1 QR", data=open("anunciosbasette/anuncio1.jpg", "rb"), file_name="anuncio1.jpg")
        
    with col_an2:
        st.image("anunciosbasette/anuncio2.jpg", caption="Anuncio 2", use_container_width=True)
        st.download_button("Descargar Anuncio 2 QR", data=open("anunciosbasette/anuncio2.jpg", "rb"), file_name="anuncio2.jpg")

    with col_pub:
        st.image("anunciosbasette/PUBLI3.png", caption="Publicidad 3", use_container_width=True)
        st.download_button("Descargar Publicidad 3", data=open("anunciosbasette/PUBLI3.png", "rb"), file_name="PUBLI3.png")

    # Otros anuncios mencionados en tus errores
    st.subheader("Otros Materiales")
    col_ext1, col_ext2 = st.columns(2)
    with col_ext1:
        try:
            st.image("anunciosbasette/anuncio_alarma1.png", width=200)
        except:
            st.warning("Archivo anuncio_alarma1.png no encontrado en carpeta anunciosbasette")
    
# --- NUEVA SECCIÓN: OBJETIVO MENSUAL ---
with tabs[4]:
    st.header("Cumplimiento de Objetivos Mensuales")
    
    # Obtener mes actual en español y mayúsculas para coincidir con el Excel
    meses_es = {1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL", 5: "MAYO", 6: "JUNIO", 
                7: "JULIO", 8: "AGOSTO", 9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"}
    mes_actual = meses_es[datetime.datetime.now().month]
    
    # Cargar datos
    df_objetivos = cargar_objetivos()
    df_ventas = cargar_ventas_reales() # Asegúrate que esta función use tus datos reales
    
    if not df_objetivos.empty:
        # Filtrar objetivos por el mes actual
        df_obj_mes = df_objetivos[df_objetivos['MES'].astype(str).str.upper() == mes_actual].copy()
        
        if df_obj_mes.empty:
            st.warning(f"No se han encontrado objetivos configurados para el mes: {mes_actual}")
        else:
            # Preparar tabla final
            # Sumamos solo ventas que NO sean móviles (en este ejemplo usamos V_Fibra)
            # Ajusta 'V_Fibra' al nombre de tu columna de ventas de fibra/energía/alarmas
            resumen_ventas = df_ventas.groupby('COMERCIAL')['V_Fibra'].sum().reset_index()
            resumen_ventas.columns = ['COMERCIAL', 'VENTAS_ACTUALES']
            
            # Unir con objetivos
            df_final = pd.merge(df_obj_mes, resumen_ventas, on='COMERCIAL', how='left').fillna(0)
            
            # Cálculos solicitados
            df_final['VENTAS_ACTUALES'] = df_final['VENTAS_ACTUALES'].astype(int)
            df_final['OBJETIVO'] = df_final['OBJETIVO'].astype(int)
            
            # Restante (Objetivo - Actuales, mínimo 0)
            df_final['RESTANTE'] = (df_final['OBJETIVO'] - df_final['VENTAS_ACTUALES']).clip(lower=0)
            
            # % Consecución (sin decimales)
            def calcular_porcentaje(row):
                if row['OBJETIVO'] > 0:
                    return int((row['VENTAS_ACTUALES'] / row['OBJETIVO']) * 100)
                return 100 if row['VENTAS_ACTUALES'] > 0 else 0
            
            df_final['% LOGRADO'] = df_final.apply(calcular_porcentaje, axis=1)
            
            # Renombrar columnas para visualización
            df_mostrar = df_final[['COMERCIAL', 'VENTAS_ACTUALES', 'OBJETIVO', 'RESTANTE', '% LOGRADO']]
            df_mostrar.columns = ['COMERCIAL', 'VENTAS ACTUALES', 'OBJETIVO/FIRMAS', 'RESTANTE', '% LOGRADO']
            
            # Estilo de la tabla (Fondo rojo como en tu imagen)
            def style_red(styler):
                styler.set_properties(**{'background-color': '#ff4b4b', 'color': 'white', 'border': '1px solid white'})
                return styler

            st.table(df_mostrar.style.pipe(style_red).format(precision=0))
    else:
        st.error("No se pudo cargar la información de objetivos desde Google Sheets.")

# --- PIE DE PÁGINA O ESTILOS ADICIONALES ---
st.markdown("""
    <style>
    .stTable {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)