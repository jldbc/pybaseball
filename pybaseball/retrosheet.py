"""
Retrosheet Data Notice:

Recipients of Retrosheet data are free to make any desired use of
the information, including (but not limited to) selling it,
giving it away, or producing a commercial product based upon the
data.  Retrosheet has one requirement for any such transfer of
data or product development, which is that the following
statement must appear prominently:

     The information used here was obtained free of
     charge from and is copyrighted by Retrosheet.  Interested
     parties may contact Retrosheet at "www.retrosheet.org".

Retrosheet makes no guarantees of accuracy for the information
that is supplied. Much effort is expended to make our website
as correct as possible, but Retrosheet shall not be held
responsible for any consequences arising from the use the
material presented here. All information is subject to corrections
as additional data are received. We are grateful to anyone who
discovers discrepancies and we appreciate learning of the details.
"""
import pandas as pd
from pybaseball.utils import get_text_file
from datetime import datetime
from io import StringIO
from github import Github
import os
from getpass import getuser, getpass
from github.GithubException import RateLimitExceededException
import warnings

gamelog_columns = [
    'date', 'game_num', 'day_of_week', 'visiting_team',
    'visiting_team_league', 'visiting_team_game_num', 'home_team',
    'home_team_league', 'home_team_game_num', 'visiting_score',
    'home_score', 'num_outs', 'day_night', 'completion_info',
    'forfeit_info', 'protest_info', 'park_id', 'attendance',
    'time_of_game_minutes', 'visiting_line_score',
    'home_line_score', 'visiting_abs', 'visiting_hits',
    'visiting_doubles', 'visiting_triples', 'visiting_homeruns',
    'visiting_rbi', 'visiting_sac_hits', 'visiting_sac_flies',
    'visiting_hbp', 'visiting_bb', 'visiting_iw', 'visiting_k',
    'visiting_sb', 'visiting_cs', 'visiting_gdp', 'visiting_ci',
    'visiting_lob', 'visiting_pitchers_used',
    'visiting_individual_er', 'visiting_er', 'visiting_wp',
    'visiting_balks', 'visiting_po', 'visiting_assists',
    'visiting_errors', 'visiting_pb', 'visiting_dp',
    'visiting_tp', 'home_abs', 'home_hits', 'home_doubles',
    'home_triples', 'home_homeruns', 'home_rbi',
    'home_sac_hits', 'home_sac_flies', 'home_hbp', 'home_bb',
    'home_iw', 'home_k', 'home_sb', 'home_cs', 'home_gdp',
    'home_ci', 'home_lob', 'home_pitchers_used',
    'home_individual_er', 'home_er', 'home_wp', 'home_balks',
    'home_po', 'home_assists', 'home_errors', 'home_pb',
    'home_dp', 'home_tp', 'ump_home_id', 'ump_home_name',
    'ump_first_id', 'ump_first_name', 'ump_second_id',
    'ump_second_name', 'ump_third_id', 'ump_third_name',
    'ump_lf_id', 'ump_lf_name', 'ump_rf_id', 'ump_rf_name',
    'visiting_manager_id', 'visiting_manager_name',
    'home_manager_id', 'home_manager_name',
    'winning_pitcher_id', 'winning_pitcher_name',
    'losing_pitcher_id', 'losing_pitcher_name',
    'save_pitcher_id', 'save_pitcher_name',
    'game_winning_rbi_id', 'game_winning_rbi_name',
    'visiting_starting_pitcher_id',
    'visiting_starting_pitcher_name',
    'home_starting_pitcher_id', 'home_starting_pitcher_name',
    'visiting_1_id', 'visiting_1_name', 'visiting_1_pos',
    'visiting_2_id', 'visiting_2_name', 'visiting_2_pos',
    'visiting_2_id.1', 'visiting_3_name', 'visiting_3_pos',
    'visiting_4_id', 'visiting_4_name', 'visiting_4_pos',
    'visiting_5_id', 'visiting_5_name', 'visiting_5_pos',
    'visiting_6_id', 'visiting_6_name', 'visiting_6_pos',
    'visiting_7_id', 'visiting_7_name', 'visiting_7_pos',
    'visiting_8_id', 'visiting_8_name', 'visiting_8_pos',
    'visiting_9_id', 'visiting_9_name', 'visiting_9_pos',
    'home_1_id', 'home_1_name', 'home_1_pos', 'home_2_id',
    'home_2_name', 'home_2_pos', 'home_3_id', 'home_3_name',
    'home_3_pos', 'home_4_id', 'home_4_name', 'home_4_pos',
    'home_5_id', 'home_5_name', 'home_5_pos', 'home_6_id',
    'home_6_name', 'home_6_pos', 'home_7_id', 'home_7_name',
    'home_7_pos', 'home_8_id', 'home_8_name', 'home_8_pos',
    'home_9_id', 'home_9_name', 'home_9_pos', 'misc',
    'acquisition_info'
]

schedule_columns = [
    'date', 'game_num', 'day_of_week', 'visiting_team', 'visiting_team_league',
    'visiting_team_game_num', 'home_team', 'home_team_league',
    'home_team_game_num', 'day_night', 'postponement_cancellation',
    'date_of_makeup'
]

parkcode_columns = [
    'park_id', 'name', 'nickname', 'city', 'state', 'open', 'close', 'league', 'notes'
]

roster_columns = [
    'player_id', 'last_name', 'first_name', 'bats', 'throws', 'team', 'position'
]

