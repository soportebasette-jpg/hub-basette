import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA Y DATOS (MANTENER IGUAL) ---
# Asumo que aquí tienes tu carga de datos de los 3 drives.
# Para que el TOTAL REF funcione, el DataFrame 'df_ventas' debe tener la columna 'Canal'

def calcular_ranking(df_ventas):
    # Agrupamos por comercial
    ranking = df_ventas.groupby('Comercial').agg({
        'Luz': 'sum',
        'Gas': 'sum',
        'Fibra': 'sum',
        'Móvil': 'sum',
        'Alarma': 'sum',
        'Canal': lambda x: (x == 'REF').sum()  # LÓGICA CORREGIDA PARA CONTAR 'REF'
    }).reset_index()

    # Renombrar columnas para claridad
    ranking.columns = ['Comercial', 'V_Luz', 'V_Gas', 'V_Fibra', 'V_Móvil', 'V_Alarma', 'TOTAL REF']
    
    # Cálculos adicionales
    ranking['VENTAS TOTALES SIN MOVIL'] = ranking['V_Luz'] + ranking['V_Gas'] + ranking['V_Fibra'] + ranking['V_Alarma']
    ranking['TOTAL CON MOVIL'] = ranking['VENTAS TOTALES SIN MOVIL'] + ranking['V_Móvil']
    
    ranking['OBJETIVO'] = 25
    ranking['FALTAN'] = ranking['OBJETIVO'] - ranking['TOTAL CON MOVIL']
    ranking['FALTAN'] = ranking['FALTAN'].apply(lambda x: x if x > 0 else 0)
    
    ranking['OBJETIVO REF'] = 8
    ranking['% CONSE'] = (ranking['TOTAL CON MOVIL'] / ranking['OBJETIVO'] * 100).round(0).astype(int).astype(str) + '%'
    
    # Ordenar por total
    ranking = ranking.sort_values(by='TOTAL CON MOVIL', ascending=False).reset_index(drop=True)
    
    # Añadir medallas
    ranking.insert(0, 'Puesto', '')
    for i in range(len(ranking)):
        if i == 0: ranking.loc[i, 'Puesto'] = '🥇 Oro'
        elif i == 1: ranking.loc[i, 'Puesto'] = '🥈 Plata'
        elif i == 2: ranking.loc[i, 'Puesto'] = '🥉 Bronce'
        else: ranking.loc[i, 'Puesto'] = '⭐'
        
    return ranking

# --- RENDERIZADO DEL DASHBOARD ---
st.title("Dashboard de Rendimiento y Ranking")

# Simulación de carga (sustituye por tu df real)
# df_ranking = calcular_ranking(df_unificado) 

if 'df_ranking' in locals() or 'ranking' in locals():
    # Estilo específico SOLO para este dashboard
    # Reducimos el tamaño de fuente y ajustamos colores para que sea legible
    st.markdown("""
        <style>
        .ranking-container {
            font-size: 12px !important;
        }
        div[data-testid="stDataFrame"] div[role="grid"] {
            background-color: #f8f9fa; /* Fondo claro para la tabla */
        }
        </style>
    """, unsafe_allow_html=True)

    # Función de estilo para las celdas
    def style_ranking(styler):
        styler.set_properties(**{
            'background-color': '#ffffff',
            'color': '#111111',
            'border-color': '#dee2e6',
            'font-size': '12px'
        })
        # Resaltar la columna de Faltan en rojo suave como en tu imagen
        styler.set_properties(subset=['FALTAN'], **{'background-color': '#ffcccc'})
        # Encabezados oscuros para contraste
        styler.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#2c3e50'), ('color', 'white'), ('font-size', '12px')]}
        ])
        return styler

    # Mostrar la tabla ajustada al ancho y con fuente pequeña
    df_mostrar = calcular_ranking(df_unificado) # Asegúrate que df_unificado es tu tabla base
    
    st.dataframe(
        style_ranking(df_mostrar.style),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("No se encontraron datos para generar el ranking.")

# --- EL RESTO DE TU CÓDIGO SIGUE AQUÍ SIN CAMBIOS ---