# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:15:09 2025

@author: jperezr
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# Estilo de fondo
page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background:
radial-gradient(black 15%, transparent 16%) 0 0,
radial-gradient(black 15%, transparent 16%) 8px 8px,
radial-gradient(rgba(255,255,255,.1) 15%, transparent 20%) 0 1px,
radial-gradient(rgba(255,255,255,.1) 15%, transparent 20%) 8px 9px;
background-color:#282828;
background-size:16px 16px;
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Título de la aplicación
st.title('Mapa Interactivo de México con CAPs')

# Sidebar con sección de ayuda y créditos
with st.sidebar:
    st.header("Ayuda")
    st.write("""
        Esta aplicación te permite visualizar un mapa interactivo de México con los Centros de Atención Primaria (CAPs) ubicados en cada estado.
        - Selecciona un estado en el menú desplegable para ver los CAPs en ese estado.
        - Los datos de las entidades federativas se cargan desde un archivo Excel.
        - Puedes ver gráficos dinámicos sobre afiliados, cuentas cedidas y recibidas.
    """)
    
    st.markdown("---")
    st.write("Desarrollado por: **Javier Horacio Pérez Ricárdez**")

# Cargar el mapa de México con CRS
@st.cache_data
def cargar_mapa_mexico():
    url = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json'
    response = requests.get(url, verify=False)
    geojson_mexico = json.loads(response.text)
    mapa_mexico = gpd.GeoDataFrame.from_features(geojson_mexico["features"])

    if mapa_mexico.crs is None:
        mapa_mexico.set_crs(epsg=4326, inplace=True)
    
    return mapa_mexico

