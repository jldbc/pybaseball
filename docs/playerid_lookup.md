# Player ID Lookup

## Single Player Lookup

`playerid_lookup(last, first=None, fuzzy=False)`

Look up a player's MLBAM, Retrosheet, FanGraphs, and Baseball Reference ID by name.

## Arguments
`last:` String. The player's last name. Case insensitive.

`first:` String. Optional. The player's first name. Case insensitive.

`fuzzy:` Boolean. Optional. Search for inexact name matches, the 5 closest will be returned.

Providing last name only will return all available id data for players with that last name (this will return several rows for a common last name like Jones, for example.) If multiple players exist for a (last name, first name) pair, you can figure out who's who by seeing their first and last years of play in the fields `mlb_played_first` and `mlb_played_last`.

This data comes from Chadwick Bureau, meaning that there are several people in this data who are not MLB players. For this reason, supplying both last and first name is recommended to narrow your search. 

## Examples of valid queries

```python
from pybaseball import playerid_lookup

# find the ids of all players with last name Jones (returns 1,314 rows)
data = playerid_lookup('jones')

# only return the ids of chipper jones (returns one row)
data = playerid_lookup('jones','chipper')

# Will return all players named Pedro Martinez (returns *2* rows)
data = playerid_lookup("martinez", "pedro", fuzzy=True)

# Will return the 5 closest names to "yadi molina" (returns 5 rows)
# First row will be Yadier Molina
data = playerid_lookup("molina", "yadi", fuzzy=True)
```

## List Lookup

`player_search_list(player_list)`

Look up a list of player ID's by name, return a data frame of all players

`player_list:` List. A list of tuples, of the form `(last, first)`. Case Insensitive.

Sources are the same as those used in the above `playerid_lookup` function. Queries for this function must be exact name matches.

## Examples of valid queries

```python

from pybaseball import player_search_list

# Will return the ids for both Lou Brock and Chipper Jones (returns 2 rows)
data = player_search_list([("brock","lou"), ("jones","chipper")])

```