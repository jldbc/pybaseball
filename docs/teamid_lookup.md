# Team ID Lookup - Fangraphs

`fangraphs_teams(season: int, league: str) -> pd.DataFrame`

Return a mapping dataframe to map Fangraphs' team id to Lahman data.
This can then be used to map to BRef and Retrosheet data with Lahman's `teamIDBR` and `teamIDretro` columns.

## Arguments
`season:` Integer. Optional. The season to get the team list of. If not specified, then return all seasons.

`league:` String. Optional. The league to get the team list of. If not specified, then 'ALL'.

## Usage example

```python
from pybaseball import fangraphs_teams, teams, team_batting

fg_teams = fangraphs_teams(2019)
lahman_teams = teams()
batting = team_batting(2019).add_prefix('batting.')

fg_teams.merge(
    lahman_teams, on=['yearID', 'teamID', 'franchID']
).merge(
    batting, left_on=['yearID', 'teamIDfg'], right_on=['batting.Season', 'batting.teamIDfg']
)
```