# Cargar datos de CAPs
@st.cache_data
def cargar_caps():
    data = {
        'estado': ["CIUDAD DE MÉXICO", "OAXACA", "COAHUILA", "YUCATÁN", "JALISCO", "MÉXICO", "TLAXCALA", "TAMAULIPAS", "VERACRUZ", "CHIHUAHUA", "BAJA CALIFORNIA SUR", "SONORA", "HIDALGO", 
                   "CHIAPAS", "QUERÉTARO", "CAMPECHE", "NUEVO LEÓN", "AGUASCALIENTES", "GUANAJUATO", "DURANGO", "COLIMA", "SINALOA", "NAYARIT", "BAJA CALIFORNIA", "PUEBLA", "MICHOACÁN", "QUINTANA ROO", 
                   "TABASCO", "ZACATECAS", "MORELOS", "CIUDAD DE MÉXICO", "SAN LUIS POTOSÍ", "GUERRERO", "CHIHUAHUA", "DURANGO", "CHIAPAS", "BAJA CALIFORNIA", "QUINTANA ROO", "SONORA", "CIUDAD DE MÉXICO", 
                   "MÉXICO", "MÉXICO", "MÉXICO", "NUEVO LEÓN", "TAMAULIPAS", "MÉXICO", "QUERÉTARO", "CIUDAD DE MÉXICO", "JALISCO", "CIUDAD DE MÉXICO", 
                   "SAN LUIS POTOSÍ", "CIUDAD DE MÉXICO", "VERACRUZ", "GUANAJUATO", "CIUDAD DE MÉXICO"],
        'nombre': ["CAP BUENAVISTA", "CAP OAXACA DE JUÁREZ", "CAP SALTILLO (LA JOYA)", "CAP MÉRIDA", "CAP GUADALAJARA", "CAP TOLUCA", "CAP TLAXCALA", "CAP CD. VICTORIA", "CAP XALAPA", "CAP CHIHUAHUA", 
                   "CAP LA PAZ", "CAP HERMOSILLO", "CAP PACHUCA", "CAP TUXTLA GTZ", "CAP QUERÉTARO", "CAP CAMPECHE", "CAP MONTERREY DELEGACIÓN", "CAP AGUASCALIENTES", "CAP CELAYA", 
                   "CAP DURANGO", "CAP COLIMA", "CAP CULIACÁN", "CAP TEPIC", "CAP MEXICALI", "CAP PUEBLA", "CAP MORELIA", "CAP CHETUMAL", "CAP VILLAHERMOSA", "CAP ZACATECAS", "CAP CUERNAVACA", 
                   "CAP EUGENIA", "CAP SAN LUIS POTOSÍ", "CAP ACAPULCO", "CAP CD. JUAREZ", "CAP GOMEZ PALACIO", "CAP TAPACHULA", "CAP TIJUANA", "CAP CANCÚN", "CAP CD. OBREGÓN", "CAP MAGNA SUR",
                  "CAP IXTAPALUCA", "CAP TULTITLÁN", "CAP CUAUTITLÁN IZCALLI", "CAP MONTERREY CENTRIKA", "CAP REYNOSA", "CAP ECATEPEC", "CAP SAN JUAN DEL RÍO", "CAP VILLA COAPA", 
                  "CAP GUADALAJARA SUPERISSSTE", "CAP CULHUACÁN", "CAP Ciudad Valles", "CAP Vasconcelos", "CAP COATZACOALCOS", "CAP LEÓN", "CAP LA VIGA"],
        'latitud': [19.444842, 17.077156, 25.446294, 20.9927598, 20.684962,	19.2922765, 19.3246045,	23.732046, 19.5607808, 28.6180364, 24.148436, 29.0680158, 20.116257, 16.7513094, 20.593007, 
                    19.8537408,	25.671223, 21.878866, 20.532269, 24.021162, 19.272548, 24.819809, 21.507202, 32.641806, 19.051696,	19.728099, 18.493589, 18.000466, 22.743022, 18.924411, 
                    19.384393, 22.150445, 16.85402, 31.7349424, 25.5545574,	14.8993629, 32.494921, 21.153982, 27.4814187, 19.3574074, 19.3572844, 19.641655, 19.68572, 25.7001902, 26.073754,	
                    19.6044288, 20.394178, 19.3167491, 20.6630626, 19.3286155, 21.9873727, 19.4136232, 18.1425219, 21.1050246, 19.380642,],
        'longitud': [-99.151902, -96.706945,	-100.994901, -89.6115249, -103.347374, -99.6233734, -98.2339656, -99.130071, -96.9290164, -106.1034114,	-110.305273, -110.9578327, -98.742239, -93.1069386, 
                     -100.406277, -90.5283937, -100.337619, -102.292733,	-100.827153, -104.671233, -103.734967, -107.408358, -104.900549, -115.452342, -98.213072, -101.223281, -88.29624, -92.925871, 
                     -102.497195, -99.217665, -99.148584, -100.987531,	-99.857197, -106.4435867, -103.508086, -92.2495908,	-116.935152, -86.838344, -109.9272276, -99.1987345, -99.1984595, -99.135953, 
                     -99.213646, -100.3093165, -98.318685, -99.0123901,	-99.984535, -99.1237739, -103.2965445, -99.1086078, -99.0108345, -99.1813129, -94.4848837,	-101.6581152, -99.1216493]
    }
    return pd.DataFrame(data)

# Cargar el archivo xlsx con los datos de las entidades federativas
@st.cache_data
def cargar_entidades_federativas():
    try:
        # Cargar el archivo Excel
        df = pd.read_excel("entidades_federativas.xlsx")
        # Verificar que la columna "Entidad Federativa" existe
        if "Entidad Federativa" not in df.columns:
            st.error("La columna 'Entidad Federativa' no existe en el archivo Excel.")
            return pd.DataFrame()  # Retorna un DataFrame vacío si la columna no existe
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío si hay un error

# Crear el mapa con los CAPs
def crear_mapa(estado, mapa_mexico, caps):
    estado_geo = mapa_mexico[mapa_mexico['name'].str.upper() == estado.upper()]
    if estado_geo.empty:
        st.error("No se encontró información para el estado seleccionado")
        return None
    centroide = estado_geo.geometry.centroid.iloc[0]
    mapa = folium.Map(location=[centroide.y, centroide.x], zoom_start=7)
    folium.GeoJson(estado_geo).add_to(mapa)
    caps_estado = caps[caps['estado'].str.upper() == estado.upper()]
    for _, cap in caps_estado.iterrows():
        folium.Marker(
            location=[cap['latitud'], cap['longitud']],
            popup=cap['nombre'],
            icon=folium.Icon(color='green', icon='building')
        ).add_to(mapa)
    return mapa

