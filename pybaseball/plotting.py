from pathlib import Path
from typing import Any, List, Optional

import matplotlib.axes as axes
import matplotlib.patches as patches
import matplotlib.path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CUR_PATH = Path(__file__).resolve().parent
STADIUM_COORDS = pd.read_csv(Path(CUR_PATH, 'data', 'mlbstadiums.csv'), index_col=0)

# transform over x axis
STADIUM_COORDS['y'] *= -1

# Use altair if available for backwards compatibility, else use pyplot
try:
    import altair as alt
    import warnings

    _ALTAIR_ENABLED = True
    _ALTAIR_WARNING = """
        Altair functionality is deprecated and will be removed in a future version.
        Use pyplot functions instead or remove the altair library to prevent autodetection.
    """
except ImportError:
    _ALTAIR_ENABLED = False

    # Needed so we can still use altair datatypes for now in our func definitions
    class FakeAltair():  # pylint: disable=too-few-public-methods
        Chart = Any
        LayerChart = Any

    alt = FakeAltair()


def plot_stadium_altair(team: str) -> alt.Chart:
    """
    Plot the outline of the specified team's stadium using MLBAM coordinates (using altair)

    Parameters
    ----------
    team: name of team whose stadium you want plotted
    """

    warnings.warn(_ALTAIR_WARNING, category=DeprecationWarning)
    print(f"WARNING: {_ALTAIR_WARNING}")

    coords = STADIUM_COORDS[STADIUM_COORDS['team'] == team.lower()]
    name = list(coords['name'])[0]
    location = list(coords['location'])[0]
    title = {'text': [name], 'subtitle': [location]}
    if team == 'generic':
        title = {'text': ['Generic Stadium']}
    stadium = alt.Chart(coords, title=title).mark_line().encode(
        x=alt.X('x', axis=None, scale=alt.Scale(zero=True)),
        y=alt.Y('y', axis=None, scale=alt.Scale(zero=True)),
        color=alt.Color(
            'segment', scale=alt.Scale(range=['grey']), legend=None
        ),
        order='segment'
    )

    return stadium

# pylint: disable=too-many-arguments


def spraychart_altair(data: pd.DataFrame, team_stadium: str, title: str = '', tooltips: Optional[List['str']] = None,
                      size: int = 100, colorby: str = 'events', legend_title: str = '', width: int = 500,
                      height: int = 500) -> alt.LayerChart:
    """
    Produces a spraychart using statcast data overlayed on specified stadium

    Parameters
    ----------
    data:         statcast batter data
    team_stadium: team whose stadium the hits will be overlaid on
    title:        title of plot
    tooltips:     list of variables in data to include as tooltips
    size:         size of marks on plot
    colorby:      which category to color the mark with. Events or player name.
                  must be 'events' or 'player'
    legend_title: optional title for the legend
    width:        width of plot
    height:       height of plot
    """

    # pull stadium plot to overlay hits on
    base = plot_stadium(team_stadium)
    if team_stadium != 'generic':
        _title = {
            'text': [title],
            'subtitle': [
                f'{base.title["text"][0]}, {base.title["subtitle"][0]}'
            ]
        }
    else:
        _title = {
            'text': [title],
            'subtitle': ['Generic Stadium']
        }
    # remove stadium plot title
    base.title = ''
    # only plot pitches where something happened
    sub_data = data[data['events'].notna()].copy()
    if colorby == 'events':
        sub_data['event'] = sub_data['events'].str.replace('_', ' ').str.title()
        color_label = 'event'
        legend_title = 'Outcome'
    elif colorby == 'player':
        color_label = 'player_name'
        legend_title = 'Player'
    else:
        color_label = colorby
    # scatter plot of hits
    scatter = alt.Chart(sub_data, title=_title).mark_circle(size=size).encode(
        x=alt.X('hc_x:Q', axis=None, scale=alt.Scale(zero=True)),
        y=alt.Y('y:Q', axis=None, scale=alt.Scale(zero=True)),
        color=alt.Color(
            color_label, legend=alt.Legend(title=legend_title)
        )
    ).transform_calculate(
        y='datum.hc_y * -1'
    )
    if tooltips:
        scatter = scatter.encode(tooltip=tooltips)

    plot = alt.layer(base, scatter).resolve_scale(color='independent')
    plot.width = width
    plot.height = height
    del sub_data

    return plot


