# Batting Stats

`batting_stats(start_season, end_season=None, league='all', qual=1, ind=1)`

The `batting_stats` function returns season-level batting data from FanGraphs.

## Arguments
`start_season:` Integer. The first season you want to retrieve data from. 

`end_season:` Integer. The final season you want to retrieve data from. If omitted, the funciton will return only data from the start_season.

`league:` String. Either "all" for all data, "nl" for National League, "al" for the American League, or "mnl" for all Negro League data. Defaults to "all", for returning data on all teams. See `FangraphsLeague` definition for all leagues.

`qual:` Integer. Minimum number of plate appearances to be included in the results. Defaults to `None`, which is equivalent to the current Fangraphs "Qualified" PA threshold from their leaderboard. 

`ind:` 1 or 0. Equals 1 if you want data returned at the individual season level. Equals 0 if you want aggregate data over the seasons included in the query. With `ind=1` and a query spanning the 2010 through 2015 seasons, for example, you will get each player's stats for 2010, 2011, 2012, 2013, 2014, and 2015 in a separate observation. With `ind=0`, this same query returns one row per player with their statistics aggregated over this period (either summed or averaged depending on what's appropriate).

Note that larger date ranges will take longer to process.

### A note on data availability 
While this query should work for any historical season, some of the more modern stats (contact %, zone %, and many others) will not be available before certain dates. 

## Examples of valid queries

```python
from pybaseball import batting_stats

# get all of this season's batting data so far
data = batting_stats(2017)

# retrieve data on only players who have 50+ plate appearances this year
data = batting_stats(2017, qual=50)

# retrieve one row per player per season since 2000 (i.e.: who had the single most dominant season over this period?)
data = batting_stats(2010, 2016)

# retrieve aggregate player statistics from 2000 to 2016 (i.e.: who had the most home runs overall over this period?)
data = batting_stats(2010, 2016, ind=0)


```
