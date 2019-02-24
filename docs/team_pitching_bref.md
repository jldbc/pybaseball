# Team Pitching Statistics from Baseball-Reference

`team_pitching_bref(team, start_season, end_season=None)`

The 'team_pitching_bref' function returns a dataframe of team-level pitching stats for a single specified team. This can be for either a single season or multiple. The dataframe has a 'Year' column, so if multiple seasons are involved, the 'Year' column can be used to differentiate between seasons. If a player has played on the specified team for multiple years they will have an additional row for each year played.

## Arguments
`team:` String. The team abbreviation (i.e. "NYY" for the New York Yankees) of the team you want pitching data for.

`start_season:` Integer. The first season for which you want the team's pitching data.

`end_season:` Integer. The last season for which you want the team's pitching data. If not provided, the query will return data for only the `start_season`.

## Examples of valid queries

```python
~~~~
from pybaseball import team_pitching

# get the Yankees (NYY) seasonal pitching stats from 2010 through 2013
data = team_pitching_bref('NYY', 2010, 2013)

# get the Yankees (NYY) team pitching stats for only the 1999 season
data = team_pitching_bref('NYY', 1999)
~~~~
```