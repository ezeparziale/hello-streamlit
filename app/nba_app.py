import gettext

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static

# Inicialización gettext
_ = gettext.gettext

# Configuración pagina streamlit
st.set_page_config(page_title="Demo NBA", layout="wide", page_icon=":basketball:")


# Idioma
_ = gettext.gettext

CHOICES = {"en": "English", "es": "Spanish"}


def format_func(option):
    return CHOICES[option]


idioma = st.sidebar.selectbox("", options=list(CHOICES.keys()), format_func=format_func)

if idioma == "en":
    en = gettext.translation("en", localedir="app/locales", languages=["en"])
    en.install()
    _ = en.gettext
else:
    es = gettext.translation("es", localedir="app/locales", languages=["es"])
    es.install()
    _ = es.gettext


# Configuración pandas
pd.options.display.float_format = "{:,.1f}".format  # Para mostrar con dos decimales

# Selector de vista
CHOICES_MODE = {0: _("Jugadores"), 1: _("Equipos")}


def format_func_mode(option):
    return CHOICES_MODE[option]


mode_view = st.sidebar.selectbox(
    _("Vista"),
    options=list(CHOICES_MODE.keys()),
    format_func=format_func_mode,
    key="choices_mode",
)
print(mode_view)
# Bara lateral
st.sidebar.header(_("Opciones:"))

# Titulo cabecera
t1, t2 = st.columns((0.08, 1))
t1.image("app/img/logo.png", width=50)
t2.title(_("NBA estadísticas"))


# Carga de datos
@st.cache_data()
def load_data_players():
    df = pd.read_csv("app/data/players.csv")
    filter_col = ["conference_id", "division_id", "region", "team_name", "team_img"]
    df = df.drop(filter_col, axis=1)
    return df


@st.cache_data()
def load_data_teams():
    df_teams = pd.read_csv("app/data/teams.csv")
    df_divisions = pd.read_csv("app/data/divisions.csv")
    df_conferences = pd.read_csv("app/data/conferences.csv")
    df_stadiums = pd.read_csv(
        "app/data/stadiums.csv", usecols=["team_id", "arena", "latitude", "longitude"]
    )
    df_teams = pd.merge(df_teams, df_divisions)
    df_teams = pd.merge(df_teams, df_conferences)
    df_teams = pd.merge(df_teams, df_stadiums)
    return df_teams


df_teams = load_data_teams()  # Cargamos los datos de equipos en el dataframe
df_players = load_data_players()  # Cargamos los datos de jugadores en el dataframe

# Logos de equipos
teams = sorted(df_teams.team_abbrev.unique())
teams_list = []
for team in teams:
    path_team = "app/img/teams/" + team + ".png"
    teams_list.append(path_team)

with st.container():
    st.image(teams_list, width=45, caption=teams)


CHOICES_TEAM = {0: _("Imagen+Nombre"), 1: _("Solo imagen"), 2: _("Solo nombre")}

