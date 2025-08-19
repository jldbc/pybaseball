# Box Score

`box_score(game_pk)`

Get box score stats from MLB Stats API for a given game.

## Arguments

`game_pk:` Integer. The unique MLB game id for the desired game.

## Data Availability

This data is available for any MLB game with a registered game id.

## Examples of valid queries

```python
from pybaseball import box_score

# get box score for game: 565997
data = box_score(565997)
```
