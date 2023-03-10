# Team Batting

`team_batting(start_season, end_season=None, league='all', ind=1)`

The team_batting function returns a dataframe of team-level batting stats. This can be for either a single season or multiple. If multiple seasons are involved, this function can provide either single-season stats (e.g. one row per team per season) or aggregate stats over all seasons (e.g. each team's total HR, RBI, etc. over all seasons queried). 

## Arguments
`start_season:` Integer. The first season for which you want the league's team-level batting data.

`end_season:` Integer. The last season for which you want the league's team-level batting data. If not provided, the query will return data for only the `start_season`.  

`league:` String. Either "all" for all data, "nl" for National League, "al" for the American League, or "mnl" for all Negro League data. Defaults to "all", for returning data on all teams. See `FangraphsLeague` definition for all leagues.

`ind:` Integer. Flag for whether you want data to be returned at the individual-season or aggregate level. If `ind=1`, returns one row per team per year. If `ind=0`, the query aggregates the data so that one row of aggregate stats is provided per team. For example, `team_batting(2010, 2012, ind=1)` would return 90 rows, one for each team's 2010, 2011, and 2012 stats, while `team_batting(2010, 2012, ind=0)` would return 30 rows, one for each team's aggregate 2010-2012 batting performance.

## Examples of valid queries

```python
from pybaseball import team_batting

# get each team's seasonal batting stats from 2010 through 2013
data = team_batting(2010, 2013)

# get each team's aggregate batting stats from 2010 through 2013
data = team_batting(2010, 2013, ind=0)

# get team batting stats for only the 1999 season
data = team_batting(1999)
```
