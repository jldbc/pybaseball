# Team Batting Against Stats from Baseball-Reference

`team_batting_against(season=[most_recent_season])`

The 'team_batting_against' function returns a dataframe of each team's batting against stats for a single season.

## Arguments

`start_season:` Integer. The season year for which you want each team's batting against data. If omitted, data for the most recent season will be returned.

## Examples of valid queries

```python
~~~~
from pybaseball import team_batting_against

# get team-level batting against data for all teams in 2018
data = team_batting_against(2018)

# get team-level batting against data for all teams for the most recent season
data = team_batting_against()
~~~~
```
