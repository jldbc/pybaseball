import altair as alt
import pandas as pd
from pathlib import Path


CUR_PATH = Path(__file__).resolve().parent
STADIUM_COORDS = pd.read_csv(
    Path(CUR_PATH, 'mlbstadiums.csv'), index_col=0
)
# transform over x axis
STADIUM_COORDS['y'] *= -1


def plot_stadium(team):
    """
    Plot the outline of the specified team's stadium using MLBAM coordinates

    Parameters
    ----------
    team: name of team whose stadium you want plotted
    """
    coords = STADIUM_COORDS[STADIUM_COORDS['team'] == team.lower()]
    name = list(coords['name'])[0]
    location = list(coords['location'])[0]
    title = {'text': [name], 'subtitle': [location]}
    if team == 'generic':
        title = 'Generic Stadium'
    stadium = alt.Chart(coords, title=title).mark_line().encode(
        x=alt.X('x', axis=None, scale=alt.Scale(zero=True)),
        y=alt.Y('y', axis=None, scale=alt.Scale(zero=True)),
        color=alt.Color(
            'segment', scale=alt.Scale(range=['grey']), legend=None
        ),
        order='segment'
    )

    return stadium


def spraychart(data, team_stadium, title='', tooltips=[], size=100,
               colorby='events', legend_title='', width=500, height=500):
    """
    Produces a spraychart using statcast data overlayed on specified stadium

    Parameters
    ----------
    data: statcast batter data
    team_stadium: team whose stadium the hits will be overlaid on
    title: title of plot
    tooltips: list of variables in data to include as tooltips
    size: size of marks on plot
    colorby: which category to color the mark with. Events or player name.
           must be 'events' or 'name'
    legend_title: optional title for the legend
    width: width of plot
    height: height of plot
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
        tooltip=tooltips,
        color=alt.Color(
            color_label, legend=alt.Legend(title=legend_title)
        )
    ).transform_calculate(
        y='datum.hc_y * -1'
    )

    plot = alt.layer(base, scatter).resolve_scale(color='independent')
    plot.width = width
    plot.height = height
    del sub_data

    return plot
