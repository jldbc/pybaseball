# Daily Schedule

`daily_schedule(day=date.today())`

The `daily_schedule` function returns data about the scheduled games for the passed date from Baseball Reference.

Only queries against the main current season schedule page at this time. This page remains up until the next season's spring training has started.

## Arguments
`day:` `datetime` object. The date you want to retrieve data for. If omitted, defaults to the current date.

### A note on data availability 
After the new season starts, schedule data including start times will no longer be available by date. Use `schedule_and_record` by team to get data on past seasons.

## Examples of valid queries

```python
import datetime
from pybaseball import daily_schedule

# get today's schedule data, returns an empty frame if there are no games (spring, regular season, or postseason)
data = daily_schedule()

# get a different day's data
specific_date = datetime.datetime(2025, 7, 4) # will only work from about February 2025 - February 2026
data = daily_schedule(specific_date)


```

# Full Daily Schedule

`full_schedule()`

The `full_schedule` function returns data about all games for the current or immediately previous season.

Only queries against the main current season schedule page at this time. This page remains up until the next season's spring training has started.

### A note on data availability 
After the new season starts, schedule data including start times will no longer be available by date. Use `schedule_and_record` by team to get data on past seasons.

## Example of valid query

```python
from pybaseball import full_schedule

# get entire schedule for current season, including some spring training games and postseason if that schedule has been released
data = full_schedule()

```
