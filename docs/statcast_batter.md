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

~~~~
from pybaseball import statcast_batter
from pybaseball import playerid_lookup

# find David Ortiz's player id (mlbam_key)
playerid_lookup('ortiz','david')

# get all available data
data = statcast_batter('2008-04-01', '2017-07-15', player_id = 120074)

# get data for August 16th, 2014
data = statcast_batter('2014-08-16', player_id = 120074)

~~~~
