from functools import partial
from pathlib import Path
from typing import List, Optional
import warnings

from matplotlib import axes
from matplotlib import patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pybaseball.utils import pitch_code_to_name_map 

CUR_PATH = Path(__file__).resolve().parent


def _transform_coordinate(coord: pd.Series, center: float, scale: float, sign: float) -> pd.Series:
    return sign * ((coord - center) * scale + center)


def transform_coordinates(coords: pd.DataFrame, scale: float, x_center: float = 125, y_center: float = 199) -> pd.DataFrame:
    x_transform = partial(_transform_coordinate, center=x_center, scale=scale, sign=+1)
    y_transform = partial(_transform_coordinate, center=y_center, scale=scale, sign=-1)
    return coords.assign(x=coords.x.apply(x_transform), y=coords.y.apply(y_transform))


#  transform STADIUM_COORDS to match hc_x, hc_y
#  the scale factor determined heuristically by:
#  - finding the scale of STADIUM_COORDS that will match the outfield dimensions, e.g.,
#    for coors, https://www.seamheads.com/ballparks/ballpark.php?parkID=DEN02
#  - finding the scale for mlbam data so that hc_x, hc_y match the hit_distance_sc field
#  - the center (x=125, y=199) comes from this hardball times article
#  https://tht.fangraphs.com/research-notebook-new-format-for-statcast-data-export-at-baseball-savant/

STADIUM_SCALE = 2.495 / 2.33
STADIUM_COORDS = transform_coordinates(
    pd.read_csv(Path(CUR_PATH, 'data', 'mlbstadiums.csv'), index_col=0), scale=STADIUM_SCALE
)


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


def plot_strike_zone(data: pd.DataFrame, title: str = '', colorby: str = 'pitch_type', legend_title: str = '',
                     annotation: str = 'pitch_type', axis: Optional[axes.Axes] = None) -> axes.Axes:
    """
    Produces a pitches overlaid on a strike zone using StatCast data
    
    Args:
        data: (pandas.DataFrame)
            StatCast pandas.DataFrame of StatCast pitcher data
        title: (str), default = ''
            Optional: Title of plot
        colorby: (str), default = 'pitch_type'
            Optional: Which category to color the mark with. 'pitch_type', 'pitcher', 'description' or a column within data
        legend_title: (str), default = based on colorby
            Optional: Title for the legend
        annotation: (str), default = 'pitch_type'
            Optional: What to annotate in the marker. 'pitch_type', 'release_speed', 'effective_speed',
              'launch_speed', or something else in the data
        axis: (matplotlib.axis.Axes), default = None
            Optional: Axes to plot the strike zone on. If None, a new Axes will be created
    Returns:
        A matplotlib.axes.Axes object that was used to generate the pitches overlaid on the strike zone
    """
    
    # some things to auto adjust formatting
    # make the markers really visible when fewer pitches
    alpha_markers = min(0.8, 0.5 + 1 / data.shape[0])
    alpha_text = alpha_markers + 0.2
    
    # define Matplotlib figure and axis
    if axis is None:
        fig, axis = plt.subplots()

    # add home plate to plot 
    home_plate_coords = [[-0.71, 0], [-0.85, -0.5], [0, -1], [0.85, -0.5], [0.71, 0]]
    axis.add_patch(patches.Polygon(home_plate_coords,
                                   edgecolor = 'darkgray',
                                   facecolor = 'lightgray',
                                   zorder = 0.1))
    
    # add strike zone to plot, technically the y coords can vary by batter
    axis.add_patch(patches.Rectangle((-0.71, 1.5), 2*0.71, 2,
                 edgecolor = 'lightgray',
                 fill=False,
                 lw=3,
                 zorder = 0.1))
    
    # legend_title = ""
    color_label = ""
    
    # to avoid the SettingWithCopyWarning error
    sub_data = data.copy().reset_index(drop=True)
    if colorby == 'pitch_type':
        color_label = 'pitch_type'
        
        if not legend_title:
            legend_title = 'Pitch Type'
            
    elif colorby == 'description':
        values = sub_data.loc[:, 'description'].str.replace('_', ' ').str.title()
        sub_data.loc[:, 'desc'] = values
        color_label = 'desc'
        
        if not legend_title:
            legend_title = 'Pitch Description'
    elif colorby == 'pitcher':
        color_label = 'player_name'
        
        if not legend_title:
            legend_title = 'Pitcher'
            
    elif colorby == "events":
        # only things where something happened
        sub_data = sub_data[sub_data['events'].notna()]
        sub_data['event'] = sub_data['events'].str.replace('_', ' ').str.title()
        color_label = 'event'
        
        if not legend_title:
            legend_title = 'Outcome'
    
    else:
        color_label = colorby
        if not legend_title:
            legend_title = colorby
        
    scatters = []
    for color in sub_data[color_label].unique():
        color_sub_data = sub_data[sub_data[color_label] == color]
        scatters.append(axis.scatter(
            color_sub_data["plate_x"],
            color_sub_data['plate_z'],
            s = 10**2,
            label = pitch_code_to_name_map[color] if color_label == 'pitch_type' else color,
            alpha = alpha_markers
        ))
        
        # add an annotation at the center of the marker
        if annotation:
            for i, pitch_coord in zip(color_sub_data.index, zip(color_sub_data["plate_x"], color_sub_data['plate_z'])):
                label_formatted = color_sub_data.loc[i, annotation]
                label_formatted = label_formatted if not pd.isna(label_formatted) else ""
                
                # these are numbers, format them that way
                if annotation in ["release_speed", "effective_speed", "launch_speed"] and label_formatted != "":
                    label_formatted = "{:.0f}".format(label_formatted)
                
                axis.annotate(label_formatted,
                            pitch_coord,
                            size = 7,
                            ha = 'center',
                            va = 'center',
                            alpha = alpha_text)

    axis.set_xlim(-4, 4)
    axis.set_ylim(-1.5, 7)
    axis.axis('off')

    axis.legend(handles=scatters, title=legend_title, bbox_to_anchor=(0.7, 1), loc='upper left')
    
    plt.title(title)
    plt.show()

    return axis


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


