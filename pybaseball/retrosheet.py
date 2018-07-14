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
from pybaseball.utils import get_zip_file
from datetime import datetime


gamelog_columns = ['date', 'game_num', 'day_of_week', 'visiting_team',
                   'visiting_team_league', 'visiting_game_num', 'home_team',
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
                   'visiting_individual_er', 'visiting_er', 'visiting__wp',
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
                   'acquisition_info']
gamelog_url = 'http://www.retrosheet.org/gamelogs/gl{}.zip'
world_series_url = 'http://www.retrosheet.org/gamelogs/glws.zip'
all_star_url = 'http://www.retrosheet.org/gamelogs/glas.zip'
wild_card_url = 'http://www.retrosheet.org/gamelogs/glwc.zip'
division_series_url = 'http://www.retrosheet.org/gamelogs/gldv.zip'
lcs_url = 'http://www.retrosheet.org/gamelogs/gllc.zip'


def season_game_logs(season):
    """
    Pull Retrosheet game logs for a given season
    """
    # validate input
    max_year = int(datetime.now().year) - 1
    if season > max_year or season < 1871:
        raise ValueError('Season must be between 1871 and {}'.format(max_year))
    file_name = 'GL{}.TXT'.format(season)
    z = get_zip_file(gamelog_url.format(season))
    data = pd.read_csv(z.open(file_name), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def world_series_logs():
    """
    Pull Retrosheet World Series Game Logs
    """
    file_name = 'GLWS.TXT'
    z = get_zip_file(world_series_url)
    data = pd.read_csv(z.open(file_name), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def all_star_game_logs():
    """
    Pull Retrosheet All Star Game Logs
    """
    file_name = 'GLAS.TXT'
    z = get_zip_file(all_star_url)
    data = pd.read_csv(z.open(file_name), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def wild_card_logs():
    """
    Pull Retrosheet Wild Card Game Logs
    """
    file_name = 'GLWC.TXT'
    z = get_zip_file(wild_card_url)
    data = pd.read_csv(z.open(file_name), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def division_series_logs():
    """
    Pull Retrosheet Division Series Game Logs
    """
    file_name = 'GLDV.TXT'
    z = get_zip_file(division_series_url)
    data = pd.read_csv(z.open(file_name), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data


def lcs_logs():
    """
    Pull Retrosheet LCS Game Logs
    """
    file_name = 'GLLC.TXT'
    z = get_zip_file(lcs_url)
    data = pd.read_csv(z.open(file_name), header=None, sep=',', quotechar='"')
    data.columns = gamelog_columns
    return data
