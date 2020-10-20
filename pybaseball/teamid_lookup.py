import logging
import os
from datetime import date
from typing import Optional

import pandas as pd

from . import lahman
from .datasources import fangraphs

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


_known_cities = ['Altoona', 'Anaheim', 'Arizona', 'Atlanta', 'Baltimore', 'Boston', 'Brooklyn', 'Buffalo',
                 'California', 'Chicago', 'Cincinnati', 'Cleveland', 'Colorado', 'Detroit', 'Elizabeth', 'Florida',
                 'Fort Wayne', 'Hartford', 'Houston', 'Indianapolis', 'Kansas City', 'Los Angeles', 'Milwaukee',
                 'Minnesota', 'Montreal', 'New York', 'Newark', 'Oakland', 'Philadelphia', 'Pittsburg',
                 'Pittsburgh', 'Richmond', 'San Diego', 'San Francisco', 'Seattle', 'St. Louis', 'St. Paul',
                 'Syracuse', 'Tampa Bay', 'Texas', 'Toronto', 'Troy', 'Washington', 'Washington', 'Wilmington']

_manual_matches = {'CPI': 'Browns/Stogies', 'ANA': 'Angels'}


def _estimate_name(team_row: pd.DataFrame, column: str) -> str:
    if team_row['franchID'] in _manual_matches:
        return _manual_matches[team_row['franchID']]
    estimate = str(team_row[column])
    for city in _known_cities + [str(team_row['city'])]:
        estimate = estimate.replace(f'{city} ', '') if estimate.startswith(city) else estimate

    return estimate


def _generate_teams() -> pd.DataFrame:
    """
    Creates a datafile with a map of Fangraphs team IDs to lahman data to be used by fangraphss_teams

    Should only need to be run when a team is added, removed, or moves to a new city.
    """

    start_season = 1871
    end_season = date.today().year

    # Only getting AB to make payload small, and you have to specify at least one column
    team_data = fangraphs.fg_team_batting_data(start_season, end_season, "ALL", stat_columns=['AB'])

    # Join the lahman data
    teams_franchises = lahman.teams().merge(lahman.teams_franchises(), how='left', on='franchID', suffixes=['', '.fr'])
    teams_franchises = teams_franchises.merge(lahman.parks(), how='left', left_on='park', right_on='park.name',
                                              suffixes=['', '.p'])

    # Drop lahman data down to just what we need
    teams_franchises = teams_franchises[
        ['yearID', 'lgID', 'teamID', 'franchID', 'divID', 'name', 'park', 'teamIDBR', 'teamIDlahman45', 'teamIDretro',
         'franchName', 'city', 'state']
    ]

    # Try to guess the name Fangraphs would use
    teams_franchises['possibleName'] = teams_franchises.apply(lambda row: _estimate_name(row, 'name'), axis=1)
    teams_franchises['possibleFranchName'] = teams_franchises.apply(lambda row: _estimate_name(row, 'franchName'),
                                                                    axis=1)

    # Join up the data by team name, and look for what is still without a match
    outer_joined = teams_franchises.merge(team_data, how='outer', left_on=['yearID', 'possibleName'],
                                          right_on=['Season', 'Team'])
    unjoined_teams_franchises = outer_joined.query('Season.isnull()').drop(team_data.columns, axis=1)
    unjoined_team_data = outer_joined.query('yearID.isnull()').drop(teams_franchises.columns, axis=1)

    # Take all the unmatched data and try to join off franchise name, instead of team name
    inner_joined = teams_franchises.merge(team_data, how='inner', left_on=['yearID', 'possibleName'],
                                          right_on=['Season', 'Team'])
    franch_inner_joined = unjoined_teams_franchises.merge(unjoined_team_data, how='inner',
                                                          left_on=['yearID', 'possibleFranchName'],
                                                          right_on=['Season', 'Team'])

    # Clean up the data
    joined = pd.concat([inner_joined, franch_inner_joined])

    outer_joined = joined.merge(team_data, how='outer', left_on=['yearID', 'teamIDfg'],
                                right_on=['Season', 'teamIDfg'], suffixes=['', '_y'])

    unjoined_teams_franchises = outer_joined.query('Season_y.isnull()').drop(team_data.columns, axis=1,
                                                                             errors='ignore')

    if not unjoined_teams_franchises.empty:
        logging.warning('When trying to join FG data to lahman, found the following extraneous lahman data',
                        extra=unjoined_teams_franchises)

    unjoined_team_data = outer_joined.query('yearID.isnull()').drop(teams_franchises.columns, axis=1, errors='ignore')

    if not unjoined_team_data.empty:
        logging.warning('When trying to join Fangraphs data to lahman, found the following extraneous Fangraphs data',
                        extra=unjoined_team_data)

    joined = joined[['yearID', 'lgID', 'teamID', 'franchID', 'teamIDfg', 'teamIDBR', 'teamIDretro']]

    joined = joined.assign(teamIDfg=joined['teamIDfg'].apply(int))
    joined = joined.assign(yearID=joined['yearID'].apply(int))

    joined = joined.sort_values(['yearID', 'lgID', 'teamID', 'franchID']).drop_duplicates()
    joined = joined.reset_index(drop=True)

    joined.to_csv(_DATA_FILENAME)

    return joined

# For backwards API compatibility
fangraphs_teams = team_ids
