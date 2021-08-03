# Statcast Pitcher
`statcast_pitcher(start_dt=[yesterday's date], end_dt=None, player_id)`

The statcast function retrieves pitch-level statcast data for a given date or range or dates. 

## Arguments
`start_dt:` first day for which you want to retrieve data. Defaults to yesterday's date if nothing is entered. If you only want data for one date, supply a `start_dt` value but not an `end_dt` value. Format: YYYY-MM-DD. 

`end_dt:` last day for which you want to retrieve data. Defaults to None. If you want to retrieve data for more than one day, both a `start_dt` and `end_dt` value must be given. Format: YYYY-MM-DD. 

`player_id:` MLBAM player ID for the pitcher you want to retrieve data for. To find a player's MLBAM ID, see the function [playerid_lookup](http://github.com/jldbc/pybaseball/docs/playerid_lookup.md) or the examples below. 

### A note on data availability 
The earliest available statcast data comes from the 2008 season when the system was first introduced to Major League Baseball. Queries before this year will not work. Further, some features were introduced after the 2008 season. Launch speed angle, for example, is only available from the 2015 season forward. 

### Known issue
In rare cases where a player has seen greater than 30,000 pitches over the time period specified in your query, only the first 30,000 of these plays will be returned. There is a fix in the works for this

## Examples of valid queries

```python
from pybaseball import statcast_pitcher
from pybaseball import playerid_lookup

# find Chris Sale's player id (mlbam_key)
playerid_lookup('sale','chris')

# get all available data
data = statcast_pitcher('2008-04-01', '2017-07-15', player_id = 519242)

# get data for July 15th, 2017
data = statcast_pitcher('2017-07-15', player_id = 519242)
```
# Statcast Pitcher Exit Velo Barrels
`statcast_pitcher_exitvelo_barrels(year, minBBE=[qualified])`

This function retrieves batted ball against data for all qualified pitchers in a given year. 

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.

`minBBE:` The minimum number of batted ball against events for each pitcher. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only qualified pitchers will be returned.

## Examples of Valid Queries
```python
from pybaseball import statcast_pitcher_exitvelo_barrels

# get data for all qualified pitchers in 2019
data = statcast_pitcher_exitvelo_barrels(2019)

# get data for pitchers with a minimum of 100 batted ball events in 2019
data = statcast_pitcher_exitvelo_barrels(2019, 100)
```
# Statcast Pitcher Expected Stats
`statcast_pitcher_expected_stats(year, minPA=[qualified])`

This function retrieves expected stats based on quality of batted ball contact against in a given year.

## Arguments
`year:` The year for which you wish to retrieve expected stats data. Format: YYYY.

`minPA:` The minimum number of plate appearances against for each player. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only qualified pitchers will be returned.

## Examples of Valid Queries
```python
from pybaseball import statcast_pitcher_expected_stats

# get data for all qualified pitchers in 2019
data = statcast_pitcher_expected_stats(2019)

# get data for pitchers with a minimum of 150 plate appearances against in 2019
data = statcast_pitcher_expected_stats(2019, 150)
```
# Statcast Pitcher Pitch Arsenal
`statcast_pitcher_pitch_arsenal(2019, minP=[qualified], arsenal_type="average_speed")`

This function retrieves high level stats on each pitcher's arsenal in a given year.

## Arguments
`year:` The year for which you wish to retrieve expected stats data. Format: YYYY.

`minP:` The minimum number of pitches thrown. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only qualified pitchers will be returned.

`arsenal_type:` The type of stat to retrieve for the pitchers' arsenals. Options include `["average_speed", "n_", "average_spin"]`, where `"n_"` corresponds to the percentage share for each pitch. If no value is specified, it will default to average speed.

## Examples of Valid Queries
```python
from pybaseball import statcast_pitcher_pitch_arsenal

# get average pitch speed data for all qualified pitchers in 2019
data = statcast_pitcher_pitch_arsenal(2019)

# get average pitch spin data for pitchers with at least 200 pitches in 2019
data = statcast_pitcher_pitch_arsenal(2019, minP=200, arsenal_type="average_spin")

# get percentage shares data for qualified pitchers in 2019
data = statcast_pitcher_pitch_arsenal(2019, arsenal_type="n_")
```
# Statcast Pitcher Pitch Arsenal Stats
`statcast_pitcher_arsenal_stats(2019, minPA=25)`

This function retrieves assorted basic and advanced outcome stats for pitchers' arsenals in a given year. Run value and whiff % are defined on a per pitch basis, while all others are on a per PA basis.