gamelog_url = 'https://raw.githubusercontent.com/chadwickbureau/retrosheet/master/gamelog/GL{}.TXT'
schedule_url = 'https://raw.githubusercontent.com/chadwickbureau/retrosheet/master/schedule/{}SKED.TXT'
parkid_url = 'https://raw.githubusercontent.com/chadwickbureau/retrosheet/master/misc/parkcode.txt'
roster_url = 'https://raw.githubusercontent.com/chadwickbureau/retrosheet/master/rosters/{}{}.ROS'
event_url = 'https://raw.githubusercontent.com/chadwickbureau/retrosheet/master/event/{}/{}'

def events(season, type='regular', export_dir='.'):
    """
    Pulls retrosheet event files for an entire season. The `type` argument
    specifies whether to pull regular season, postseason or asg files. Valid
    arguments are 'regular', 'post', and 'asg'.

    Right now, pybaseball does not parse the retrosheet files but downloads and
    saves them.
    """
    GH_TOKEN=os.getenv('GH_TOKEN', '')
    if not os.path.exists(export_dir):
        os.mkdir(export_dir)

    try:
        g = Github(GH_TOKEN)
        repo = g.get_repo('chadwickbureau/retrosheet')
        tree = repo.get_git_tree('master')
        for t in tree.tree:
            if t.path == 'event':
                subtree = t

        subtree = repo.get_git_tree(subtree.sha)
        for t in subtree.tree:
            if t.path == type:
                subsubtree = t

        event_files = [t.path for t in repo.get_git_tree(subsubtree.sha).tree if str(season) in t.path]
        if len(event_files) == 0:
            raise ValueError(f'Event files not available for {season}')
    except RateLimitExceededException:
        warnings.warn(
            'Github rate limit exceeded. Cannot check if the file you want exists.',
            UserWarning
        )

    for filename in event_files:
        print(f'Downloading {filename}')
        s = get_text_file(event_url.format(type, filename))
        with open(os.path.join(export_dir, filename), 'w') as f:
            f.write(s)

def rosters(season):
    """
    Pulls retrosheet roster files for an entire season
    """
    GH_TOKEN=os.getenv('GH_TOKEN', '')

    try:
        g = Github(GH_TOKEN)
        repo = g.get_repo('chadwickbureau/retrosheet')
        tree = repo.get_git_tree('master')
        for t in tree.tree:
            if t.path == 'rosters':
                subtree = t

        rosters = [t.path for t in repo.get_git_tree(subtree.sha).tree if str(season) in t.path]
        if len(rosters) == 0:
            raise ValueError(f'Rosters not available for {season}')
    except RateLimitExceededException:
        warnings.warn(
            'Github rate limit exceeded. Cannot check if the file you want exists.',
            UserWarning
        )

    df_list = [_roster(team = r[:3], season = season, checked=False) for r in rosters]

    return pd.concat(df_list)

def _roster(team, season, checked = False):
    """
    Pulls retrosheet roster files
    """
    GH_TOKEN=os.getenv('GH_TOKEN', '')

    if not checked:
        g = Github(GH_TOKEN)
        try:
            repo = g.get_repo('chadwickbureau/retrosheet')
            tree = repo.get_git_tree('master')
            for t in tree.tree:
                if t.path == 'rosters':
                    subtree = t

            rosters = [t.path for t in repo.get_git_tree(subtree.sha).tree]
            file_name = f'{team}{season}.ROS'
            if file_name not in rosters:
                raise ValueError(f'Roster not available for {team} in {season}')
        except RateLimitExceededException:
            warnings.warn(
                'Github rate limit exceeded. Cannot check if the file you want exists.',
                UserWarning
            )

    s = get_text_file(roster_url.format(team, season))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = roster_columns
    return data

def park_codes():
    """
    Pulls retrosheet Park IDs
    """
    s = get_text_file(parkid_url)
    data = pd.read_csv(StringIO(s), sep=',', quotechar='"')
    data.columns = parkcode_columns
    return data

def schedules(season):
    """
    Pull retrosheet schedule for a given season
    """
    GH_TOKEN=os.getenv('GH_TOKEN', '')
    # validate input
    g = Github(GH_TOKEN)
    repo = g.get_repo('chadwickbureau/retrosheet')
    schedules = [f.path[f.path.rfind('/')+1:] for f in repo.get_contents('schedule')]
    file_name = f'{season}SKED.TXT'

    if file_name not in schedules:
        raise ValueError(f'Schedule not available for {season}')
    s = get_text_file(schedule_url.format(season))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = schedule_columns
    return data

def season_game_logs(season):
    """
    Pull Retrosheet game logs for a given season
    """
    GH_TOKEN=os.getenv('GH_TOKEN', '')
    # validate input
    g = Github(GH_TOKEN)
    repo = g.get_repo('chadwickbureau/retrosheet')
    gamelogs = [f.path[f.path.rfind('/')+1:] for f in repo.get_contents('gamelog')]
    file_name = f'GL{season}.TXT'

    if file_name not in gamelogs:
        raise ValueError(f'Season game logs not available for {season}')
    s = get_text_file(gamelog_url.format(season))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def world_series_logs():
    """
    Pull Retrosheet World Series Game Logs
    """
    s = get_text_file(gamelog_url.format('WS'))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def all_star_game_logs():
    """
    Pull Retrosheet All Star Game Logs
    """
    s = get_text_file(gamelog_url.format('AS'))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def wild_card_logs():
    """
    Pull Retrosheet Wild Card Game Logs
    """
    s = get_text_file(gamelog_url.format('WC'))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def division_series_logs():
    """
    Pull Retrosheet Division Series Game Logs
    """
    s = get_text_file(gamelog_url.format('DV'))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def lcs_logs():
    """
    Pull Retrosheet LCS Game Logs
    """
    s = get_text_file(gamelog_url.format('LC'))
    data = pd.read_csv(StringIO(s), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data
