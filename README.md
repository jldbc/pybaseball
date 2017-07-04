# pybaseball
**(First release: 06/28/17)**

`pybaseball` is a Python package for baseball data analysis. This package scrapes baseball-reference.com and baseballsavant.com so you don't have to. So far, the package performs four main tasks: retrieving statcast data, pitching stats, batting stats, and division standings/team records.

## Statcast: Pull advanced metrics from Major League Baseball's Statcast system

Statcast data include features such as Perceived Velocity (PV), Spin Rate (SR), Exit Velocity (EV), pitch X, Y, and Z coordinates, and more. The function `statcast(start_dt, end_dt)` pulls this data from baseballsavant.com. 

~~~~
>>> pybaseball.statcast(start_dt='2017-06-15', end_dt='2017-06-28').head(2)

   pitch_type   game_date release_speed release_pos_x release_pos_z
0         SI  2017-06-27          90.1       -2.4290        6.0911
1         CH  2017-06-27          82.6       -2.2735        6.0835

    player_name  batter  pitcher     events          description  ...        
0   Denard Span  452655   430589     single  hit_into_play_score  ...
1   Denard Span  452655   430589       null                 ball  ...

   release_pos_y  estimated_ba_using_speedangle
0        54.4438                          0.584
1        54.7243                          0.000

   estimated_woba_using_speedangle  woba_value woba_denom babip_value 
0                            0.545        0.90          1           1
1                            0.000        null       null        null

  iso_value launch_speed_angle at_bat_number pitch_number
0         0                  4           110            2
1      null               null           110            1
~~~~

If `start_dt` and `end_dt` are supplied, it will return all statcast data between those two dates. If not, it will return yesterday's data. The argument `team` may also be supplied with a team's city abbreviation (i.e. BOS) to obtain only observations for games containing that team. 

For a more specific statcast query, pull pitching or batting data using the `statcast_pitcher` and `statcast_batter` functions. These take the same `start_dt` and `end_dt` arguments as the statcast function, as well as a `player_id` argument. This ID comes from MLB Advanced Media, and can be obtained using the function `playerid_lookup`. A complete example: 

~~~~
# Find Clayton Kershaw's player id
>>> pybaseball.playerid_lookup('kershaw', 'clayton')
Gathering player lookup table. This may take a moment.

       name_last name_first  key_mlbam key_retro  key_bbref  key_fangraphs  
136954   kershaw    clayton     477132  kersc001  kershcl01           2036

        mlb_played_first  mlb_played_last
136954            2008.0           2017.0

# His MLBAM ID is 477132, so we feed that as the player_id argument to the following function 
>>> pybaseball.statcast_pitcher('2017-06-01', '2017-07-01', 477132).head(2)

  pitch_type   game_date release_speed release_pos_x release_pos_z
0         SL  2017-06-29          87.2        1.0865        6.4034
1         SL  2017-06-29          86.9        1.0195        6.4324

       player_name  batter  pitcher     events              description  ...
0  Clayton Kershaw  458913   477132  strikeout  swinging_strike_blocked  ...
1  Clayton Kershaw  458913   477132       null                     ball  ...

      release_pos_y  estimated_ba_using_speedangle
0     54.5463                            0.0
1     54.7625                            0.0

   estimated_woba_using_speedangle  woba_value woba_denom babip_value
0                              0.0        0.00          1           0
1                              0.0        null       null        null

  iso_value launch_speed_angle at_bat_number pitch_number
0         0               null            57            6
1      null               null            57            5

~~~~

## Pitching Stats: pitching stats for players within seasons or during a specified time period

This library contains two functions for obtaining pitching data. The first, `pitching_stats(season)`, will return all pitcher stats for a given regular season. The present season will return stats for season-to-date. The second, `pitching_stats_range(start_dt, end_dt)`, will return pitcher stats from a given time period. Note that all dates should be in `YYYY-MM-DD` format. 

~~~~
>>> pybaseball.pitching_stats(2015).head(2)

            Name      Age  #days     Lev       Tm   G  GS    W    L  ...  
1  David Aardsma  gl   33    674  MLB-NL  Atlanta  33   0  1.0  1.0  ...
2  Fernando Abad  gl   29    633  MLB-AL  Oakland  62   0  2.0  2.0  ...

    Str   StL   StS  GB/FB    LD    PU   WHIP  BAbip   SO9  SO/W
