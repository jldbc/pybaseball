# Statcast
__statcast_pitcher(start_dt=[yesterday's date], end_dt=None, player_id)__

The statcast function retrieves pitch-level statcast data for a given date or range or dates. 

## Arguments
__start_dt:__ first day for which you want to retrieve data. Defaults to yesterday's date if nothing is entered. If you only want data for one date, supply a start_dt value but not an end_dt value. Format: YYYY-MM-DD. 

__end_dt:__ last day for which you want to retrieve data. Defaults to None. If you want to retrieve data for more than one day, both a start_dt and end_dt value must be given. Format: YYYY-MM-DD. 

__player_id:__ MLBAM player ID for the pitcher you want to retrieve data for. To find a player's MLBAM ID, see the function [playerid_lookup](http://github.com/jldbc/pybaseball/docs/playerid_lookup.md) or the examples below. 

### A note on data availability 
The earliest available statcast data comes from the 2008 season when the system was first introduced to Major League Baseball. Queries before this year will not work. Further, some features were introduced after the 2008 season. Launch speed angle, for example, is only available from the 2015 season forward. 

### Known issue
In rare cases where a player has seen greater than 30,000 pitches over the time period specified in your query, only the first 30,000 of these plays will be returned. There is a fix in the works for this

## Examples of valid queries

~~~~
from pybaseball import statcast_pitcher
from pybaseball import playerid_lookup

# find Chris Sale's player id (mlbam_key)
playerid_lookup('sale','chris')

# get all available data
data = statcast_pitcher('2008-04-01', '2017-07-15', player_id = 519242)

# get data for July 15th, 2017
data = statcast_pitcher('2017-07-15', player_id = 519242)
~~~~