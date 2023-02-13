import logging
import os
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set
from datetime import date

import numpy as np
import pandas as pd

from . import lahman
from .datasources import fangraphs
from .utils import most_recent_season

_DATA_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'fangraphs_teams.csv')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logger = logging.getLogger('pybaseball')
logger.setLevel(LOG_LEVEL)


def team_ids(season: Optional[int] = None, league: str = 'ALL') -> pd.DataFrame:
    if not os.path.exists(_DATA_FILENAME):
        _generate_teams()

    fg_team_data = pd.read_csv(_DATA_FILENAME, index_col=0)

    if season is not None:
        fg_team_data = fg_team_data.query(f"yearID == {season}")

    if league is not None and league.upper() != "ALL":
        fg_team_data = fg_team_data.query(f"lgID == '{league.upper()}'")

    return fg_team_data


def mlb_team_id(team_name):
    #
    # For the given team_name passed in, look it up in the csv and return the MLB Team ID (for example, if Cubs
    # were passed in, 112 should be returned. If not found, throw an error.
    #
    mlb_url_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'mlb_url_team_ID.csv')
    mlb_team_id_data = pd.read_csv(mlb_url_file_name, index_col=0)

    # Sanitize the input - remove spaces, dashes and make lower case
    team_name = team_name.replace(" ", "").replace("-", "").lower()

    # Filter the csv data by the sanitized team name
    filtered_data = mlb_team_id_data.query(f"team_name == '{team_name}'")

    # If we found something, return it.
    if filtered_data.size == 0:
        raise ValueError(f"Team name {team_name} was not found!")
    else:
        return mlb_team_id_data['mlb_team_id'].loc[filtered_data.index[0]]

# franchID: teamIDfg
_manual_matches: Dict[str, int] = {
    'BLT': 1007,
    'BLU': 1008,
    'BRG': 1012,
    'BTT': 1014,
    'CEN': 1019,
    'CHP': 1022,
    'CPI': 1030,
    'ECK': 1032,
    'MAR': 1046,
    'NYY': 9,
    'SLM': 1072,
}


def _front_loaded_ratio(str_1: str, str_2: str) -> float:
    '''
        A difflib ration based on difflint's SequenceMatcher ration.

        It gives higher weight to a name that starts the same.

        For example:

        In the default ratio, 'LSA' and 'BSN' both match to 'BSA' with a score of 67.
        However, for team names, the first letter or two are almost always the city, which is likely to be the same.
        So, in this scorer 'LSA' would match to 'BSA' with a score of 83, while 'BSN' would match at 58.
    '''

    if len(str_1) != 3 or len(str_2) != 3:
        logger.warn(
            "This ratio is intended for 3 length string comparison (such as a lahman teamID, franchID, or teamIDBR."
            "Returning 0 for non-compliant string(s)."
        )
        return 0.0

    full_score = SequenceMatcher(a=str_1, b=str_2).ratio()
    front_score = SequenceMatcher(a=str_1[:-1], b=str_2[:-1]).ratio()

    return (full_score + front_score) / 2


def _get_close_team_matches(lahman_row: pd.Series, fg_data: pd.DataFrame, min_score: int = 50) -> Optional[str]:
    columns_to_check = ['franchID', 'teamID', 'teamIDBR', 'initials', 'city_start']
    best_of = 3

    choices: Set[str] = set(fg_data[fg_data['Season'] == lahman_row.yearID]['Team'].values)

    if len(choices) == 0:
        return None

    scores: Dict[str, List[float]] = {choice: [] for choice in choices}
    for join_column in columns_to_check:
        for choice in choices:
            scores[choice].append(
                _front_loaded_ratio(lahman_row[join_column], choice) * 100 if len(lahman_row[join_column]) == 3 else 0.0
            )
    scores = {key: sorted(value, reverse=True)[:best_of] for key, value in scores.items()}
    scores_list = [(key, round(np.mean(value))) for key, value in scores.items()]
    choice, score = sorted(scores_list, key=lambda x: x[1], reverse=True)[0]
    return choice if score >= min_score else None


