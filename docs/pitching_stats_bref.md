# Pitching Stats Bref

`pitching_stats_bref(season)`

Get pitching stats from Baseball Reference for a given season. 

## Arguments
`season:` Integer. The season to get data for. If no value is provided, pulls data for the season of the current calendar year. 

## Data Availability
This table only has data from 2008 to present. The `pitching_stats` function is a better resource for historical data. 

## Examples of valid queries

```python
from pybaseball import pitching_stats_bref

# get all of this season's pitching data so far
data = pitching_stats_bref()

# retrieve data on the 2009 season
data = pitching_stats_bref(2009)
```

