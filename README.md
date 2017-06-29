# pybaseball
**(First release: 06/28/17)**

'pybaseball' is a Python package for baseball data analysis. This package scrapes baseball-reference.com and baseballsavant.com so you don't have to. So far, the package performs four main tasks. 

## Statcast: Pull advanced metrics from Major League Baseball's Statcast system

Statcast data include features such as Perceived Velocity (PV), Spin Rate (SR), Exit Velocity (EV), pitch X, Y, and Z coordinates, and more. The function 'get_statcast()' pulls this data from baseballsavant.com. 

~~~~
>>> pybaseball.get_statcast(start_dt='2017-06-15', end_dt='2017-06-28').head(2)

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

If 'start_dt' and 'end_dt' are supplied, it will return all statcast data between those two dates. If not, it will return yesterday's data. The argument 'team' may also be supplied with a team's city abbreviation (i.e. BOS) to obtain only observations for games containing that team. 

## Pitching Stats: pitching stats for players within seasons or during a specified time period

This library contains two functions for obtaining pitching data. The first, 'pitching_stats(season)', will return all pitcher stats for a given regular season. The present season will return stats for season-to-date. The second, 'pitching_stats_range(start_dt, end_dt)', will return pitcher stats from a given time period. Note that all dates should be in 'YYYY-MM-DD' format. 

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

Batting stats are obtained similar to pitching stats. The function call for getting an entire season worth of stats is 'batting_stats(season)', and for a particular time range it is 'batting_stats_range(start_dt, end_dt)'. 

~~~~
>>> pybaseball.batting_stats_range('2017-05-01', '2017-05-08').head(2)

         Name      Age  #days     Lev       Tm  G  PA  AB  R  ... 
1  Jose Abreu  gl   30     51  MLB-AL  Chicago  7  31  30  5  ... 
2  Lane Adams  gl   27     51  MLB-NL  Atlanta  6   6   6  0  ... 

   HB  SH  PSF  GDP  SB  CS     BA    OBP    SLG    OPS
1   0   0   0    1   0   0   0.300  0.323  0.667  0.989
2   0   0   0    1   1   0   0.333  0.333  0.333  0.667
~~~~

## Standings: up to date or historical division standings, W/L records

The 'standings(season)' function gives division standings for a given season. If the current season is chosen, it will give the most current set of standings. Otherwise, it will give the end-of-season standings for each division for the chosen season. 

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

## Work in Progress:
Moving forward, I intend to:

* Make this pip-installable
* Pull data from additional sources (i.e. fangraphs.com, other pages on baseball-reference.com)
* Improve error handling to clarify which queries will and will not work (i.e. date ranges for which data is available, acceptable values for function arguments)
* Implement custom metrics such as historical Elo ratings

#### Dependencies

This library depends on: Pandas, NumPy, bs4 (beautiful soup), and Requests. 
