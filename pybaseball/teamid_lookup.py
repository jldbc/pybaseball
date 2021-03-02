import logging
import os
from typing import Dict, Optional, Set, Tuple

import pandas as pd
from fuzzywuzzy import process

from . import lahman
from .datasources import fangraphs
from .utils import most_recent_season

_DATA_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'fangraphs_teams.csv')


def team_ids(season: Optional[int] = None, league: str = 'ALL') -> pd.DataFrame:
    if not os.path.exists(_DATA_FILENAME):
        _generate_teams()

    fg_team_data = pd.read_csv(_DATA_FILENAME, index_col=0)

    if season is not None:
        fg_team_data = fg_team_data.query(f"yearID == {season}")

    if league is not None and league.upper() != "ALL":
        fg_team_data = fg_team_data.query(f"lgID == '{league.upper()}'")

    return fg_team_data


# (teamID, franchID): teamIDfg
_manual_matches: Dict[Tuple[str, str], int] = {
    ('BL4', 'MAR'): 1046,
    ('BLA', 'NYY'): 9,
    ('BLF', 'BLT'): 1007,
    ('BR1', 'ECK'): 1032,
    ('BR4', 'BRG'): 1012,
    ('BRF', 'BTT'): 1014,
    ('BLU', 'BLU'): 1008,
    ('CHP', 'CHP'): 1022,
    ('CHU', 'CPI'): 1030,
    ('FW1', 'KEK'): 1042,
    ('MLA', 'BAL'): 2,
    ('ML1', 'ATL'): 16,
    ('SL5', 'SLM'): 1072,
    ('SLU', 'SLM'): 1072,
    ('WS1', 'MIN'): 8,
    ('WS2', 'TEX'): 13,
    ('WS3', 'OLY'): 1057,
    ('WS4', 'NAT'): 1050,
}


def _front_loaded_scorer(str_1: str, str_2: str, force_ascii: bool = True, full_process: bool = True) -> int:
    '''
        A fuzzywuzzy scorer based on fuzzywuzzy's default_scorer.

        It gives higher weight to a name that starts the same.

        For example:

        In the default_scorer 'LSA' and 'BSN' both match to 'BSA' with a score of 67.
        However, for team names, the first letter or two are almost always the city, which is likely to be the same.
        So, in this scorer 'LSA' would match to 'BSA' with a score of 84, while 'BSN' would match at 59.
    '''

    if len(str_1) == 1 or len(str_2) == 1:
        return int(process.default_scorer(str_1, str_2, force_ascii, full_process))

    full_score = process.default_scorer(str_1, str_2, force_ascii, full_process)
    front_score = process.default_scorer(str_1[:-1], str_2[:-1], force_ascii, full_process)

    return round((full_score + front_score) / 2)


def _fuzzy_match_team(lahman_row: pd.Series, fg_data: pd.DataFrame, min_score: int = 51) -> Optional[str]:
    columns_to_check = ['franchID', 'teamID', 'teamIDBR']

    choices: Set[str] = set(fg_data[fg_data['Season'] == lahman_row.yearID]['Team'].values)

    if len(choices) == 0:
        return None

    scores = {choice: 0 for choice in choices}
    for join_column in columns_to_check:
        for choice in choices:
            scores[choice] += _front_loaded_scorer(lahman_row[join_column], choice)
    scores_list = [(key, round(value / len(columns_to_check))) for key, value in scores.items()]
    choice, score = sorted(scores_list, key=lambda x: x[1], reverse=True)[0]
    return choice if score >= min_score else None


