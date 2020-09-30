# pybaseball

**2.0.0 Release: 28 August, 2020**

## Recent Updates
- New Maintainer: after a period of inactive maintenance, this is again being actively maintained.
- New functionality:
   - Plot spray charts on stadium (schorrm/pybaseball#9, thanks to @andersonfrailey)
   - Baseball Reference game logs (schorrm/pybaseball#4, thanks to @reddigari)
   - More functions for Chadwick Bureau data (schorrm/pybaseball#8, thanks to @valdezt)
   - Exposes Chadwick Bureau lookup table (schorrm/pybaseball#7)
   - Top Prospects (schorrm/pybaseball#5, thanks to @TylerLiu42)
   - Full Season Statcast data (schorrm/pybaseball#2, @TylerLiu42)
   - Amateur Draft results (schorrm/pybaseball#11, @TylerLiu42)
- Bugfixes, with thanks to @bgunn34 and @TAThor

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

## Statcast: Pull advanced metrics from Major League Baseball's Statcast system

Statcast data include pitch-level features such as Perceived Velocity (PV), Spin Rate (SR), Exit Velocity (EV), pitch X, Y, and Z coordinates, and more. The function `statcast(start_dt, end_dt)` pulls this data from baseballsavant.com. 

```python
>>> from pybaseball import statcast
>>> data = statcast(start_dt='2017-06-24', end_dt='2017-06-27')
>>> data.head(2)

   index pitch_type  game_date  release_speed  release_pos_x  release_pos_z  
0    314         CU 2017-06-27           79.7        -1.3441         5.4075
1    332         FF 2017-06-27           98.1        -1.3547         5.4196

  player_name    batter   pitcher     events     ...      release_pos_y  
0   Matt Bush  608070.0  456713.0  field_out     ...            54.8585
1   Matt Bush  429665.0  456713.0  field_out     ...            54.3470

   estimated_ba_using_speedangle  estimated_woba_using_speedangle  woba_value  
0                          0.100                            0.137         0.0
1                          0.269                            0.258         0.0

   woba_denom babip_value iso_value launch_speed_angle at_bat_number pitch_number  
0         1.0         0.0       0.0                3.0          64.0          1.0
1         1.0         0.0       0.0                3.0          63.0          3.0  
[2 rows x 79 columns]
```

If `start_dt` and `end_dt` are supplied, it will return all statcast data between those two dates. If not, it will return yesterday's data. The optional argument `verbose` will control whether the library updates you on its progress while it pulls the data.

For a player-specific statcast query, pull pitching or batting data using the `statcast_pitcher` and `statcast_batter` functions. These take the same `start_dt` and `end_dt` arguments as the statcast function, as well as a `player_id` argument. This ID comes from MLB Advanced Media, and can be obtained using the function `playerid_lookup`. A complete example: 

```python
>>> # Find Clayton Kershaw's player id
>>> from pybaseball import playerid_lookup
>>> from pybaseball import statcast_pitcher
>>> playerid_lookup('kershaw', 'clayton')
Gathering player lookup table. This may take a moment.

  name_last name_first  key_mlbam key_retro  key_bbref  key_fangraphs  
0   kershaw    clayton     477132  kersc001  kershcl01           2036

   mlb_played_first  mlb_played_last
0            2008.0           2017.0

>>> # His MLBAM ID is 477132, so we feed that as the player_id argument to the following function 
>>> kershaw_stats = statcast_pitcher('2017-06-01', '2017-07-01', 477132)
>>> kershaw_stats.head(2)
  pitch_type   game_date release_speed release_pos_x release_pos_z  
0         SL  2017-06-29          87.2        1.0865        6.4034
1         SL  2017-06-29          86.9        1.0195        6.4324

       player_name  batter  pitcher     events              description  
0  Clayton Kershaw  458913   477132  strikeout  swinging_strike_blocked
1  Clayton Kershaw  458913   477132       null                     ball

      ...       release_pos_y  estimated_ba_using_speedangle  
0     ...             54.5463                            0.0
1     ...             54.7625                            0.0

   estimated_woba_using_speedangle  woba_value woba_denom babip_value  
0                              0.0        0.00          1           0
1                              0.0        null       null        null

  iso_value launch_speed_angle at_bat_number pitch_number
0         0               null            57            6
1      null               null            57            5

[2 rows x 78 columns]
```

## Pitching Stats: pitching stats for players across multiple seasons, single seasons, or during a specified time period

This library contains two main functions for obtaining pitching data. For league-wide season-level pitching data, use the function `pitching_stats(start_season, end_season)`. This will return one row per player per season, and provide all metrics made available by FanGraphs.

The second is `pitching_stats_range(start_dt, end_dt)`. This allows you to obtain pitching data over a specific time interval, allowing you to get more granular than the FanGraphs function (for example, to see which pitcher had the strongest month of May). This query pulls data from Baseball Reference. Note that all dates should be in `YYYY-MM-DD` format.

If you prefer Baseball Reference to FanGraphs, there is a third option called `pitching_stats_bref(season)`. This works the same as `pitching_stats`, but retrieves its data from Baseball Reference instead. This is typically not recommended, however, because the Baseball Reference query currently can only retrieve one season's worth of data per request.

```python
>>> from pybaseball import pitching_stats
>>> data = pitching_stats(2012, 2016)
>>> data.head()
     Season             Name     Team   Age     W    L   ERA  WAR     G    GS  
336  2015.0  Clayton Kershaw  Dodgers  27.0  16.0  7.0  2.13  8.6  33.0  33.0
236  2014.0  Clayton Kershaw  Dodgers  26.0  21.0  3.0  1.77  7.6  27.0  27.0
472  2014.0     Corey Kluber  Indians  28.0  18.0  9.0  2.44  7.4  34.0  34.0
235  2015.0     Jake Arrieta     Cubs  29.0  22.0  6.0  1.77  7.3  33.0  33.0
256  2013.0  Clayton Kershaw  Dodgers  25.0  16.0  9.0  1.83  7.1  33.0  33.0

       ...      wSL/C (pi)  wXX/C (pi)  O-Swing% (pi)  Z-Swing% (pi)  
336    ...            1.76       22.85          0.364          0.665
236    ...            2.62         NaN          0.371          0.670
472    ...            3.92         NaN          0.336          0.598
235    ...            2.42         NaN          0.329          0.618
256    ...            0.74         NaN          0.339          0.635

     Swing% (pi)  O-Contact% (pi)  Z-Contact% (pi)  Contact% (pi)  Zone% (pi)  
336        0.511            0.478            0.811          0.689       0.487
236        0.525            0.536            0.831          0.730       0.515
472        0.468            0.485            0.886          0.744       0.505
235        0.468            0.595            0.856          0.762       0.483
256        0.484            0.563            0.873          0.763       0.492

     Pace (pi)
336       23.4
236       23.7
472       24.6
235       23.3
256       23.4

[5 rows x 299 columns]
```


## Batting Stats: hitting stats for players within seasons or during a specified time period

Batting stats are obtained similar to pitching stats. The function call for getting a season-level stats is `batting_stats(start_season, end_season)`, and for a particular time range it is `batting_stats_range(start_dt, end_dt)`. The Baseball Reference equivalent for season-level data is `batting_stats_bref(season)`. 

```python
>>> from pybaseball import batting_stats_range
>>> data = batting_stats_range('2017-05-01', '2017-05-08')
>>> data.head()
          Name  Age  #days     Lev          Tm  G  PA  AB  R  H  ...    HBP  
1   Jose Abreu   30     69  MLB-AL     Chicago  7  31  30  5  9  ...      0
2   Lane Adams   27     69  MLB-NL     Atlanta  6   6   6  0  2  ...      0
3   Matt Adams   28     68  MLB-NL   St. Louis  6   9   9  2  4  ...      0
4   Jim Adduci   32     69  MLB-AL     Detroit  6  24  21  3  5  ...      0
5  Tim Adleman   29     72  MLB-NL  Cincinnati  1   2   2  0  0  ...      0

   SH  SF  GDP  SB  CS     BA    OBP    SLG    OPS
1   0   0    1   0   0  0.300  0.323  0.667  0.989
2   0   0    1   1   0  0.333  0.333  0.333  0.667
3   0   0    0   0   0  0.444  0.444  0.778  1.222
4   0   0    0   0   0  0.238  0.333  0.381  0.714
5   0   0    0   0   0  0.000  0.000  0.000  0.000

[5 rows x 27 columns]
```

## Game-by-Game Results and Schedule 
The `schedule_and_record` function returns a team's game-by-game results for a given season, including game date, home and away teams, end result (W/L/Tie), score, winning/losing/saving pitchers, attendance, and division standing at that date. The function's only two arguments are `season` and `team`, where team is the team's abbreviation (i.e. NYY for New York Yankees, SEA for Seattle Mariners). If the season argument is set to the current season, the query returns results for past games and the schedule for those that have not occurred yet. 

```python
# Example: Let's take a look at the individual-game results of the 1927 Yankees
>>> from pybaseball import schedule_and_record
>>> data = schedule_and_record(1927, 'NYY')
>>> data.head()
                Date   Tm Home_Away  Opp W/L     R   RA   Inn  W-L  Rank  \
1    Tuesday, Apr 12  NYY      Home  PHA   W   8.0  3.0   9.0  1-0   1.0
2  Wednesday, Apr 13  NYY      Home  PHA   W  10.0  4.0   9.0  2-0   1.0
3   Thursday, Apr 14  NYY      Home  PHA   T   9.0  9.0  10.0  2-0   1.0
4     Friday, Apr 15  NYY      Home  PHA   W   6.0  3.0   9.0  3-0   1.0
5   Saturday, Apr 16  NYY      Home  BOS   W   5.0  2.0   9.0  4-0   1.0

       GB      Win     Loss  Save  Time D/N  Attendance  Streak
1    Tied     Hoyt    Grove  None  2:05   D     72000.0       1
2  up 0.5  Ruether     Gray  None  2:15   D      8000.0       2
3    Tied     None     None  None  2:50   D      9000.0       2
4    Tied  Pennock    Ehmke  None  2:27   D     16000.0       3
5  up 1.0  Shocker  Ruffing  None  2:05   D     25000.0       4
```


## Standings: up to date or historical division standings, W/L records

The `standings(season)` function gives division standings for a given season. If the current season is chosen, it will give the most current set of standings. Otherwise, it will give the end-of-season standings for each division for the chosen season. 

This function returns a list of dataframes. Each dataframe is the standings for one of MLB's six divisions. 

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

# Caching

To facilitate faster data retrieval for repeated calls, caching may be used to save a local copy of the requested data.
By default caching is disabled so as to respect a user's potential desire to not have their hard drive space used
without their permission. However, enabling caching is simple.

Caching can be turned on by including the caching module in the pybaseball.datahelpers submodule, and enabling the
caching option like so:

```python
from pybaseball.datahelpers import caching

caching.cache_config.enable()
```

This will store a copy of the data returned for each DataFrame returning function call.
This data will be stored in `~/.pybaseball/cached_data` (or `%USERPROFILE%\.pybaseball\cached_data` in Windows) by
default. This can be configured by modifying the config:

```python
from pybaseball.datahelpers import caching

caching.cache_config.cache_directory = '~/other_location'
```

The cache_config has many options that can be set or it can be replaced with a new CacheConfig object:

```python
from datetime import timedelta

from pybaseball.datahelpers import caching

caching.cache_config = caching.CacheConfig(
   enabled=True,
   cache_directory='~/other_other_location',
   expiration=timedelta(days=7),
   cache_type=caching.CacheType.CSV
)
```

Each CacheConfig option is as follows:
- `enabled` - bool - Whether caching should be enabled
- `cache_directory` - str - The location to store the cached data. If it does not exist, it will be created.
- `expiration` - datetime.timedelta - The timedelta after the cache file is created to expire it. Default = 24 hours.
- `cache_type` - pybaseball.datahelpers.caching.CacheType - The method to use in storing the cache. Options:
  - `CacheType.CSV` - Cache is stored in pandas compatible CSV format files
  - `CacheType.CSV_GZ` - Cache is stored in pandas compatible GZip files with a compressed CSV file inside
  - `CacheType.EXCEL` - Cache is stored in Microsoft Excel XLSX format files
  - `CacheType.FEATHER` - Cache is stored in Apache Arrow Feather format files: https://arrow.apache.org/docs/python/feather.html
  - `CacheType.JSON` - Cache is stored in JSON format files
  - `CacheType.PARQUET` - Cache is stored in Apache Parquet format files: https://parquet.apache.org/
  - `CacheType.PICKLE` - Cache is stored as python pickle files


# Complete Documentation

So far this has provided a basic overview of what this package can do and how you can use it. For full documentation on available functions and their arguments, see the [docs](https://github.com/jldbc/pybaseball/tree/master/docs) folder. 

# So what can I do with this? 

Need some inspiration? See some examples of classic baseball studies replicated using this package [here](https://github.com/jldbc/pybaseball/tree/master/EXAMPLES).

------

## Credit

This package was developed by James LeDoux and is maintained by [Moshe Schorr](https://github.com/schorrm).

This package was inspired by Bill Petti's excellent R package [baseballr](https://github.com/billpetti/baseballr), which at the time of this package's development had no Python equivalent. Our hope is to fill that void with this package.

The Lahman data comes from [Sean Lahman's baseball database](http://www.seanlahman.com/baseball-archive/statistics/).

All other data comes from FanGraphs, Baseball Reference, the Chadwick Bureau, Retrosheet, and Baseball Savant.

## Work in Progress:

Moving forward, we intend to:

* Implement custom metrics such as Statcast edge percentages, historical Elo ratings, wOBA, etc.
* Retrieve data from other useful sources
* Identify edge cases where these queries fail (please open up an issue if you find one!)
* Add more examples

Interested in contributing? There are some ideas in [contributing.md](https://github.com/jldbc/pybaseball/tree/master/contributing.md).