if mode_view == 0:
    # Selector de Jugador
    sorted_unique_player = df_players.player_name.unique()
    all_players = st.sidebar.checkbox(
        _("Ver todos los jugadores"), key="player_name", value=True
    )

    if not all_players:
        selected_player = st.sidebar.selectbox(_("JUGADOR 1"), sorted_unique_player)
        compare_players = st.sidebar.checkbox(
            _("Comparar jugadores"), key="compare_player", value=False
        )

        if compare_players:
            selected_player_2 = st.sidebar.selectbox(
                _("JUGADOR 2"), sorted_unique_player, index=1
            )

    # Selector de Equipos
    sorted_unique_team = sorted(df_teams.team_abbrev.unique())
    all_teams = st.sidebar.checkbox(
        _("Ver todos los equipos"), key="team_abbrev", value=True
    )

    if all_teams:
        selected_team = st.sidebar.multiselect(
            _("Equipos"), sorted_unique_team, sorted_unique_team
        )
    else:
        selected_team = st.sidebar.multiselect(_("Equipos"), sorted_unique_team)

    # Filtro el dataframe con los valores seleccionados
    if all_players:
        df_selected = df_players[(df_players.team_abbrev.isin(selected_team))]
    else:
        if compare_players:
            df_selected = df_players[
                (df_players.player_name == selected_player)
                | (df_players.player_name == selected_player_2)
            ]
        else:
            df_selected = df_players[(df_players.player_name == selected_player)]

    # Subtitulo
    st.write(
        _("Set de datos: ")
        + str(df_selected.shape[0])
        + _(" filas y ")
        + str(df_selected.shape[1])
        + _(" columnas")
    )

    # Link para descargar el csv
    st.sidebar.download_button(
        label=_("Exportar a CSV"),
        data=df_selected.to_csv(index=False).encode("utf-8"),
        file_name="NBA_stats.csv",
        mime="text/csv",
        help=_("Exporta datos en formato CSV"),
    )

    # Personalización tabla
    CHOICES_PLAYER = {0: _("Imagen+Nombre"), 1: _("Solo imagen"), 2: _("Solo nombre")}

    def format_func_player(option):
        return CHOICES_PLAYER[option]

    choices_player = st.sidebar.selectbox(
        _("Personalización jugador"),
        options=list(CHOICES_PLAYER.keys()),
        format_func=format_func_player,
        key="choices_player",
    )

    if choices_player in [0, 1]:
        player_img_size = st.sidebar.slider(_("JUGADOR TAMAÑO IMAGEN"), 50, 200, 80)

    def format_func_team(option):
        return CHOICES_TEAM[option]

    choices_team = st.sidebar.selectbox(
        _("Personalización Equipo"),
        options=list(CHOICES_TEAM.keys()),
        format_func=format_func_team,
        key="choices_team",
    )

    if choices_team in [0, 1]:
        team_img_size = st.sidebar.slider(_("TEAM TAMAÑO IMAGEN"), 50, 130, 60)

    # Mostramos el dataframe
    with st.container():
        df_players_img = df_selected.copy()
        df_players_img["player_img_url"] = [
            f"<img src='{r.player_img}' style='display:block;margin-left:auto;margin-right:auto;width:{player_img_size}px;border:0;'>"
            if choices_player == 1
            else f"<div class='column' align=center> {r.player_name} </div>"
            if choices_player == 2
            else f"<img src='{r.player_img}' style='display:block;margin-left:auto;margin-right:auto;width:{player_img_size}px;border:0;'>"
            + f"<div class='column' align=center> {r.player_name} </div>"
            for ir, r in df_players_img.iterrows()
        ]
        df_players_img["team_img_small_url"] = [
            f"<img src='{r.team_img_small}' style='display:block;margin-left:auto;margin-right:auto;width:{team_img_size}px;border:0;'>"
            if choices_team == 1
            else f"<div class='column' align=center> {r.team_abbrev} </div>"
            if choices_team == 2
            else f"<img src='{r.team_img_small}' style='display:block;margin-left:auto;margin-right:auto;width:{team_img_size}px;border:0;'>"
            + f"<div class='column' align=center> {r.team_abbrev} </div>"
            for ir, r in df_players_img.iterrows()
        ]

        df_players_img = df_players_img.drop(
            ["player_img", "team_img_small", "team_id"], axis=1
        )
        column_names = [
            "player_img_url",
            "team_img_small_url",
            "pos",
            "height",
            "weight",
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

        column_names[0] = _("Jugador")
        column_names[1] = _("Equipo")
        column_names[2] = _("Posición")
        column_names[3] = _("Altura")
        column_names[4] = _("Peso")

        df_players_img_small = df_players_img.copy()

        df_players_img_small.rename(
            columns={
                "player_img_url": _("Jugador"),
                "team_img_small_url": _("Equipo"),
                "pos": _("Posición"),
                "height": _("Altura"),
                "weight": _("Peso"),
            },
            inplace=True,
        )

        df_players_img_small = df_players_img_small.reindex(columns=column_names)
        st.write(
            df_players_img_small.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )

    # Linea entre tabla y radar
    st.write("")

    # Grafico radar
    if all_players is False:
        option_color_team_1 = st.sidebar.selectbox(
            _("Colores del equipo 1"), ("color_0", "color_1", "color_2")
        )

        columns = st.multiselect(
            _("Caracteristicas del jugador"),
            column_names[5:],
            column_names[5:10],
            help=_("Seleccione las caracteristicas a comparar"),
        )

        fig = go.Figure()
        team_1 = df_players_img["team_abbrev"].values.tolist()[0]
        color_1 = df_teams[df_teams.team_abbrev == team_1][
            option_color_team_1
        ].values.tolist()[0]
        ratings = columns  # ["hgt","stre","spd","jmp","endu","ins","reb"]
        df_player_1 = pd.DataFrame(
            dict(
                r=df_players_img[ratings].values.tolist()[0],
                theta=ratings,
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=df_player_1["r"],
                theta=ratings,
                fill="toself",
                marker=dict(color=color_1),
                name=df_players_img["player_name"].values.tolist()[0],
            )
        )
        if compare_players:
            option_color_team_2 = st.sidebar.selectbox(
                _("Colores del equipo 2"), ("color_0", "color_1", "color_2")
            )

            team_2 = df_players_img["team_abbrev"].values.tolist()[1]
            if team_1 == team_2 and option_color_team_1 == option_color_team_2:
                color_2 = df_teams[df_teams.team_abbrev == team_2][
                    "color_2"
                ].values.tolist()[0]
            else:
                color_2 = df_teams[df_teams.team_abbrev == team_2][
                    option_color_team_2
                ].values.tolist()[0]
            df_player_2 = pd.DataFrame(
                dict(
                    r=df_players_img[ratings].values.tolist()[1],
                    theta=ratings,
                )
            )
            fig.add_trace(
                go.Scatterpolar(
                    r=df_player_2["r"],
                    theta=ratings,
                    marker=dict(color=color_2),
                    name=df_players_img["player_name"].values.tolist()[1],
                )
            )

        fig.update_traces(fill="toself")
        fig.update_polars(bgcolor="#ffffff")
        fig.update_polars(angularaxis_showgrid=False)
        fig.update_polars(radialaxis_showgrid=False)

        st.plotly_chart(fig)

    # Referencias
    st.markdown(_("#### Referencias:"))
    st.markdown(
        "hgt: "
        + _("altura, que influye en casi todo")
        + " \n"
        + "stre: "
        + _(
            "fuerza, que influye en la defensa, el rebote y la anotación en el poste bajo"
        )
        + "  \n"
        + "spd: "
        + _(
            "velocidad, que influye en el manejo del balón, contraataques rápidos y defensa"
        )
        + "  \n"
        + "jmp: "
        + _(
            "salto, que influye en la finalización en el aro, el rebote, el bloqueo y la defensa"
        )
        + "  \n"
        + "endu: "
        + _(
            "resistencia, que determina qué tan rápido se degradan las habilidades de un jugador cuando se cansa"
        )
        + "  \n"
        + "ins: "
        + _("anotación en el poste bajo")
        + "  \n"
        + "dnk: "
        + _("volcadas / bandejas")
        + "  \n"
        + "ft: "
        + _("lanzamiento de tiros libres")
        + "  \n"
        + "fg: "
        + _("habilidad de tiro en suspensión de 2 puntos")
        + "  \n"
        + "tp: "
        + _("tiro de 3 puntos")
        + "  \n"
        + "oiq: "
        + _("coeficiente intelectual ofensivo")
        + "  \n"
        + "diq: "
        + _("coeficiente intelectual defensivo")
        + "  \n"
        + "drb: "
        + _("regatear")
        + "  \n"
        + "pd: "
        + _("pasando")
        + "  \n"
        + "reb: "
        + _("rebote")
    )

if mode_view == 1:
    # Selector de Equipos
    sorted_unique_team = sorted(df_teams.team_abbrev.unique())
    all_teams = st.sidebar.checkbox(
        _("Ver todos los equipos"), key="team_abbrev", value=True
    )

    if all_teams:
        # Selector de conferencias
        sorted_unique_conference = sorted(df_teams.conference.unique())
        all_conferences = st.sidebar.checkbox(
            _("Ver todos las conferencias"), key="conference", value=True
        )

        if all_conferences:
            # Selector de divisiones
            sorted_unique_division = sorted(df_teams.division.unique())
            all_divisions = st.sidebar.checkbox(
                _("Ver todos las divisones"), key="division", value=True
            )

            if not all_divisions:
                selected_division = st.sidebar.selectbox(
                    _("Divisiones"), sorted_unique_division
                )
        else:
            selected_conference = st.sidebar.selectbox(
                _("Conferencias"), sorted_unique_conference
            )
    else:
        selected_team = st.sidebar.selectbox(_("Equipos"), sorted_unique_team)

    def format_func_team(option):
        return CHOICES_TEAM[option]

    choices_team = st.sidebar.selectbox(
        _("Personalización Equipo"),
        options=list(CHOICES_TEAM.keys()),
        format_func=format_func_team,
        key="choices_team",
    )

    if choices_team in [0, 1]:
        team_img_size = st.sidebar.slider(_("TEAM TAMAÑO IMAGEN"), 50, 130, 60)

    # Filtro el dataframe con los valores seleccionados
    df_selected = df_teams.copy()
    if not all_teams:
        df_selected = df_selected[(df_selected.team_abbrev.isin([selected_team]))]
    else:
        if not all_conferences:
            df_selected = df_selected[
                (df_selected.conference.isin([selected_conference]))
            ]
        else:
            if not all_divisions:
                df_selected = df_selected[
                    (df_selected.division.isin([selected_division]))
                ]

    with st.container():
        df_teams_img = df_selected.copy()
        df_teams_img["team_img_small_url"] = [
            f"<img src='{r.team_img_small}' style='display:block;margin-left:auto;margin-right:auto;width:{team_img_size}px;border:0;'>"
            if choices_team == 1
            else f"<div class='column' align=center> {r.team_abbrev} </div>"
            if choices_team == 2
            else f"<img src='{r.team_img_small}' style='display:block;margin-left:auto;margin-right:auto;width:{team_img_size}px;border:0;'>"
            + f"<div class='column' align=center> {r.team_abbrev} </div>"
            for ir, r in df_teams_img.iterrows()
        ]

        df_teams_img = df_teams_img.drop(
            [
                "team_id",
                "conference_id",
                "division_id",
                "team_abbrev",
                "colors",
                "team_img",
                "team_img_small",
                "color_0",
                "color_1",
                "color_2",
            ],
            axis=1,
        )
        column_names = [
            "team_img_small_url",
            "region",
            "team_name",
            "arena",
            "conference",
            "division",
        ]

        column_names[0] = _("Logo")
        column_names[1] = _("Región")
        column_names[2] = _("Equipo")
        column_names[3] = _("Arena")
        column_names[4] = _("Conferencia")
        column_names[5] = _("División")

        df_teams_img_small = df_teams_img.copy()

        df_teams_img_small.rename(
            columns={
                "team_img_small_url": _("Logo"),
                "region": _("Región"),
                "team_name": _("Equipo"),
                "arena": _("Arena"),
                "conference": _("Conferencia"),
                "division": _("División"),
            },
            inplace=True,
        )

        df_teams_img_small = df_teams_img_small.reindex(columns=column_names)
        st.write(
            df_teams_img_small.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )

        st.write("")

        m = folium.Map(location=[34.94, -96.69], zoom_start=4.4)

        for i in range(0, len(df_teams_img_small)):
            folium.Marker(
                location=[
                    df_teams_img.iloc[i]["latitude"],
                    df_teams_img.iloc[i]["longitude"],
                ],
                popup=df_teams_img_small.iloc[i][_("Equipo")],
                icon=folium.DivIcon(html=df_teams_img_small.iloc[i][_("Logo")]),
            ).add_to(m)

        folium_static(m, width=910, height=500)
