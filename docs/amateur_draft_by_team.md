# Amateur Draft by Team

`amateur_draft_by_team(team, year, keep_stats=True)`

Get amateur draft results by team and year.

## Arguments

`team`: Team code which you want to check. Following is the list of team codes.

|Team Name|Team Code|
|:--:|:--:|
|Angels|ANA|
|Astros|HOU|
|Athletics|OAK|
|Blue Jays|TOR|
|Braves|ATL|
|Brewers|MIL|
|Cardinals|STL|
|Cubs|CHC|
|Rays|TBD|
|Diamondbacks|ARI|
|Dodgers|LAD|
|Giants|SFG|
|Indians (Guardians)|CLE|
|Mariners|SEA|
|Marlins|FLA|
|Mets|NYM|
|Nationals|WSN|
|Orioles|BAL|
|Padres|SDP|
|Phillies|PHI|
|Pirates|PIT|
|Rangers|TEX|
|Red Sox|BOS|
|Reds|CIN|
|Rockies|COL|
|Royals|KCR|
|Tigers|DET|
|Twins|MIN|
|White Sox|CHW|
|Yankees|NYY|

`year`: Year which you want to check.

## Examples of valid queries

```python
from pybaseball import amateur_draft_by_team

# check 2011 Rays draft
rays_2011_draft = amateur_draft_by_team("TBD", 2011)

# check 2013 Royals draft without stats
royals_2013_draft_without_stats = amateur_draft_by_team("KCR", 2013, keep_stats=False)
```