# Cargar datos
mapa_mexico = cargar_mapa_mexico()
caps = cargar_caps()
entidades_federativas = cargar_entidades_federativas()

# Verificar si el DataFrame de entidades federativas está vacío
if entidades_federativas.empty:
    st.error("No se pudieron cargar los datos de las entidades federativas.")
else:
    # Crear selector de estado
    estados = mapa_mexico['name'].unique().tolist()
    estado_seleccionado = st.selectbox("Selecciona un estado:", estados)

    # Filtrar el DataFrame según el estado seleccionado
    df_estado = entidades_federativas[entidades_federativas["Entidad Federativa"].str.upper() == estado_seleccionado.upper()]

    # Mostrar el mapa con los CAPs
    mapa = crear_mapa(estado_seleccionado, mapa_mexico, caps)
    if mapa:
        st_folium(mapa, width=700, height=500)

    # Mostrar el DataFrame con los datos filtrados
    st.subheader(f'Datos de {estado_seleccionado}')
    st.dataframe(df_estado)

   # Gráficos dinámicos
st.subheader(f'Gráficos de {estado_seleccionado}')

# Verificar si el DataFrame no está vacío
if not df_estado.empty:
    # Limpiar los datos si es necesario
    try:
        # Si las columnas son strings, eliminar comas y símbolos de moneda
        if df_estado["# de afiliados"].dtype == "object":
            df_estado["# de afiliados"] = df_estado["# de afiliados"].str.replace(",", "").astype(float)
        if df_estado["# de cuentas cedidas"].dtype == "object":
            df_estado["# de cuentas cedidas"] = df_estado["# de cuentas cedidas"].str.replace(",", "").astype(float)
        if df_estado["# de cuentas recibidas"].dtype == "object":
            df_estado["# de cuentas recibidas"] = df_estado["# de cuentas recibidas"].str.replace(",", "").astype(float)
        if df_estado["Monto de cuentas recibidas"].dtype == "object":
            df_estado["Monto de cuentas recibidas"] = df_estado["Monto de cuentas recibidas"].str.replace("$", "").str.replace(",", "").astype(float)
        if df_estado["Monto de cuentas cedidas"].dtype == "object":
            df_estado["Monto de cuentas cedidas"] = df_estado["Monto de cuentas cedidas"].str.replace("$", "").str.replace(",", "").astype(float)
    except Exception as e:
        st.error(f"Error al limpiar los datos: {e}")

    # Gráfico de barras: Número de afiliados, cuentas cedidas y recibidas
    st.write("### Número de afiliados, cuentas cedidas y recibidas")
    fig, ax = plt.subplots()
    df_estado[["# de afiliados", "# de cuentas cedidas", "# de cuentas recibidas"]].plot(kind="bar", ax=ax)
    ax.set_xticklabels([estado_seleccionado], rotation=0)
    st.pyplot(fig)

    # Gráfico de pastel: Montos cedidos vs recibidos
    st.write("### Proporción de montos cedidos vs recibidos")
    montos = df_estado[["Monto de cuentas recibidas", "Monto de cuentas cedidas"]].iloc[0]
    fig, ax = plt.subplots()
    ax.pie(montos, labels=["Montos recibidos", "Montos cedidos"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Para que el gráfico sea un círculo
    st.pyplot(fig)

    # Gráfico interactivo con Plotly: Montos cedidos vs recibidos
    st.write("### Montos cedidos vs recibidos (Interactivo)")
    fig = px.bar(df_estado, x="Entidad Federativa", y=["Monto de cuentas recibidas", "Monto de cuentas cedidas"],
                 title=f"Montos en {estado_seleccionado}", barmode="group")
    st.plotly_chart(fig)