## Arguments
`year:` The year for which you wish to retrieve expected stats data. Format: YYYY.

`minPA:` The minimum number of plate appearances against. If a player falls below this threshold, they will be excluded from the results. If no value is specified, it will default to 25 plate appearances against.

## Examples of Valid Queries
```python
from pybaseball import statcast_pitcher_arsenal_stats

# get data for all pitchers with 25 or more plate appearances against in 2019
data = statcast_pitcher_arsenal_stats(2019)

# get data for all pitchers with 100 or more plate appearances against in 2019
data = statcast_pitcher_arsenal_stats(2019, minPA=100)
```
# Statcast Pitcher Pitch Movement
`statcast_pitcher_pitch_movement(2019, minP=[qualified], pitch_type="FF")`

This function retrieves pitch movement stats for all qualified pitchers with a specified pitch type for a given year. 

## Arguments
`year:` The year for which you wish to retrieve expected stats data. Format: YYYY.

`minP:` The minimum number of pitches thrown. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only qualified pitchers will be returned.

`pitch_type:` The type of pitch to retrieve movement data on. Options include `["FF", "SIFT", "CH", "CUKC", "FC", "SL", "FS", "ALL"]`. Pitch names also allowed. If no value is specified, it will default to "FF".

## Examples of Valid Queries
```python
from python import statcast_pitcher_pitch_movement

# get data on qualified fastballs in 2019
data = statcast_pitcher_pitch_movement(2019)

# get data on pitchers who threw 30 or more changeups in 2019
data = statcast_pitcher_pitch_movement(2019, minP=30, pitch_type="CH")
```
# Statcast Pitcher Active Spin
`statcast_pitcher_active_spin(2019, minP=250)`

This function retrieves active spin stats on all of a pitchers' pitches in a given year.

## Arguments
`year:` The year for which you wish to retrieve expected stats data. Format: YYYY.

`minP:` The minimum number of pitches thrown. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only pitchers who threw 250 or more pitches will be returned.

## Examples of Valid Queries
```python
from python import statcast_pitcher_active_spin

# get data on qualified pitchers in 2019
data = statcast_pitcher_active_spin(2019)

# get data on pitchers who threw 100 or more pitches in 2019
data = statcast_pitcher_active_spin(2019, minP=100)
```
# Statcast Pitcher Percentile Ranks
`statcast_pitcher_percentile_ranks(year)`

This function retrieves percentile ranks for each player in a given year, including batters with 2.1 PA per team game and 1.25 for pitchers. It includes percentiles on expected stats, batted ball data, and spin rates, among others.

## Arguments
`year:` The year for which you wish to retrieve percentile data. Format: YYYY.

## Examples of Valid Queries
```python
from pybaseball import statcast_pitcher_percentile_ranks

# get data for all qualified pitchers in 2019
data = statcast_pitcher_percentile_ranks(2019)
```
# Statcast Pitcher Spin Direction Comparison
`statcast_pitcher_spin_dir_comp(2020)`

This function retrieves spin comparisons between two pitches for qualifying pitchers in a given year.

## Arguments
`year:` The year for which you wish to retrieve percentile data. Format: YYYY.

`pitch_a:` The first pitch in the comparison. Valid pitches include "4-Seamer", "Sinker", "Changeup", "Curveball", "Cutter", "Slider", and "Sinker". Defaults to "4-Seamer". Pitch codes also accepted.

`pitch_b:` The second pitch in the comparison and must be different from `pitch_a`. Valid pitches include "4-Seamer", "Sinker", "Changeup", "Curveball", "Cutter", "Slider", "Sinker". Defaults to "Changeup". Pitch codes also accepted.

`minP:` The minimum number of pitches of type `pitch_a` thrown. If a player falls below this threshold, they will be excluded from the results. If no value is specified, only pitchers who threw 100 or more pitches will be returned.

`pitcher_pov:` Boolean. If `True`, then direction of movement is from the pitcher's point of view. If `False`, then it is from the batter's point of view.

## Examples of Valid Queries
```python
from pybaseball import statcast_pitcher_spin_dir_comp

# get data for fastball / changeup combos in 2020
data = statcast_pitcher_spin_dir_comp(2020)

# get data for sinker / slider combos in 2020, with at least 50 sinkers thrown
data = statcast_pitcher_spin_dir_comp(2020, pitch_a="Sinker", pitch_b="Slider", minP=50)

# get data for sinker / slider combos in 2020 using pitch codes and from the batter's POV
data = statcast_pitcher_spin_dir_comp(2020, pitch_a="SIFT", pitch_b="SL", pitcher_pov=False)
```
