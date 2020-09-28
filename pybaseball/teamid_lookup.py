
import logging
from datetime import date
from typing import Optional

import pandas as pd

from . import lahman
from .datasources import fangraphs

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

def fangraphs_teams(season: Optional[int] = None, league: str = 'ALL') -> pd.DataFrame:
    """
    Get the team ids from Fangraphs, with their lahman match for joining Fangraphs data with other sources.

    Args:
        season (Optional[int]): The season to get data for. If None, get teams from all seasons.
                                Default = None
        league (str)          : League to return data for: ALL, AL, FL, NL
                                Default = ALL

    Returns:
        A pandas.DataFrame with columns for teamIDfg (int), yearID (int), teamID (str), franchID (str)
        Where yearID is the season, teamID is the lahman team id and franchID is the lahman team franchise id
    """

    if season:
        start_season = season
        end_season = season
    else:
        start_season = 1871
        end_season = date.today().year

    # Only getting AB to make payload small, and you have to specify at least one column
    team_data = fangraphs.fg_team_batting_data(start_season, end_season, league, stat_columns=['AB'])

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

    joined = joined[['yearID', 'teamIDfg', 'teamID', 'franchID']]
    joined = joined.rename(columns={'teamIDfg': 'teamIDfg_float'})
    joined['teamIDfg'] = joined['teamIDfg_float'].apply(lambda value: int(value))
    joined = joined.drop(['teamIDfg_float'], axis=1).drop_duplicates()
    joined = joined.sort_values(['yearID', 'teamIDfg'])

    return joined.reset_index(drop=True)
