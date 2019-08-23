# Statcast Pitcher Spin
`statcast_pitcher(start_dt=[yesterday's date], end_dt=None, player_id)`

The statcast function retrieves pitch-level statcast data for a given date or range or dates and calculates spin related metrics.

## Arguments
`start_dt:` first day for which you want to retrieve data. Defaults to yesterday's date if nothing is entered. If you only want data for one date, supply a `start_dt` value but not an `end_dt` value. Format: YYYY-MM-DD. 

`end_dt:` last day for which you want to retrieve data. Defaults to None. If you want to retrieve data for more than one day, both a `start_dt` and `end_dt` value must be given. Format: YYYY-MM-DD. 

`player_id:` MLBAM player ID for the pitcher you want to retrieve data for. To find a player's MLBAM ID, see the function [playerid_lookup](http://github.com/jldbc/pybaseball/docs/playerid_lookup.md) or the examples below. 

### Added Return Columns
`Mx`: The amount of movement in the x-direction due to the Magnus effect alone. (Positive is towards first base/catcher's right)

`Mz`: The amount of movement in the z-direction due to the Magnus effect alone. (Positive is upwards)

`theta`: The angle of the spin axis with respect to it's movement between 0 and 90. A 0 angle means the spin axis is perpendicular to it's movement (it's all 'useful' spin with regards to the Magnus effect); 90 means the spin axis is parallel to it's direction (like a gyroball). Pitches 

`phi`: The angle of the spin axis in the x-z plane oriented to the x-axis. More colloquially, the axis the ball is spinning from the catcher's eye.

### Notes 
- This method piggybacks off of the `statcast_pitcher` method and is therefore prone to any issue or bug in it. 
- The method's calcuations were modeled from the work of Professor Alan Nathan of the University of Illinois.
- The axes referred to are the PITCHf/x coordinate system, where the origin is home plate, the x-axis points to the catcher's right, the y-axis, towards the mound, and the z-axis, upward. So a pitch generally moves in the -y direction.
- These calculations are sensitive to the environment (temperature, barometic pressure, humidity, altitude, windspeed, etc.). These calculations are all done as if the pitches were thrown at Tropicana Field, which has no wind and a constant temperature of 70 degrees.


## Examples of valid queries

```python
from pybaseball import statcast_pitcher_spin
from pybaseball import playerid_lookup

# find Chris Sale's player id (mlbam_key)
playerid_lookup('darvish','yu')

# get all available data within date range
data = statcast_pitcher_spin('2019-07-01', '2019-07-31', player_id = 506433)

# get data for July 15th, 2017
data = statcast_pitcher_spin('2019-05-03', player_id = 543294)
```
