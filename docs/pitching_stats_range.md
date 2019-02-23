# Pitching Stats Range

`pitching_stats_range(start_dt, end_dt=None)`

The pitching_stats_range function returns pitching stats from Baseball Reference, aggregated over a user-defined time range.

## Arguments
`start_dt:` String. The beginning of the date range you want data for. Format: "YYYY-MM-DD". 

`end_dt:` String. The end of the date range you want data for. If omitted, the funciton will return only data from the `start_dt`. Format: "YYYY-MM-DD".

## Examples of valid queries

```python
from pybaseball import pitching_stats_range

# retrieve all players' pitching stats for the month of May, 2017 
data = pitching_stats_range("2017-05-01", "2017-05-28")

# retrieve pitching stats for only August 24, 2016
data = pitching_stats_range("2016-08-24",)
```
