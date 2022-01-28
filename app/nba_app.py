import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# Configuración pandas
pd.options.display.float_format = "{:,.1f}".format  # Para mostrar con dos decimales

# Configuración pagina streamlit
st.set_page_config(page_title="NBA stats", layout="wide", page_icon=":basketball:")

# Bara lateral
st.sidebar.header("Opciones:")

# Titulo cabecera
t1, t2 = st.columns((0.08, 1))
t1.image("img/logo.png", width=50)
t2.title("NBA stats")

# Carga de datos
@st.cache(allow_output_mutation=True)
def load_data_players():
    df = pd.read_csv("data/players.csv")
    filter_col = ["conference_id", "division_id", "region", "team_name", "team_img"]
    df = df.drop(filter_col, axis=1)
    # df = df.rename(columns={"FULL_NAME": "JUGADOR"})
    # for column in filter_col:
    #     df[column] = df[column].astype(str)
    # df[column] = df[column].str.replace(",", ".").astype(float)
    return df


@st.cache(allow_output_mutation=True)
def load_data_teams():
    return pd.read_csv("data/teams.csv")


df_teams = load_data_teams()  # Cargamos los datos de equipos en el dataframe
df_players = load_data_players()  # Cargamos los datos de jugadores en el dataframe

# Selector de Jugador
sorted_unique_player = df_players.player_name.unique()
all_players = st.sidebar.checkbox(
    "Ver todos los jugadores", key="player_name", value=True
)

if all_players:
    selected_player = st.sidebar.selectbox("JUGADOR", ["Todos"])
else:
    selected_player = st.sidebar.selectbox("JUGADOR", sorted_unique_player)
    compare_players = st.sidebar.checkbox(
        "Comparar jugadores", key="compare_player", value=False
    )

    if compare_players:
        selected_player_2 = st.sidebar.selectbox("JUGADOR 2", sorted_unique_player, index=1)



# Selector de Equipos
sorted_unique_team = sorted(df_teams.team_abbrev.unique())
all_teams = st.sidebar.checkbox("Ver todos los equipos", key="team_abbrev", value=True)

if all_teams:
    selected_team = st.sidebar.multiselect(
        "TEAM", sorted_unique_team, sorted_unique_team
    )
else:
    selected_team = st.sidebar.multiselect("TEAM", sorted_unique_team)


# Filtro el dataframe con los valores seleccionados
if all_players:
    df_selected = df_players[
        (
            df_players.team_abbrev.isin(selected_team)
        )  # & (df_players.POS.isin(selected_pos))
    ]
else:
    if compare_players:
        df_selected = df_players[(df_players.player_name == selected_player) | (df_players.player_name == selected_player_2)]
    else:
        df_selected = df_players[(df_players.player_name == selected_player)]


# Logos de equipos
teams = sorted(df_teams.team_abbrev.unique())
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

player_img_size = st.sidebar.slider("JUGADOR TAMAÑO IMAGEN", 50, 200, 80)
team_img_size = st.sidebar.slider("TEAM TAMAÑO IMAGEN", 50, 130, 60)


# Mostramos el dataframe
with st.container():
    df_players_img = df_selected.copy()
    df_players_img["player_img_url"] = [
        "<img src='"
        + r.player_img
        + f"""' style='display:block;margin-left:auto;margin-right:auto;width:{player_img_size}px;border:0;'>"""
        for ir, r in df_players_img.iterrows()
    ]
    df_players_img["team_img_small_url"] = [
        "<img src='"
        + r.team_img_small
        + f"""' style='display:block;margin-left:auto;margin-right:auto;width:{team_img_size}px;border:0;'>"""
        for ir, r in df_players_img.iterrows()
    ]

    df_players_img = df_players_img.drop(
        ["player_img", "team_img_small", "team_id"], axis=1
    )
    column_names = [
        "player_img_url",
        "player_name",
        "team_abbrev",
        "team_img_small_url",
        "hgt",
        "stre",
        "spd",
        "jmp",
        "endu",
        "ins",
        "dnk",
        "ft",
        "fg",
        "tp",
        "diq",
        "oiq",
        "drb",
        "pss",
        "reb",
    ]

    columns = st.multiselect(
        "Columnas",
        column_names,
        column_names[:10],
        help="Seleccione las columnas a visualizar",
    )

    df_players_img = df_players_img.reindex(columns=columns)

    st.write(df_players_img.to_html(escape=False, index=False), unsafe_allow_html=True)


# Link para descargar el csv
st.sidebar.download_button(
    label="Exportar a CSV", 
    data=df_selected.to_csv(index=False).encode("utf-8"), 
    file_name="NBA_stats.csv", 
    mime="text/csv",
    help="Exporta datos en formato CSV"
)

# Grafico radar
if all_players is False:
    fig = go.Figure()
    team_1 = df_players_img["team_abbrev"].values.tolist()[0]
    color_1 = df_teams[df_teams.team_abbrev == team_1]["color_0"].values.tolist()[0]
    ratings = ["hgt","stre","spd","jmp","endu","ins"]
    df_player_1 = pd.DataFrame(
        dict(
            r=df_players_img[ratings].values.tolist()[0],
            theta=ratings,
        )
    )
    fig.add_trace(go.Scatterpolar(
        r=df_player_1["r"],
        theta=ratings,
        fill='toself',
        marker = dict(color = color_1),
        name=df_players_img["player_name"].values.tolist()[0]
    ))
    if compare_players:
        team_2 = df_players_img["team_abbrev"].values.tolist()[1]
        if team_1 ==  team_2:
            color_2 = df_teams[df_teams.team_abbrev == team_2]["color_2"].values.tolist()[0]
        else:
            color_2 = df_teams[df_teams.team_abbrev == team_2]["color_0"].values.tolist()[0]
        df_player_2 = pd.DataFrame(
            dict(
                r=df_players_img[ratings].values.tolist()[1],
                theta=ratings,
            )
        )
        fig.add_trace(go.Scatterpolar(
            r=df_player_2["r"],
            theta=ratings,
            marker = dict(color = color_2),
            name=df_players_img["player_name"].values.tolist()[1]
        ))

    fig.update_traces(fill="toself")
    fig.update_polars(bgcolor="#ffffff")
    fig.update_polars(angularaxis_showgrid=False)
    fig.update_polars(radialaxis_showgrid=False)

    st.plotly_chart(fig)