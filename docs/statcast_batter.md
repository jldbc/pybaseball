# Statcast Batter
`statcast_batter(start_dt=[yesterday's date], end_dt=None, player_id)`

The statcast function retrieves pitch-level statcast data for a given date or range or dates. 

## Arguments
`start_dt:` first day for which you want to retrieve data. Defaults to yesterday's date if nothing is entered. If you only want data for one date, supply a `start_dt` value but not an `end_dt` value. Format: YYYY-MM-DD. 

`end_dt:` last day for which you want to retrieve data. Defaults to None. If you want to retrieve data for more than one day, both a `start_dt` and `end_dt` value must be given. Format: YYYY-MM-DD. 

`player_id:` MLBAM player ID for the player you want to retrieve data for. To find a player's MLBAM ID, see the function [playerid_lookup](http://github.com/jldbc/pybaseball/docs/playerid_lookup.md) or the examples below. 

### A note on data availability 
The earliest available statcast data comes from the 2008 season when the system was first introduced to Major League Baseball. Queries before this year will not work. Further, some features were introduced after the 2008 season. Launch speed angle, for example, is only available from the 2015 season forward. 

## Examples of valid queries

```python
from pybaseball import statcast_batter
from pybaseball import playerid_lookup

# find David Ortiz's player id (mlbam_key)
playerid_lookup('ortiz','david')

# get all available data
data = statcast_batter('2008-04-01', '2017-07-15', player_id = 120074)

# get data for August 16th, 2014
data = statcast_batter('2014-08-16', player_id = 120074)

```
# Statcast Batter Exit Velo Barrels
`statcast_batter_exitvelo_barrels(year, minBBE=[qualified])`

This function retrieves batted ball data for all batters in a given year. 

## Arguments
`year:` The year for which you wish to retrieve batted ball data. Format: YYYY.

`minBBE:` The minimum number of batted ball events for each player. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only qualified batters will be returned.

## Examples of Valid Queries
```python
from pybaseball import statcast_batter_exitvelo_barrels

# get data for all qualified batters in 2019
data = statcast_batter_exitvelo_barrels(2019)

# get data for batters with a minimum of 100 batted ball events in 2019
data = statcast_batter_exitvelo_barrels(2019, 100)
```
# Statcast Batter Expected Stats
`statcast_batter_expected_stats(year, minPA=[qualified])`

This function retrieves expected stats based on quality of batted ball contact in a given year.

## Arguments
`year:` The year for which you wish to retrieve expected stats data. Format: YYYY.

`minPA:` The minimum number of plate appearances for each player. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only qualified batters will be returned.

## Examples of Valid Queries
```python
from pybaseball import statcast_batter_expected_stats

# get data for all qualified batters in 2019
data = statcast_batter_expected_stats(2019)

# get data for batters with a minimum of 150 plate appearances in 2019
data = statcast_batter_expected_stats(2019, 150)
```
# Statcast Batter Percentile Ranks
`statcast_batter_percentile_ranks(year)`

This function retrieves percentile ranks for each player in a given year, including batters with 2.1 PA per team game and 1.25 for pitchers.

## Arguments
`year:` The year for which you wish to retrieve percentile data. Format: YYYY.

## Examples of Valid Queries
```python
from pybaseball import statcast_batter_percentile_ranks

# get data for all qualified batters in 2019
data = statcast_batter_percentile_ranks(2019)
```
# Statcast Batter Pitch Arsenal
`statcast_batter_pitch_arsenal(year, minPA=25)`

This function retrieves outcome data for batters split by the pitch type in a given year.

## Arguments:
`year:` The year for which you wish to retrieve pitch arsenal data. Format: YYYY.

`minPA:` The minimum number of plate appearances for each player. If a player falls below this threshold, they will be excluded from the results. If no value is specified, the default number of plate appearances is 25.

## Examples of Valid Queries
```python
from pybaseball import statcast_batter_pitch_arsenal

# get data for all qualified batters in 2019
data = statcast_batter_pitch_arsenal(2019)

# get data for batters with a minimum of 100 plate appearances in 2019
data = statcast_batter_pitch_arsenal(2019, 100)
```