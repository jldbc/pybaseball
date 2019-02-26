# Player Salaries from Spotrac

Note: Salary Data on Spotrac is only available beginning in 2011.

`salaries_by_all(start_season, end_season=None, to_float=False)`

PROBLEM: requests to receive all player salaries only returns the top 100 salaries, and doesn't have pages to iterate through. Not sure how to workaround yet.

The 'salaries_by_all' function returns a dataframe of the top 100 salaries. This can be for either a single season or multiple.

## Arguments
`start_season:` Integer. The first season for which you want the salary data.

`end_season:` Integer. The last season for which you want the salary data. If not provided, the query will return data for only the `start_season`.

`to_float:` Boolean. Set to True if you want to convert player salaries to float values. Otherwise, leave as False.

## Examples of valid queries

```python
from pybaseball import player_salaries

# get top 100 seasonal player salaries from 2011 through 2013
data = salaries_by_all(2011, 2013)

# get top 100 seasonal player salaries for only the 2011 season
data = salaries_by_all(2011)
```

`salaries_by_team(team, start_season, end_season=None, to_float=False)`

The 'salaries_by_team' function returns a dataframe for all player salaries for the specified team. This can be for either a single season or multiple.

## Arguments
`team:` String. The team abbreviation (i.e. 'NYY' for Yankees) of the team for which to collect salary data.

`start_season:` Integer. The first season for which you want the salary data.

`end_season:` Integer. The last season for which you want the salary data. If not provided, the query will return data for only the `start_season`.

`to_float:` Boolean. Set to True if you want to convert player salaries to float values. Otherwise, leave as False.

## Examples of valid queries

```python
from pybaseball import player_salaries

# get the Yankees ('NYY') seasonal player salaries from 2011 through 2013
data = salaries_by_team('NYY', 2011, 2013)

# get the Yankees ('NYY') seasonal player salaries for only the 2011 season
data = salaries_by_team('NYY', 2011)
```


`salaries_by_position(position, start_season, end_season=None, to_float=False)`

The 'salaries_by_position' function returns a dataframe for all player salaries for a specified position. This can be for either a single season or multiple.

## Arguments
`position:` String. The position abbreviation (i.e. '1B' for First Base, or 'SP' for Starting Pitcher (a dict is provided at the beginning of `player_salaries.py` with all abbreviations)) of the position for which to collect salary data.

`start_season:` Integer. The first season for which you want the salary data.

`end_season:` Integer. The last season for which you want the salary data. If not provided, the query will return data for only the `start_season`.

`to_float:` Boolean. Set to True if you want to convert player salaries to float values. Otherwise, leave as False.

## Examples of valid queries

```python
from pybaseball import player_salaries

# get seasonal player salaries for First-Basemen from 2011 through 2013
data = salaries_by_position('1B', 2011, 2013)

# get seasonal player salaries for First-Basemen for only the 2011 season
data = salaries_by_position('1B', 2011)
```