def plot_teams(data: pd.DataFrame, x_axis: str, y_axis: str, title: Optional[str] = None) -> None:
    """Plots a scatter plot with each MLB team

    Args:
        data: (pandas.DataFrame)
            pandas.DataFrame of Fangraphs team data (retrieved through team_batting or team_pitching)
        x_axis: (str)
            Stat name to be plotted as the x_axis of the chart
        y_axis: (str)
            Stat name to be plotted as the y_axis of the chart
        title: (str), default = None
            Optional: Title of the plot
    """

    data = data[['Team', x_axis, y_axis]]

    fig, ax = plt.subplots()

    for index, row in data.iterrows():

        # If there is a logo image for the corresponding team, plot the Team's logo image
        try:
            # Get path of team logo
            path = Path(CUR_PATH, '../docs/images/logos', f"{row['Team']}.png")

            # Read in the image from the folder location
            img = OffsetImage(plt.imread(path, format="png"), zoom=.3)

            # Convert the image into a plottable object
            ab = AnnotationBbox(img, (float(row[x_axis]), float(row[y_axis])), frameon=False)

            # Plot the MLB logo
            ax.add_artist(ab)

        # If there is no logo image for the corresponding team, just plot the Team's Abbreviation
        except FileNotFoundError:
            plt.text(float(row[x_axis]), float(row[y_axis]), row['Team'], fontsize=20, weight='bold')






    # add some spacing to the x axis and y axis so the logos stay within the bounds of the chart
    x_axis_spacing = (data[x_axis].max() - data[x_axis].min()) * .1
    y_axis_spacing = (data[y_axis].max() - data[y_axis].min()) * .1

    # set the axis with the spacing from above
    plt.xlim([data[x_axis].min() - x_axis_spacing, data[x_axis].max() + x_axis_spacing])
    plt.ylim([data[y_axis].min() - y_axis_spacing, data[y_axis].max() + y_axis_spacing])

    # Plot league average for y axis variable
    plt.axhline(y=data[y_axis].mean(), color='k', linestyle='-')
    plt.text(data[x_axis].min() - x_axis_spacing * .9, data[y_axis].mean() + y_axis_spacing * .1, 'league average')

    # Plot league average for x axis variable
    plt.axvline(x=data[x_axis].mean(), color='k', linestyle='-')
    plt.text(data[x_axis].mean() + x_axis_spacing * .05, data[y_axis].min() - y_axis_spacing * .8, 'league average',
             rotation=90)

    # Add title and labels
    if not title:
        title = f'Plot of Team {x_axis}/Team {y_axis}'

    plt.title(title)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)

    plt.show()
