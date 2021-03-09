from pathlib import Path
from typing import List, Optional
import warnings

from matplotlib import axes
from matplotlib import patches
import matplotlib.path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CUR_PATH = Path(__file__).resolve().parent
STADIUM_COORDS = pd.read_csv(Path(CUR_PATH, 'data', 'mlbstadiums.csv'), index_col=0)

# transform over x axis
STADIUM_COORDS['y'] *= -1


def plot_stadium(team: str, title: Optional[str] = None, width: Optional[int] = None,
                 height: Optional[int] = None, axis: Optional[axes.Axes] = None) -> axes.Axes:
    """
    Plot the outline of the specified team's stadium using MLBAM coordinates (using pyplot)

    
    Args:
        team: (str)
            Team whose stadium will be plotted
        title: (str), default = name of team
            Optional: Title of plot
        width: (int), default = 5 inches
            Optional: Width of plot
        height: (int), default = 5 inches
            Optional: Height of plot
        axis: (matplotlib.axis.Axes), default = None
            Optional: Axes to plot the stadium against. If None, a new Axes will be created

    Returns:
        A matplotlib.axes.Axes object that was used to generate the stadium render
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


def spraychart(data: pd.DataFrame, team_stadium: str, title: str = '', tooltips: Optional[List['str']] = None,  # pylint: disable=too-many-arguments
               size: int = 100, colorby: str = 'events', legend_title: str = '', width: int = 500,
               height: int = 500) -> axes.Axes:
    """
    Produces a spraychart using statcast data overlayed on specified stadium

    
    Args:
        data: (pandas.DataFrame)
            StatCast pandas.DataFrame of StatCast batter data
        team_stadium: (str)
            Team whose stadium the hits will be overlaid on
        title: (str), default = ''
            Optional: Title of plot
        tooltips: (List[str]), default = None
            Optional: List of variables in data to include as tooltips (Deprecated)
        size: (int), default = 100
            Optional: Size of hit circles on plot
        colorby: (str), default = 'events'
            Optional: Which category to color the mark with. 'events','player', or a column within data
        legend_title: (str), default = based on colorby
            Optional: Title for the legend
        width: (int), default = 500
            Optional: Width of plot (not counting the legend)
        height: (int), default = 500
            Optional: Height of plot

    Returns:
        A matplotlib.axes.Axes object that was used to generate the stadium render and the spraychart
    """

    # pull stadium plot to overlay hits on
    base = plot_stadium(team_stadium, title, width-50, height)

    # only plot pitches where something happened
    sub_data = data.copy().reset_index(drop=True)
    sub_data = sub_data[sub_data['events'].notna()][sub_data['hc_x'].notna()][sub_data['hc_y'].notna()]
    if colorby == 'events':
        sub_data['event'] = sub_data['events'].str.replace('_', ' ').str.title()
        color_label = 'event'
        if not legend_title:
            legend_title = 'Outcome'
    elif colorby == 'player':
        color_label = 'player_name'
        if not legend_title:
            legend_title = 'Player'
    else:
        color_label = colorby
        if not legend_title:
            legend_title = colorby

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

    return base


def plot_bb_profile(df: pd.DataFrame, parameter: Optional[str] = "launch_angle") -> None:
    """Plots a given StatCast parameter split by bb_type

    Args:
        df: (pandas.DataFrame)
            pandas.DataFrame of StatCast batter data (retrieved through statcast, statcast_batter, etc)
        parameter: (str), default = 'launch_angle'
            Optional: Parameter to plot
    """

    bb_types = df["bb_type"].dropna().unique()

    for bb_type in bb_types:
        df_skimmed = df[df.bb_type == bb_type]
        bins = np.arange(df_skimmed[parameter].min(), df_skimmed[parameter].max(), 2)
        plt.hist(df_skimmed[parameter], bins=bins, alpha=0.5, label=bb_type.replace("_", " ").capitalize())
        plt.tick_params(labelsize=12)
