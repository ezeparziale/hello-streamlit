import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Titulo
st.title('Streamlit para análisis de datos')

# Bara lateral
st.sidebar.header('Selecciones')

# Carga de datos
@st.cache
def load_data():
    df = pd.read_json('https://raw.githubusercontent.com/ezeparziale/hello-docker/master/src/data/players.json')
    filter_col = ['AGE','GP','MPG','MIN_pct','USG_pct','TO_pct','FTA','FT_pct','twoPA','twoP_pct','threePA','threeP_pct','eFG_pct','TS_pct','PPG','RPG','TRB_pct','APG','AST_pct','SPG','BPG','TOPG','VIV','ORTGO','DRTGD'         ]
    for column in filter_col:
        df[column] = df[column].astype(str)
        df[column] = df[column].str.replace(',','.').astype(float)
    return df

pd.options.display.float_format = '{:,.1f}'.format  # Para mostrar con dos decimales

df_nba_stats = load_data()  # Cargamos los datos en el dataframe

# Selector de Equipos
sorted_unique_team = sorted(df_nba_stats.TEAM.unique())
selected_team = st.sidebar.multiselect('TEAM', sorted_unique_team, sorted_unique_team)

# Selector de posición del jugador
unique_pos = sorted(df_nba_stats.POS.unique())
selected_pos = st.sidebar.multiselect('POS', unique_pos, unique_pos)

# Filtro el dataframe con los valores seleccionados
df_selected = df_nba_stats[(df_nba_stats.TEAM.isin(selected_team)) & (df_nba_stats.POS.isin(selected_pos))]

# Titulo cabecera
st.header('NBA stats')

# Subtitulo
st.write('Set de datos: ' + str(df_selected.shape[0]) + ' filas y ' + str(df_selected.shape[1]) + ' columnas')

# Mostramos el dataframe
st.dataframe(df_selected)

# Export a CSV
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="NBA_stats.csv">Export CSV</a>'
    return href

# Link para descargar el csv
st.markdown(filedownload(df_selected), unsafe_allow_html=True)

# Grafico
aux = df_selected.groupby('TEAM')['AGE'].mean()
aux = pd.DataFrame({'TEAM': aux.index, 'AGE_mean': aux.values})
aux = aux.sort_values('AGE_mean')
fig, ax = plt.subplots()
ax.barh(aux.TEAM, aux.AGE_mean, color='red', alpha=0.5)
st.pyplot(fig)