# Team ID Lookup

`team_ids(season: int, league: str) -> pd.DataFrame`

Return a mapping dataframe to map Fangraphs, Retrosheet, Baeball Reference, and Lahman team data.

## Arguments
`season:` Integer. Optional. The season to get the team list of. If not specified, then return all seasons.

`league:` String. Optional. The league to get the team list of. If not specified, then 'ALL'.

## Usage example

```python
from pybaseball import team_ids, teams, team_batting

teams = team_ids(2019)
batting = team_batting(2019).add_prefix('batting.')

teams.merge(
    batting, left_on=['yearID', 'teamIDfg'], right_on=['batting.Season', 'batting.teamIDfg']
)

```

