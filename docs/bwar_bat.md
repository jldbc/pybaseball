# Bwar Batting

`bwar_bat(return_all=False)`

Get Baseball Reference's WAR stats from its `war_daily_bat` table, along with some other data that's not included in the `batting_stats_bref` function. 

## Arguments
`return_all` Bool. Returns all fields from `war_daily_bat` table if True, returns only a subset of columns if False. Defaults to False because most fields aren't needed for standard use cases. 

## Examples of valid queries

```python
from pybaseball import bwar_bat

# get war stats from baseball reference 
data = bwar_bat()

# get war stats plus additional fields from this table 
data = bwar_bat(return_all=True)
```
