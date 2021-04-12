# Statcast Running Sprint Speed
`statcast_sprint_speed(year: int, min_opp: int = 10)`

This function returns each player's sprint speed for the given year and minimum number of opportunities. Sprint speed is defined as "feet per second in a player’s fastest one-second window" and calculated using approximately the top two-thirds of a player's opportunities.

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_opp:` The minimum number of sprinting opportunities. Statcast considers the following two situations as opportunities:
- Runs of two bases or more on non-homers, excluding being a runner on second base when an extra base hit happens
- Home to first on “topped” or “weakly hit” balls.

## Examples of Valid Queries
```python
from pybaseball import statcast_sprint_speed

# All players with at least 50 opportunities in 2019
data = statcast_sprint_speed(2019, 50)
```

# Statcast Running 90 ft Splits
`statcast_running_splits(year: int, min_opp: int = 5, raw_splits: bool = True)`

This function returns each player's 90 feet sprint splits at five foot intervals for the given year and minimum number of opportunities.

## Arguments
`year:` The year for which you wish to retrieve batted ball against data. Format: YYYY.
`min_opp:` The minimum number of sprinting opportunities. Statcast considers the following two situations as opportunities:
- Runs of two bases or more on non-homers, excluding being a runner on second base when an extra base hit happens
- Home to first on “topped” or “weakly hit” balls.
`raw_splits:` Boolean indicator for if the function returns raw times or percentiles for each split.

## Examples of Valid Queries
```python
from pybaseball import statcast_running_splits

# Raw split times for players with at least 50 opportunities in 2019
data = statcast_running_splits(2019, 50)

# Percentiles for players with at least 100 opportunities in 2019
data = statcast_sprint_speed(2019, 100, raw_splits = False)
```