def _generate_teams() -> pd.DataFrame:
    """
    Creates a datafile with a map of Fangraphs team IDs to lahman data to be used by fangraphss_teams

    Should only need to be run when a team is added, removed, or moves to a new city.
    """

    start_season = 1876
    end_season = most_recent_season()

    lahman_columns = ['yearID', 'lgID', 'teamID', 'franchID', 'divID', 'name', 'teamIDBR', 'teamIDlahman45',
                      'teamIDretro']

    lahman_teams = lahman.teams_core().query('yearID >= @start_season')[lahman_columns]

    # Only getting AB to make payload small, and you have to specify at least one column
    fg_team_data = fangraphs.fg_team_batting_data(start_season, end_season, "ALL", stat_columns=['AB'])

    fg_columns = list(fg_team_data.columns.values)

    unjoined_fangraphs_teams = fg_team_data.copy(deep=True)

    unjoined_lahman_teams = lahman_teams.copy(deep=True)

    unjoined_lahman_teams['manual_teamid'] = unjoined_lahman_teams.apply(
        lambda row: _manual_matches.get(row.franchID, -1),
        axis=1
    )

    lahman_columns += ['manual_teamid']

    unjoined_lahman_teams['initials'] = unjoined_lahman_teams.apply(
        lambda row: re.sub(r'[^A-Z]', '', row['name']),
        axis=1
    )

    lahman_columns += ['initials']

    unjoined_lahman_teams['city_start'] = unjoined_lahman_teams.apply(
        lambda row: row['name'][:3].upper(),
        axis=1
    )

    lahman_columns += ['city_start']

    joined: pd.DataFrame = None

    for join_column in ['manual_teamid', 'teamID', 'franchID', 'teamIDBR', 'initials', 'city_start']:
        joined_count = len(joined.index) if (joined is not None) else 0
        if join_column == 'manual_teamid':
            outer_joined = unjoined_lahman_teams.merge(unjoined_fangraphs_teams, how='outer',
                                                       left_on=['yearID', join_column],
                                                       right_on=['Season', 'teamIDfg'])
        else:
            outer_joined = unjoined_lahman_teams.merge(unjoined_fangraphs_teams, how='outer',
                                                       left_on=['yearID', join_column],
                                                       right_on=['Season', 'Team'])

        # Clean up the data
        found = outer_joined.query("not Season.isnull() and not yearID.isnull()")
        joined = pd.concat([joined, found]) if (joined is not None) else found

        # My kingdom for an xor function
        unjoined = outer_joined.query('yearID.isnull() or Season.isnull()')

        unjoined_lahman_teams = unjoined.query('Season.isnull()').drop(labels=fg_columns, axis=1)
        unjoined_fangraphs_teams = unjoined.query('yearID.isnull()').drop(labels=lahman_columns, axis=1)

        logger.info("Matched %s teams off of %s. %s teams remaining to match.", len(joined.index) - joined_count,
                    join_column, len(unjoined_lahman_teams.index))

    joined_count = len(joined.index) if (joined is not None) else 0

    # Try to close match the rest
    unjoined_lahman_teams['close_match'] = unjoined_lahman_teams.apply(
        lambda row: _get_close_team_matches(row, unjoined_fangraphs_teams),
        axis=1
    )

    outer_joined = unjoined_lahman_teams.merge(unjoined_fangraphs_teams, how='outer', left_on=['yearID', 'close_match'],
                                               right_on=['Season', 'Team'])

    # Clean up the data
    joined = pd.concat([joined, outer_joined.query("not Season.isnull() and not yearID.isnull()")])

    unjoined = outer_joined.query('(yearID.isnull() or Season.isnull()) and not (yearID.isnull() and Season.isnull())')

    unjoined_lahman_teams = unjoined.query('Season.isnull()').drop(unjoined_fangraphs_teams.columns.values, axis=1)
    unjoined_fangraphs_teams = unjoined.query('yearID.isnull()').drop(unjoined_lahman_teams.columns, axis=1)

    logger.info("Matched %s teams off of close match. %s teams remaining to match.", len(joined.index) - joined_count,
                len(unjoined_lahman_teams.index))

    error_state = False

    if not unjoined_lahman_teams.empty:
        logger.warning(
            'When trying to join lahman data to Fangraphs, found %s rows of extraneous lahman data: %s',
            len(unjoined_lahman_teams.index),
            unjoined_lahman_teams.sort_values(['yearID', 'lgID', 'teamID', 'franchID'])
        )
        error_state = True

    if not unjoined_fangraphs_teams.empty:
        this_year = date.today().year
        if not unjoined_fangraphs_teams[(unjoined_fangraphs_teams.Season.astype(int) < this_year)].empty:
            logger.warning(
                'When trying to join Fangraphs data to lahman, found %s rows of extraneous Fangraphs data: %s',
                len(unjoined_fangraphs_teams.index),
                unjoined_fangraphs_teams.sort_values(['Season', 'Team'])
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