def plot_stadium_pyplot(team: str, title: Optional[str] = None, width: Optional[int] = None,
                        height: Optional[int] = None, axis: Optional[axes.Axes] = None) -> axes.Axes:
    """
    Plot the outline of the specified team's stadium using MLBAM coordinates (using pyplot)

    Parameters
    ----------
    team: name of team whose stadium you want plotted
    ax:   optional axes to plot the stadium against. If None, a new figure will be created.
    """
    coords = STADIUM_COORDS[STADIUM_COORDS['team'] == team.lower()]

    if not axis:
        name = list(coords['name'])[0]

        stadium = plt.figure()
        if width is not None and height is not None:
            stadium.set_size_inches(width / stadium.dpi, height / stadium.dpi)
        else:
            stadium.set_size_inches(5, 5)
        axis = stadium.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)  # Centering

        axis.set_xlim(0, 250)
        axis.set_ylim(-250, 0)

        axis.set_xticks([])
        axis.set_yticks([])

    segments = set(coords['segment'])

    for segment in segments:
        segment_verts = coords[coords['segment'] == segment][['x', 'y']]
        path = matplotlib.path.Path(segment_verts)
        patch = patches.PathPatch(path, facecolor='None', edgecolor='grey', lw=2)
        axis.add_patch(patch)

    if title is None:
        _title = name
        if team == 'generic':
            _title = 'Generic Stadium'

        plt.title(_title)
    else:
        plt.title(title)

    return axis

# pylint: disable=too-many-arguments


def spraychart_pyplot(data: pd.DataFrame, team_stadium: str, title: str = '', tooltips: Optional[List['str']] = None,
                      size: int = 100, colorby: str = 'events', legend_title: str = '', width: int = 500,
                      height: int = 500) -> axes.Axes:
    """
    Produces a spraychart using statcast data overlayed on specified stadium

    Parameters
    ----------
    data:         statcast batter data
    team_stadium: team whose stadium the hits will be overlaid on
    title:        title of plot
    tooltips:     list of variables in data to include as tooltips (Deprecated)
    size:         size of marks on plot
    colorby:      which category to color the mark with. Events or player name.
                  must be 'events' or 'player'
    legend_title: optional title for the legend
    width:        width of plot
    height:       height of plot
    """

    # pull stadium plot to overlay hits on
    base = plot_stadium_pyplot(team_stadium, title, width-50, height)

    # only plot pitches where something happened
    sub_data = data.copy().reset_index(drop=True)
    sub_data = sub_data[sub_data['events'].notna()][sub_data['hc_x'].notna()][sub_data['hc_y'].notna()]
    if colorby == 'events':
        sub_data['event'] = sub_data['events'].str.replace('_', ' ').str.title()
        color_label = 'event'
        legend_title = 'Outcome'
    elif colorby == 'player':
        color_label = 'player_name'
        legend_title = 'Player'
    else:
        color_label = colorby

    # scatter plot of hits
    scatters = []
    for color in sub_data[color_label].unique():
        color_sub_data = sub_data[sub_data[color_label] == color]
        scatters.append(base.scatter(
            color_sub_data["hc_x"], color_sub_data['hc_y'].mul(-1), size, label=color, alpha=0.5
        ))

    if tooltips:
        warnings.warn(
            "Tooltips are disabled in the pyplot version of spraychart and will be removed in the future",
            category=DeprecationWarning
        )

    plt.legend(handles=scatters, title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.draw()

    plt.show()

    # return plot
    return base


def plot_bb_profile(df: pd.DataFrame, parameter: Optional[str] = "launch_angle") -> None:
    """Plots a given StatCast parameter split by bb_type

    Args:
        df (pd.DataFrame):                   StatCast pd.DataFrame (retrieved through statcast, statcast_batter, etc)
        parameter (Optional[str], optional): Parameter to plot. Defaults to "launch_angle".
    """

    bb_types = df["bb_type"].dropna().unique()

    for bb_type in bb_types:
        df_skimmed = df[df.bb_type == bb_type]
        bins = np.arange(df_skimmed[parameter].min(), df_skimmed[parameter].max(), 2)
        plt.hist(df_skimmed[parameter], bins=bins, alpha=0.5, label=bb_type.replace("_", " ").capitalize())
        plt.tick_params(labelsize=12)


if _ALTAIR_ENABLED:
    plot_stadium = plot_stadium_altair
    spraychart = spraychart_altair
else:
    plot_stadium = plot_stadium_pyplot
    spraychart = spraychart_pyplot
