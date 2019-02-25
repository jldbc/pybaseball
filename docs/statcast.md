# Statcast
`statcast(start_dt=[yesterday's date], end_dt=None, team=None)`

The `statcast` function retrieves pitch-level statcast data for a given date or range or dates. 

## Arguments
`start_dt:` first day for which you want to retrieve data. Defaults to yesterday's date if nothing is entered. If you only want data for one date, supply a `start_dt` value but not an `end_dt` value. Format: YYYY-MM-DD. 

`end_dt:` last day for which you want to retrieve data. Defaults to None. If you want to retrieve data for more than one day, both a `start_dt` and `end_dt` value must be given. Format: YYYY-MM-DD. 

`team:` optional. If you only want statcast data for one team, supply that team's abbreviation here (i.e. BOS, SEA, NYY, etc).

`verbose:` Boolean, default=True. If set to True this will provide updates on query progress, if set to False it will not. 

### A note on data availability 
The earliest available statcast data comes from the 2008 season when the system was first introduced to Major League Baseball. Queries before this year will not work. Further, some features were introduced after the 2008 season. Launch speed angle, for example, is only available from the 2015 season forward. 

### A note on query time
Baseball savant limits queries to 30000 rows each. For this reason, if your request is for a period of greater than 5 days, it will be broken into two or more smaller requests. The data will still be returned to you in a single dataframe, but it will take slightly longer. 

## Examples of valid queries

```python
from pybaseball import statcast

# get all statcast data for July 4th, 2017
data = statcast('2017-07-04')

#get data for the first seven days of August in 2016
data = statcast('2016-08-01', '2016-08-07')

#get all data for the Texas Rangers in the 2016 season
data = statcast('2016-04-01', '2016-10-30', team='TEX')

# get data for yesterday
data = statcast()
```
