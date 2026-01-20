# Get Splits Stats

`get_splits(playerid, year=None, player_info=False, pitching_splits=False)`

Look up a player's split stats from baseball-reference. Either batting or pitching splits can be returned and splits can be provided for any season or for career. 
Split stats are returned as a multi-index dataframe by split category and split. 
Additionaly, player info can also be returned as a dictionary since the information is available without requiring a separate request to the baseball-reference page. 

## Arguments

`playerid:` String. The player's bbref playerid. Example: Mike Trout is 'troutmi01'

`year:` Integer. Optional. The year to get split stats for. Leaving this out will provide career split stats.

`player_info:` Boolean. Optional. If set to True, the get_splits function will return both the split stats dataframe and a dictionary of player info that contains player position, handedness, height, weight, and team

`pitching_splits:` Boolean. Optional. If set to True, the get_splits function will return pitching splits. Otherwise, get_splits will return batting splits.

## Examples of valid queries

```python
from pybaseball import get_splits

# find the split stats for Mike Trout
df = get_splits('troutmi01')

#find the split stats and player info for Mike Trout
df, player_info_dict = get_splits('troutmi01', player_info=True)

#find the pitching split stats for Jon Lester
df = get_splits('lestejo01', pitching_splits=True)
```

# Get Team Splits Stats

`get_team_splits(team, year, pitching_splits = False)`
Look up a team's split stats from baseball-reference. Either batting or pitching splits can be returned and splits can be provided for any season.
Split stats are returned as a multi-index dataframe by split category and split. 
## Arguments

`team:` String. The team's baseball-reference code.
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

`year:` Integer. The year to get split stats for.

`pitching_splits:` Boolean. Optional. If set to True, the get_splits function will return pitching splits. Otherwise, get_splits will return batting splits.

## Examples of valid queries

```python
from pybaseball import get_splits

# find the split stats for the Braves for 2023
df = get_team_splits('ATL', 2023)
```