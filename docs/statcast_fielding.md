# Statcast Fielding Outs Above Average
`statcast_outs_above_average(year: int, pos: str, min_att: Union[int, str] = "q")`

This function retrieves outs above average (OAA) for the given year, position, and attempts. OAA is a Statcast metric based on the "cumulative effect of all individual plays a fielder has been credited or debited with, making it a range-based metric of fielding skill that accounts for the number of plays made and the difficulty of them".

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`pos:` The position you are interested in. Valid positions include "all", "IF", "OF", and position names or abbreviations. Pitchers and catchers are not included.
`min_att:` The minimum number of fielding attempts for the player to be included in the result. The default is players, which is 1 fielding attempt per game played for 2B, SS, 3B, and OF and 1 fielding attempt per every other game played for 1B.

## Examples of Valid Queries
```python
from pybaseball import statcast_outs_above_average

# All fielders with at least 50 fielding attempts in 2019
data = statcast_outs_above_average(2019, "all", 50)

# Center fielders who qualified in 2019
data = statcast_outs_above_average(2019, "CF")

# Infielders with at least 100 fielding attempts in 2019
data = statcast_outs_above_average(2019, pos = "IF", min_att = 100)
```

# Statcast Fielding Outfield Directional OAA
`statcast_outfield_directional_oaa(year: int, min_opp: Union[int, str] = "q")`

This function retrieves outfielders' directional OAA data for the given year and number of opportunities. The directions are Back Left, Back, Back Right, In Left, In, and In Right.

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_opp:` The minimum number of opportunities for the player to be included in the result. The default is players with at least 1 fielding attempt per game.

## Examples of Valid Queries
```python
from pybaseball import statcast_outfield_directional_oaa

# All qualified outfielders from 2019
data = statcast_outfield_directional_oaa(2019)

# All outfielders with at least 200 attempts in 2019
data = statcast_outfield_directional_oaa(2019, 200)
```

# Statcast Fielding Outfield Catch Probability
`statcast_outfield_catch_proba(year: int, min_opp: Union[int, str] = "q")`

This function retrieves aggregated data for outfielder performance on fielding attempt types, binned into five star categories, for the given year and number of opportunities.

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_opp:` The minimum number of opportunities for the player to be included in the result. The default is players with at least 1 fielding attempt per game. 

## Examples of Valid Queries
```python
from pybaseball import statcast_outfield_catch_proba

# All qualified outfielders from 2019
data = statcast_outfield_catch_proba(2019)

# All outfielders with at least 200 attempts in 2019
data = statcast_outfield_catch_proba(2019, 200)
```

# Statcast Fielding Outfielder Jump
`statcast_outfielder_jump(year: int, min_att: Union[int, str] = "q")`

This function retrieves data on outfielder's jump to the ball for the given year and number of attempts. Jump is calculated only for two star or harder plays (90% or less catch probabiility).

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_att:` The minimum number of attempts for the player to be included in the result. The default is players with at least 2 two star or harder fielding attempts per team game / 5. 

## Examples of Valid Queries
```python
from pybaseball import statcast_outfielder_jump

# All qualified outfielders from 2019
data = statcast_outfielder_jump(2019)

# All outfielders with at least 100 attempts in 2019
data = statcast_outfielder_jump(2019, 100)
```

# Statcast Fielding Catcher Poptime
`statcast_catcher_poptime(year: int, min_2b_att: int, min_3b_att: int)`

This function retrieves pop time data for catchers given year and minimum stolen base attempts for second and third base. Pop time is measured as the time from the moment the ball hits the catcher's mitt to when it reaches the projected receiving point at the center of the fielder's base.

Note: It is not available for 2020 data.

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_2b_att:` The minimum number of stolen base attempts for second base against the catcher.
`min_3b_att:` The minimum number of stolen base attempts for third base against the catcher.

## Examples of Valid Queries
```python
from pybaseball import statcast_catcher_poptime

# Catchers with at least 10 second base attempts against and 2 third base attempts against in 2019
data = statcast_catcher_poptime(2019, min_2b_att = 10, min_3b_att = 2)
```

# Statcast Fielding Catcher Framing
`statcast_catcher_framing(year: int, min_called_p: Union[int, str] = "q")`

This function retrieves the catcher's framing results for the given year and minimum called pitches. It uses eight zones around the strike zone (aka "shadow zone") and gives the percentage of time the catcher gets the strike called in each zone.

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_called_p:` The minimum number of called pitches for the catcher in the shadow zone. The default is players with at least 6 called pitches in the shadow zone per team game.

## Examples of Valid Queries
```python
from pybaseball import statcast_catcher_framing

# All qualified catchers from 2019
data = statcast_catcher_framing(2019)

# Catchers with at least 500 called pitches from 2019
data = statcast_catcher_framing(2019, min_called_p = 500)
```
