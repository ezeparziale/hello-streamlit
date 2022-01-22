from turtle import width
from webbrowser import BackgroundBrowser
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import plotly.express as px


st.set_page_config(page_title="NBA stats", layout="wide", page_icon=":basketball:")

# Titulo
# st.title('Streamlit para análisis de datos')

# Bara lateral
st.sidebar.header("Opciones:")

# Titulo cabecera
t1, t2 = st.columns((0.08, 1))
t1.image("img/logo.png", width=50)
t2.title("NBA stats")

# Carga de datos
@st.cache
def load_data():
    df = pd.read_json(
        "https://raw.githubusercontent.com/ezeparziale/hello-docker/master/src/data/players.json"
    )
    filter_col = [
        "AGE",
        "GP",
        "MPG",
        "MIN_pct",
        "USG_pct",
        "TO_pct",
        "FTA",
        "FT_pct",
        "twoPA",
        "twoP_pct",
        "threePA",
        "threeP_pct",
        "eFG_pct",
        "TS_pct",
        "PPG",
        "RPG",
        "TRB_pct",
        "APG",
        "AST_pct",
        "SPG",
        "BPG",
        "TOPG",
        "VIV",
        "ORTGO",
        "DRTGD",
    ]
    df = df.rename(columns={"FULL_NAME": "JUGADOR"})
    for column in filter_col:
        df[column] = df[column].astype(str)
        df[column] = df[column].str.replace(",", ".").astype(float)
    return df


pd.options.display.float_format = "{:,.1f}".format  # Para mostrar con dos decimales

df_nba_stats = load_data()  # Cargamos los datos en el dataframe

# Selector de Jugador
sorted_unique_player = sorted(df_nba_stats.JUGADOR.unique())
all_players = st.sidebar.checkbox("Ver todos los jugadores", key="JUGADOR", value=True)

if all_players:
    selected_player = st.sidebar.selectbox("JUGADOR", ["Todos"])
else:
    selected_player = st.sidebar.selectbox("JUGADOR", sorted_unique_player)

# Selector de Equipos
sorted_unique_team = sorted(df_nba_stats.TEAM.unique())
all_teams = st.sidebar.checkbox("Ver todos los equipos", key="TEAM", value=True)

if all_teams:
    selected_team = st.sidebar.multiselect(
        "TEAM", sorted_unique_team, sorted_unique_team
    )
else:
    selected_team = st.sidebar.multiselect("TEAM", sorted_unique_team)

# Selector de posición del jugador
unique_pos = sorted(df_nba_stats.POS.unique())
all_pos = st.sidebar.checkbox("Ver todas las posiciones", key="POS", value=True)

if all_pos:
    selected_pos = st.sidebar.multiselect("POS", unique_pos, unique_pos)
else:
    selected_pos = st.sidebar.multiselect("POS", unique_pos)

# Filtro el dataframe con los valores seleccionados
if all_players:
    df_selected = df_nba_stats[
        (df_nba_stats.TEAM.isin(selected_team)) & (df_nba_stats.POS.isin(selected_pos))
    ]
else:
    df_selected = df_nba_stats[df_nba_stats.JUGADOR == selected_player]


# Logos de equipos
teams = sorted(df_selected.TEAM.unique())
teams_list = []
for team in teams:
    path_team = "./img/teams/" + team + ".png"
    teams_list.append(path_team)

with st.container():
    st.image(teams_list, width=45, caption=teams)

# Subtitulo
st.write(
    "Set de datos: "
    + str(df_selected.shape[0])
    + " filas y "
    + str(df_selected.shape[1])
    + " columnas"
)

# Mostramos el dataframe
with st.container():
    columns = st.multiselect(
        "Columnas",
        df_nba_stats.columns,
        list(df_nba_stats.columns),
        help="Seleccione las columnas a visualizar",
    )
    st.dataframe(df_selected[columns])

# Export a CSV
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = (
        f'<a href="data:file/csv;base64,{b64}" download="NBA_stats.csv">Export CSV</a>'
    )
    return href


# Link para descargar el csv
st.markdown(filedownload(df_selected), unsafe_allow_html=True)

# Subtitulo
st.subheader("Edad promedio:")

# Grafico
aux = df_selected.groupby("TEAM")["AGE"].mean().round(2)
aux = pd.DataFrame({"TEAM": aux.index, "AGE_mean": aux.values})
aux = aux.sort_values("AGE_mean")
fig = px.bar(aux, x='AGE_mean', y='TEAM', orientation='h', hover_data=["TEAM","AGE_mean"], text='AGE_mean')
config = {'displayModeBar': False}
fig.update_traces(marker_color='#C9082A')
fig.update_layout(
    autosize=False,
    width=30,
    height=800,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
     margin=dict(
        l=50,
        r=50,
        b=0,
        t=0,
        pad=4
    ),
)
st.plotly_chart(fig, use_container_width=True, config=config)
