# Statcast Single Game

`statcast_single_game(game_pk)`

Retrieve all statcast data for a given game id.  

## Arguments
`game_pk:` Integer. Game id provided by MLB Advanced Media.

## Examples of valid queries

```python
from pybaseball import statcast_single_game

# get statcast data for game_pk 
data = statcast_single_game(529429)
```
