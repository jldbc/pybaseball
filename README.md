# pybaseball

Baseball data scraping and analysis tools in python

## Overview

`pybaseball` is a Python package for baseball data analysis. This package scrapes Baseball Reference, Baseball Savant, and FanGraphs so you don't have to. The package retrieves statcast data, pitching stats, batting stats, division standings/team records, awards data, and more. Data is available at the individual pitch level, as well as aggregated at the season level and over custom time periods. See the [docs](https://github.com/jldbc/pybaseball/tree/master/docs) for a comprehensive list of data acquisition functions.

## Installation

Pybaseball can be installed via pip:

```bash
pip install pybaseball
```

or from the repo (which may at times be more up to date):

```bash
git clone https://github.com/jldbc/pybaseball
cd pybaseball
pip install -e .
```

We will try to publish periodic updates through the 'releases' and PyPI CI, but it may lag at times.

## Community

Discussion about pybaseball use and development is hosted on our group Discord, sign up link [here](https://discord.gg/TnJVyUDDn8). Issues with the codebase should still be raised and addressed on GitHub.

##  Documentation

Full documentation on available functions and their arguments along with examples is located [docs](https://github.com/jldbc/pybaseball/tree/master/docs) folder. This section contains a brief overview of the main functionalities of this library.


### Statcast: Pull advanced metrics from Major League Baseball's Statcast system

Statcast data include pitch-level information, pulled from baseballsavant.com.

```python
>>> from pybaseball import statcast
>>> statcast(start_dt="2019-06-24", end_dt="2019-06-25").columns
Index(['pitch_type', 'game_date', 'release_speed', 'release_pos_x',
       'release_pos_z', 'player_name', 'batter', 'pitcher', 'events',
       'description', 'spin_dir', 'spin_rate_deprecated',
       'break_angle_deprecated', 'break_length_deprecated', 'zone', 'des',
       'game_type', 'stand', 'p_throws', 'home_team', 'away_team', 'type',
       'hit_location', 'bb_type', 'balls', 'strikes', 'game_year', 'pfx_x',
       'pfx_z', 'plate_x', 'plate_z', 'on_3b', 'on_2b', 'on_1b',
       'outs_when_up', 'inning', 'inning_topbot', 'hc_x', 'hc_y',
       'tfs_deprecated', 'tfs_zulu_deprecated', 'fielder_2', 'umpire', 'sv_id',
       'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az', 'sz_top', 'sz_bot',
       'hit_distance_sc', 'launch_speed', 'launch_angle', 'effective_speed',
       'release_spin_rate', 'release_extension', 'game_pk', 'pitcher.1',
       'fielder_2.1', 'fielder_3', 'fielder_4', 'fielder_5', 'fielder_6',
       'fielder_7', 'fielder_8', 'fielder_9', 'release_pos_y',
       'estimated_ba_using_speedangle', 'estimated_woba_using_speedangle',
       'woba_value', 'woba_denom', 'babip_value', 'iso_value',
       'launch_speed_angle', 'at_bat_number', 'pitch_number', 'pitch_name',
       'home_score', 'away_score', 'bat_score', 'fld_score', 'post_away_score',
       'post_home_score', 'post_bat_score', 'post_fld_score',
       'if_fielding_alignment', 'of_fielding_alignment', 'spin_axis',
       'delta_home_win_exp', 'delta_run_exp'],
      dtype='object')
```

For documentation on the definitions of these columns, see the [Statcast Search CSV Documentation](https://baseballsavant.mlb.com/csv-docs).

If `start_dt` and `end_dt` are supplied, it will return all statcast data between those two dates. If not, it will return yesterday's data. The optional argument `verbose` will control whether the library updates you on its progress while it pulls the data.

#### Player-Specific Queries

For a player-specific statcast query, pull pitching or batting data using the `statcast_pitcher` and `statcast_batter` functions. These take the same `start_dt` and `end_dt` arguments as the statcast function, as well as a `player_id` argument. This ID comes from MLB Advanced Media, and can be obtained using the function `playerid_lookup`. The returned columns match the set above, but filtered to rows for that specific pitcher or batter. A complete example: 

```python
# Find Clayton Kershaw's player id
from pybaseball import  playerid_lookup
from pybaseball import  statcast_pitcher
playerid_lookup('kershaw', 'clayton')
  name_last name_first  key_mlbam key_retro  key_bbref  key_fangraphs  mlb_played_first  mlb_played_last
0   kershaw    clayton     477132  kersc001  kershcl01           2036            2008.0           2022.0

# His MLBAM ID is 477132, so we feed that as the player_id argument to the following function 
kershaw_stats = statcast_pitcher('2017-06-01', '2017-07-01', 477132)
kershaw_stats.groupby("pitch_type").release_speed.agg("mean")
pitch_type
CH    86.725000
CU    73.133333
FF    92.844622
SI    94.515385
SL    87.962381
Name: release_speed, dtype: float64
```

#### A note on Statcast data

Statcast data is subject to change (even for prior seasons):

<div>
   <blockquote class="twitter-tweet">
      <p lang="en" dir="ltr">
         Each season has 700,000+ pitches, and is subject to update. You should code accordingly.
      </p>&mdash; Tangotiger (@tangotiger)
      <a href="https://twitter.com/tangotiger/status/1362064972025634821?ref_src=twsrc%5Etfw">February 17, 2021</a>
   </blockquote>
</div>

### Aggregate Statistics

For league-wide season-level pitching data, use the function `pitching_stats(start_season, end_season)`. This will return one row per player per season, and provide all metrics made available by FanGraphs.

For a fixed range, `pitching_stats_range(start_dt, end_dt)` pulls data for a specific time-interval from Baseball Reference. Note that all dates should be in `YYYY-MM-DD` format.

```python
from pybaseball import pitching_stats
data = pitching_stats(2014,2016)
data.columns
Index(['IDfg', 'Season', 'Name', 'Team', 'Age', 'W', 'L', 'WAR', 'ERA', 'G',
       ...
       'LA', 'Barrels', 'Barrel%', 'maxEV', 'HardHit', 'HardHit%', 'Events',
       'CStr%', 'CSW%', 'xERA'],
      dtype='object', length=334)
```

Batting stats are obtained similarly. The function call for getting a season-level stats is `batting_stats(start_season, end_season)`, and for a particular time range it is `batting_stats_range(start_dt, end_dt)`. The Baseball Reference equivalent for season-level data is `batting_stats_bref(season)`. 

(For season level queries, if you prefer Baseball Reference to FanGraphs, there is a third option, `pitching_stats_bref(season)`. This works the same as `pitching_stats`, but retrieves its data from Baseball Reference instead. This is *not recommended*, however, because the Baseball Reference query currently can only retrieve one season's worth of data per request.)

### Game-by-Game Results and Schedule 
The `schedule_and_record` function returns a team's game-by-game results for a given season. The function's only two arguments are `season` and `team`, where team is the team's abbreviation (i.e. NYY for New York Yankees).

```python
# Example: Say we want to know the 1927 Yankees record on May 16 
from pybaseball import schedule_and_record
data = schedule_and_record(1927, 'NYY')
data.loc[data.Date.str.contains("May 16"), :]
              Date   Tm Home_Away  Opp W/L    R   RA  Inn   W-L  Rank      GB      Win      Loss   Save  Time D/N  Attendance   cLI  Streak Orig. Scheduled
28  Monday, May 16  NYY         @  DET   W  6.0  2.0  9.0  19-8   1.0  up 3.0  Ruether  Holloway  Moore  2:28   D      4000.0  5.15       5            None
```


### Standings: up to date or historical division standings, W/L records

The `standings(season)` function gives division standings for a given season. If the current season is chosen, it will give the most current set of standings. Otherwise, it will give the end-of-season standings for each division for the chosen season. This function returns a list of dataframes. Each dataframe is the standings for one of MLB's six divisions. 

```python
>>> from pybaseball import standings
>>> data = standings(2016)[4]
>>> print(data)
                    Tm    W   L  W-L%    GB
1         Chicago Cubs  103  58  .640    --
2  St. Louis Cardinals   86  76  .531  17.5
3   Pittsburgh Pirates   78  83  .484  25.0
4    Milwaukee Brewers   73  89  .451  30.5
5      Cincinnati Reds   68  94  .420  35.5
```

### Caching

To facilitate faster data retrieval for repeated calls, a local data cache may be used to save a local copy of the
requested data. By default the cache is disabled so as to respect a user's potential desire to not have their hard drive
space used without their permission. However, enabling the cache is simple.

Cache can be turned on by including the pybaseball.cache module and enabling the cache option like so:

```python
from pybaseball import cache

cache.enable()
```

## FAQ

### Stale Cache

If you call a statcast method for a future date, the cache will log empty datasets for those dates. If you're not getting the results you expect for a given date, first try clearing your cache:

```
from pybaseball import cache
cache.purge()
```

### Multiprocessing

If you're getting a error with `concurrent.futures.process.BrokenProcessPool`, wrap your call in a main function, e.g.

```
if __name__ == '__main__':
    stats = statcast()
```

This may be necessary on systems that use spawn-based processes (often Windows and OSX). 

For other problems, please submit an issue.

## Contributing

See [contributing.md](https://github.com/jldbc/pybaseball/tree/master/contributing.md) for a guide to contributing to this library.


------

## Credit

This package was developed by James LeDoux and is maintained by [Moshe Schorr](https://github.com/schorrm).

This package was inspired by Bill Petti's excellent R package [baseballr](https://github.com/billpetti/baseballr), which at the time of this package's development had no Python equivalent. Our hope is to fill that void with this package.

The Lahman data comes from [Sean Lahman's baseball database](http://www.seanlahman.com/baseball-archive/statistics/).

All other data comes from FanGraphs, Baseball Reference, the Chadwick Bureau, Retrosheet, and Baseball Savant.