1  0.65  0.14  0.15   0.29  0.35  0.06  1.272  0.264  10.3  2.50
2  0.63  0.15  0.11   0.39  0.29  0.07  1.343  0.270   8.5  2.37
~~~~


## Batting Stats: hitting stats for players within seasons or during a specified time period

Batting stats are obtained similar to pitching stats. The function call for getting an entire season worth of stats is `batting_stats(season)`, and for a particular time range it is `batting_stats_range(start_dt, end_dt)`. 

~~~~
>>> pybaseball.batting_stats_range('2017-05-01', '2017-05-08').head(2)

         Name      Age  #days     Lev       Tm  G  PA  AB  R  ... 
1  Jose Abreu  gl   30     51  MLB-AL  Chicago  7  31  30  5  ... 
2  Lane Adams  gl   27     51  MLB-NL  Atlanta  6   6   6  0  ... 

   HB  SH  PSF  GDP  SB  CS     BA    OBP    SLG    OPS
1   0   0   0    1   0   0   0.300  0.323  0.667  0.989
2   0   0   0    1   1   0   0.333  0.333  0.333  0.667
~~~~

## Game-by-Game Results and Schedule 
The `schedule_and_record` function returns a team's game-by-game results for a given season, including game date, home and away teams, end result (W/L/Tie), score, winning/losing/saving pitchers, attendance, and division standing at that date. The function's only two arguments are `season` and `team`, where team is the team's abbreviation (i.e. NYY for New York Yankees, SEA for Seattle Mariners). If the season argument is set to the current season, the query returns results for past games and the schedule for those that have not occurred yet. 

~~~~
# Example: Let's take a look at the individual-game results of the 1927 Yankees
>>> pybaseball.schedule_and_record(1927, 'NYY').head()

                Date             Tm Home_Away  Opp W/L   R RA Inn  W-L Rank  \
1    Tuesday, Apr 12  boxscore  NYY      Home  PHA   W   8  3   9  1-0    1
2  Wednesday, Apr 13  boxscore  NYY      Home  PHA   W  10  4   9  2-0    1
3   Thursday, Apr 14  boxscore  NYY      Home  PHA   T   9  9  10  2-0    1
4     Friday, Apr 15  boxscore  NYY      Home  PHA   W   6  3   9  3-0    1
5   Saturday, Apr 16  boxscore  NYY      Home  BOS   W   5  2   9  4-0    1

       GB      Win     Loss  Save  Time D/N Attendance Streak
1    Tied     Hoyt    Grove  None  2:05   D     72,000      +
2  up 0.5  Ruether     Gray  None  2:15   D      8,000     ++
3    Tied     None     None  None  2:50   D      9,000     ++
4    Tied  Pennock    Ehmke  None  2:27   D     16,000    +++
5  up 1.0  Shocker  Ruffing  None  2:05   D     25,000   ++++

~~~~


## Standings: up to date or historical division standings, W/L records

The `standings(season)` function gives division standings for a given season. If the current season is chosen, it will give the most current set of standings. Otherwise, it will give the end-of-season standings for each division for the chosen season. 

This function returns a list of dataframes. Each dataframe is the standings for one of MLB's six divisions. 

~~~~
>>> pybaseball.standings(2016)[4]

                    Tm    W   L  W-L%    GB
1         Chicago Cubs  103  58  .640    --
2  St. Louis Cardinals   86  76  .531  17.5
3   Pittsburgh Pirates   78  83  .484  25.0
4    Milwaukee Brewers   73  89  .451  30.5
5      Cincinnati Reds   68  94  .420  35.5
~~~~

------

This pacakge was inspired by Bill Petti's excellent R package [baseballr](https://github.com/billpetti/baseballr), which to date has no Python equivalent. My hope is to fill this void with this library. 

## Installation

To install pybaseball, run the following steps in your terminal:

~~~~
git clone https://github.com/jldbc/pybaseball
cd pybaseball
python setup.py install
~~~~

After cleaning up a few more things I will deploy to PyPi and installation will be possible via pip. 

## Work in Progress:
Moving forward, I intend to:

* Make this pip-installable
* Expand capabilities for pulling individual-player statistics (i.e. a player's full history)
* Implement custom metrics such as Statcast edge percentages, historical Elo ratings, wOBA, etc.

#### Dependencies

This library depends on: Pandas, NumPy, bs4 (beautiful soup), and Requests. 