def _generate_teams() -> pd.DataFrame:
    """
    Creates a datafile with a map of Fangraphs team IDs to lahman data to be used by fangraphss_teams

    Should only need to be run when a team is added, removed, or moves to a new city.
    """

    start_season = 1871
    end_season = most_recent_season()

    lahman_columns = ['yearID', 'lgID', 'teamID', 'franchID', 'divID', 'name', 'teamIDBR', 'teamIDlahman45',
                      'teamIDretro']

    lahman_teams = lahman.teams()[lahman_columns]

    # Only getting AB to make payload small, and you have to specify at least one column
    fg_team_data = fangraphs.fg_team_batting_data(start_season, end_season, "ALL", stat_columns=['AB'])

    fg_columns = list(fg_team_data.columns.values)

    unjoined_team_data = fg_team_data.copy(deep=True)

    unjoined_lahman_teams = lahman_teams.copy(deep=True)

    unjoined_lahman_teams['manual_teamid'] = unjoined_lahman_teams.apply(
        lambda row: _manual_matches.get((row.teamID, row.franchID)),
        axis=1
    )

    lahman_columns += ['manual_teamid']

    joined = None

    for join_column in ['manual_teamid', 'teamID', 'franchID', 'teamIDBR']:
        if join_column == 'manual_teamid':
            outer_joined = unjoined_lahman_teams.merge(unjoined_team_data, how='outer',
                                                       left_on=['yearID', join_column],
                                                       right_on=['Season', 'teamIDfg'])
        else:
            outer_joined = unjoined_lahman_teams.merge(unjoined_team_data, how='outer',
                                                       left_on=['yearID', join_column],
                                                       right_on=['Season', 'Team'])

        # Clean up the data
        found = outer_joined.query("not Season.isnull() and not yearID.isnull()")
        joined = pd.concat([joined, found]) if (joined is not None) else found

        # My kingdom for an xor function
        unjoined = outer_joined.query(
            '(yearID.isnull() or Season.isnull()) and not (yearID.isnull() and Season.isnull())'
        )

        unjoined_lahman_teams = unjoined.query('Season.isnull()').drop(labels=fg_columns, axis=1)
        unjoined_team_data = unjoined.query('yearID.isnull()').drop(labels=lahman_columns, axis=1)

    # Try to fuzzy match the rest
    unjoined_lahman_teams['fuzzy_match'] = unjoined_lahman_teams.apply(
        lambda row: _fuzzy_match_team(row, unjoined_team_data),
        axis=1
    )

    outer_joined = unjoined_lahman_teams.merge(unjoined_team_data, how='outer', left_on=['yearID', 'fuzzy_match'],
                                               right_on=['Season', 'Team'])

    # Clean up the data
    joined = pd.concat([joined, outer_joined.query("not Season.isnull() and not yearID.isnull()")])

    # My kingdom for an xor function
    unjoined = outer_joined.query('(yearID.isnull() or Season.isnull()) and not (yearID.isnull() and Season.isnull())')

    unjoined_lahman_teams = unjoined.query('Season.isnull()').drop(unjoined_team_data.columns.values, axis=1)
    unjoined_team_data = unjoined.query('yearID.isnull()').drop(unjoined_lahman_teams.columns, axis=1)

    error_state = False

    if not unjoined_lahman_teams.empty:
        logging.warning('When trying to join lahman data to Fangraphs, found %s rows of extraneous lahman data: %s',
                        len(unjoined_lahman_teams.index),
                        unjoined_lahman_teams)
        error_state = True

    if not unjoined_team_data.empty:
        logging.warning(
            'When trying to join Fangraphs data to lahman, found %s rows of extraneous Fangraphs data: %s',
            len(unjoined_team_data.index),
            unjoined_team_data
        )
        error_state = True

    if error_state:
        raise Exception("Extraneous data was not matched. Aborting.")

    joined = joined[['yearID', 'lgID', 'teamID', 'franchID', 'teamIDfg', 'teamIDBR', 'teamIDretro']]

    joined = joined.assign(teamIDfg=joined['teamIDfg'].apply(int))
    joined = joined.assign(yearID=joined['yearID'].apply(int))

    joined = joined.sort_values(['yearID', 'lgID', 'teamID', 'franchID']).drop_duplicates()
    joined = joined.reset_index(drop=True)

    joined.to_csv(_DATA_FILENAME)

    return joined


# For backwards API compatibility
fangraphs_teams = team_ids
