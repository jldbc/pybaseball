# Team Pitching

`team_pitching(start_season, end_season=None, league='all', ind=1)`

The team_pitching function returns a dataframe of team-level pitching stats. This can be for either a single season or multiple. If multiple seasons are involved, this function can provide either single-season stats (e.g. one row per team per season) or aggregate stats over multiple seasons. 

## Arguments
`start_season:` Integer. The first season for which you want the league's team-level pitching data.

`end_season:` Integer. The last season for which you want the league's team-level pitching data. If not provided, the query will return data for only the start_season.  

`league:` String. Either "all", "nl", or "al" for determining whether you want data from one league or both. Defaults to "all", for returning data on all teams. 

`ind:` Integer. Flag for whether you want data to be returned at the individual-season or aggregate level. If `ind=1`, returns one row per team per year. If `ind=0`, the query aggregates the data so that one row of aggregate stats is provided per team. For example, `team_pitching(2010, 2012, ind=1)` would return 90 rows, one for each team's 2010, 2011, and 2012 stats, while `team_pitching2010, 2012, ind=0)` would return 30 rows, one for each team's aggregate 2010-2012 pitching performance.

## Examples of valid queries

~~~~
from pybaseball import team_pitching

# get each team's individual-season-level pitching stats from 2010 through 2013
data = team_pitching(2010, 2013)

# get each team's aggregate pitching stats from the 2010 - 2013 seasons combined
data = team_pitching(2010, 2013, ind=0)

# get team pitching stats for only the 1999 season
data = team_pitching(1999)
~~~~

`team_pitching_bref(team, start_season, end_season=None)`

The team_pitching_bref function returns a dataframe of team-level pitching stats for a single specified team. This can be for either a single season or multiple. The dataframe has a 'Year' column, so if multiple seasons are involved, the 'Year' column can be used to differentiate between seasons. If a player has played on the specified team for multiple years they will have an additional row for each year played.

## Arguments
`team:` String. The team abbreviation (i.e. "NYY" for the New York Yankees) of the team you want pitching data for.

`start_season:` Integer. The first season for which you want the team's pitching data.

`end_season:` Integer. The last season for which you want the team's pitching data. If not provided, the query will return data for only the `start_season`.

## Examples of valid queries

~~~~
from pybaseball import team_pitching

# get the Yankees (NYY) seasonal pitching stats from 2010 through 2013
data = team_pitching_bref('NYY', 2010, 2013)

# get the Yankees (NYY) team pitching stats for only the 1999 season
data = team_pitching_bref('NYY', 1999)
~~~~
