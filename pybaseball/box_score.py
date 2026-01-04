import datetime
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


def post_process_batting(batter_df, html_table):
    """
       Retrieves the bbref player_id from a html header attribute, determines the starters/positions,
       and cleans up the name
    """
    row_count = 0
    table_soup = BeautifulSoup(html_table, "lxml")
    for row in table_soup.findAll('tr'):
        if 0 < row_count < len(batter_df.index):  # skip the first row of the table plus any trailing rows
            header = row.find('th')

            if 'iz' not in header['class']:
                # first get the player_id for each batter
                batter_df.loc[row_count-1, 'player_id'] = header['data-append-csv']
                name = header.text

                # first check if player is a starter or sub. Subs are indented so start with a space
                if name[0].isspace():
                    batter_df.loc[row_count-1, 'is_starter'] = 'False'
                else:
                    batter_df.loc[row_count-1, 'is_starter'] = 'True'

                # now extract position(s) from the name, everything after the last space is the position, rest is name
                if name != 'Team Totals':
                    name_word_list = name.split(' ')
                    position = name_word_list[len(name_word_list)-1]
                    batter_df.loc[row_count - 1, 'position'] = position
                    batter_df.loc[row_count - 1, 'Batting'] = name.replace(' ' + position, '')

        row_count += 1

    return batter_df


def post_process_pitching(pitcher_df, html_table):
    """
           Retrieves the bbref player_id from a html header attribute, finds the stat in the name,
           and then cleans up the name
    """
    row_count = 0
    table_soup = BeautifulSoup(html_table, "lxml")
    for row in table_soup.findAll('tr'):
        if 0 < row_count < len(pitcher_df.index):  # skip the first row of the table plus any trailing rows
            header = row.find('th')
            # first get the player_id for each pitcher
            pitcher_df.loc[row_count - 1, 'player_id'] = header['data-append-csv']
            name = header.text

            # now extract stat (W/L/S/BS/H), everything after the last comma is part of stat, rest is name
            if name != 'Team Totals':
                name_word_list = name.split(',')
                if len(name_word_list) > 1:
                    stat_string = name_word_list[len(name_word_list) - 1]
                    pitcher_df.loc[row_count - 1, 'Details'] = stat_string  # called Details b/c bbref did for batters
                    pitcher_df.loc[row_count - 1, 'Pitching'] = name.replace(',' + stat_string, '')
        row_count += 1
    return pitcher_df


def normalize_team_abbreviation(input_abbr):
    """
        Baseball Reference is inconsistent in their team name abbreviations, so convert to the one used for box scores
    """

    team_abbr_map = {
        "LAD": "LAN",
        "SDP": "SDN",
        "CHC": "CHN",
        "LAA": "ANA",
        "SFG": "SFN",
        "WSN": "WAS",
        "NYM": "NYN",
        "NYG": "NY1",
        "STL": "SLN",
        "TBR": "TBA",
        "NYY": "NYA",
        "CHW": "CHA",
        "KCR": "KCA",
        "WSH": "WS1",
        "KCA": "KC1",
        "SLB": "SLA"
    }
    output_abbr = input_abbr
    if input_abbr in team_abbr_map:
        output_abbr = team_abbr_map[input_abbr]

    return output_abbr


def box_score(home_team: str, game_date: datetime, doubleheader_id: int):
    """
    Get Baseball Reference box score. Particularly useful for pulling current season box scores before the
    retrosheet data is available for the season.

    :param home_team: 3 char bbref format of teamname, includes AL/NL char for multiteam cities (e.g. LAN)
    :param game_date: datetime object of the game
    :param doubleheader_id: int where 0=no doubleheader, 1=first game, 2=second game
    :return: 4 pandas.DataFrame for the batting and pitching boxscores for the home and away team
    """
    # create the url
    date_str = game_date.strftime("%Y%m%d")
    home_team = normalize_team_abbreviation(home_team)
    boxscore_url = f'https://www.baseball-reference.com/boxes/{home_team}/{home_team}{date_str}{doubleheader_id}.shtml'

    # load content and build soup
    content = requests.get(boxscore_url).content
    if '<h1>Page Not Found (404 error)</h1>' in content.decode('utf-8'):
        raise RuntimeError(f'Unable to parse url {boxscore_url}, please check your inputs')
    soup = BeautifulSoup(content, "lxml")

    # get batting box scores
    # unfortunately the table is initially commented out so find divs the comments are in
    batting_divs = soup.findAll("div", {"id": re.compile('batting$')})
    visitor_batting_table = str(batting_divs[0])  # first one is visitor
    # now parse to get the main table out of the comment
    visitor_batting_table = \
        visitor_batting_table[visitor_batting_table.find('<table'):visitor_batting_table.rfind('</table>') + 8]
    visitor_batting_df = pd.read_html(str(visitor_batting_table))[0]
    visitor_batting_df = post_process_batting(visitor_batting_df, visitor_batting_table)

    home_batting_table = str(batting_divs[1])  # second one is home
    # now parse to get the main table out of the comment
    home_batting_table = \
        home_batting_table[home_batting_table.find('<table'):home_batting_table.rfind('</table>') + 8]
    home_batting_df = pd.read_html(str(home_batting_table))[0]
    home_batting_df = post_process_batting(home_batting_df, home_batting_table)

    # next get the pitcher box scores, similar to batter they are in a comment and one that is a little harder to get to
    # the div we want is the 4th one that starts with "all"
    pitching_wrapper_div = soup.findAll("div", {"id": re.compile('^all_')})
    pitching_html = str(pitching_wrapper_div[3])

    # now just remove all the comment tags from within that div, they are only surrounding valid html (for now)
    pitching_html = pitching_html.replace('<!--', '')
    pitching_html = pitching_html.replace('-->', '')
    pitching_soup = BeautifulSoup(pitching_html, "lxml")

    # finally, find the tables we want from that uncommented html
    pitching_tables = pitching_soup.find_all('table', {"id": re.compile('pitching$')})
    visitor_pitching_table = str(pitching_tables[0]) # first one is visitor
    visitor_pitching_df = pd.read_html(visitor_pitching_table)[0]
    visitor_pitching_df = post_process_pitching(visitor_pitching_df, visitor_pitching_table)

    home_pitching_table = str(pitching_tables[1])  # second one is home
    home_pitching_df = pd.read_html(home_pitching_table)[0]
    home_pitching_df = post_process_pitching(home_pitching_df, home_pitching_table)

    return visitor_batting_df, home_batting_df, visitor_pitching_df, home_pitching_df
