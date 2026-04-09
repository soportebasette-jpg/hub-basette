import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stDataFrame { border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

## --- TÍTULO ---
st.title("📊 Dashboard de Rendimiento y Ranking")

# --- SIMULACIÓN DE DATOS (Asegúrate de que tu carga de datos real mantenga estos nombres) ---
# Aquí incluyo los datos que se ven en tu imagen para que el código sea funcional
data = {
    'Pos': ['🥇 Oro', '🥈 Plata', '🥉 Bronce', '⭐'],
    'Comercial': ['BELEN TRONCOSO', 'DEBORAH RODRIGUEZ', 'LORENA POZO', 'LUIS RODRIGUEZ GOMEZ'],
    'Luz': [0, 2, 0, 0],
    'Gas': [0, 1, 0, 0],
    'Fibra': [5, 1, 2, 1],
    'Móvil': [7, 1, 2, 1],
    'Alarma': [0, 0, 1, 0],
    'REF': [2, 1, 0, 1]  # Ejemplo con datos para que no salga a 0
}

df = pd.DataFrame(data)

# --- CÁLCULOS LÓGICOS ---
# Ventas totales sin móvil (Luz + Gas + Fibra + Alarma)
df['TOTAL SIN MOVIL'] = df['Luz'] + df['Gas'] + df['Fibra'] + df['Alarma']
# Total con móvil
df['TOTAL CON MOVIL'] = df['TOTAL SIN MOVIL'] + df['Móvil']

# Objetivos
df['OBJ'] = 25
df['FALTA'] = df['OBJ'] - df['TOTAL SIN MOVIL']
df['OBJ REF'] = 8

# Porcentaje de consecución (basado en TOTAL SIN MOVIL vs OBJ)
df['%'] = (df['TOTAL SIN MOVIL'] / df['OBJ'] * 100).round(1)

# --- FUNCIÓN DE COLOR SEMÁFORO ---
def color_semaforo_faltan(val):
    # Entre más alto el número de "Faltan", más rojo (está lejos del objetivo)
    if val <= 5: color = '#28a745' # Verde (Cerca)
    elif val <= 15: color = '#ffc107' # Amarillo
    else: color = '#dc3545' # Rojo (Lejos)
    return f'background-color: {color}; color: white'

def color_semaforo_porcentaje(val):
    if val >= 80: color = '#28a745'
    elif val >= 40: color = '#ffc107'
    else: color = '#dc3545'
    return f'background-color: {color}; color: white'

def color_semaforo_referidos(val, obj_ref=8):
    if val >= obj_ref: color = '#28a745'
    elif val >= obj_ref / 2: color = '#ffc107'
    else: color = '#dc3545'
    return f'background-color: {color}; color: white'

# --- APLICAR ESTILOS ---
# Usamos map() en lugar de applymap() para compatibilidad con Pandas 2.0+
st_df = df.style.applymap(color_semaforo_faltan, subset=['FALTA']) \
                .applymap(color_semaforo_porcentaje, subset=['%']) \
                .applymap(color_semaforo_referidos, subset=['REF']) \
                .format({'%': '{:.0f}%'})

# --- RENDERIZADO DE LA INTERFAZ ---

# Tabs de navegación
tab_ranking, tab_energia, tab_telco, tab_alarmas = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO", "🛡️ ALARMAS"])

with tab_ranking:
    # Banner del número 1
    vendedor_top = df.iloc[0]['Comercial']
    ventas_top = df.iloc[0]['TOTAL SIN MOVIL']
    st.info(f"👑 #1: {vendedor_top} ({ventas_top} VENTAS SIN MÓVIL)")

    # Tabla Principal
    st.table(st_df)

# --- INFO EXTRA (BOTONES VAMOS) ---
st.markdown("---")
cols = st.columns(len(df))
for i, row in df.iterrows():
    with cols[i]:
        if st.button(f"🎯 VAMOS {row['Comercial'].split()[0]}", key=f"btn_{i}"):
            st.balloons()