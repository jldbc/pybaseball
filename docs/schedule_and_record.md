# Schedule and Record

`schedule_and_record(season, team)`

The schedule_and_record function returns a dataframe of a team's game-level results for a given season, including win/loss/tie result, score, attendance, and winning/losing/saving pitcher. If the season is incomplete, it will provide scheduling information for future games. 

## Arguments
`season:` Integer. The season for which you want a team's record data. 

`team:` String. The abbreviation of the team for which you are requesting data (e.g. "PHI", "BOS", "LAD"). 

Note that if a team did not exist during the year you are requesting data for, the query will be unsuccessful. Historical name and city changes for teams in older seasons can cause some problems as well. The Los Angeles Dodgers ("LAD"), for example, are abbreviated "BRO" in older seasons, due to their origins as the Brooklyn Dodgers. This may at times require some detective work in certain cases.   

## Examples of valid queries

```python
from pybaseball import schedule_and_record

# Game-by-game results from the Yankees' 1927 season
data = schedule_and_record(1927, "NYY")

# Results and upcoming schedule for the Phillies' current season (2017 at the time of writing)
data = schedule_and_record(2017, "PHI")
```
