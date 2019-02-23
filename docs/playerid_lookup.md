# Player ID Lookup

`playerid_lookup(last, first=None)`

Look up a player's MLBAM, Retrosheet, FanGraphs, and Baseball Reference ID by name.

## Arguments
`last:` String. The player's last name. Case insensitive.

`first:` String. Optional. The player's first name. Case insensitive.

Providing last name only will return all available id data for players with that last name (this will return several rows for a common last name like Jones, for example.) If multiple players exist for a (last name, first name) pair, you can figure out who's who by seeing their first and last years of play in the fields `mlb_played_first` and `mlb_played_last`.

This data comes from Chadwick Bureau, meaning that there are several people in this data who are not MLB players. For this reason, supplying both last and first name is recommended to narrow your search. 

## Examples of valid queries

```python
from pybaseball import playerid_lookup

# find the ids of all players with last name Jones (returns 1,314 rows)
data = playerid_lookup('jones')

# only return the ids of chipper jones (returns one row)
data = playerid_lookup('jones','chipper')
```
