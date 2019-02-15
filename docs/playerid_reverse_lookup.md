# Player ID Reverse Lookup

`playerid_reverse_lookup(player_ids, key_type='mlbam')`

Find the names and ids of one or several players given a list of MLBAM, FanGraphs, Baseball Reference, or Retrosheet ids. 

## Arguments
`player_ids:` List. A list of player ids.

`key_type:` String. The type of id you're passing in the `player_ids` field. Valid inputs are 'mlbam', 'retro', 'bbref', and 'fangraphs'. Defaults to 'mlbam' if no value is passed. 
 
This function is useful for connecting data sets from various sources or for finding player names when only an id is provided. Data for this function comes from the Chadwick Bureau. 

## Examples of valid queries

```python
from pybaseball import playerid_reverse_lookup

# a list of mlbam ids
player_ids = [116539, 116541, 641728, 116540]

# find the names of the players in player_ids, along with their ids from other data sources
data = playerid_reverse_lookup(player_ids, key_type='mlbam')

# a list of fangraphs ids
fg_ids = [826, 5417, 210, 1101]

# find their names and ids from other data sources
data = playerid_reverse_lookup(fg_ids, key_type='fangraphs')
```
