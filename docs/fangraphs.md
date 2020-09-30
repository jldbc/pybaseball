# Fangraphs Data Acquisition Functions

## Parameters

| Parameter        | Type             | Description
|  ---             | ---              | ---
| start_season     | int              | The first season to pull data for. If no end_season is passed, this is the only season returned.
| end_season       | int              | The last season to pull data for.
| league           | str              | League to return data for: ALL, AL, FL, NL. Default = ALL
| ind              | int              | DEPRECATED. ONLY FOR BACKWARDS COMPATIBILITY. USE `split_seasons` INSTEAD. <br> 1 if you want individual season-level data. <br> 0 if you want a player's aggregate data over all seasons in the query
| stat_columns     | str or List[str] | The columns of data to return. <br> Default = ALL
| qual             | Optional[int]    | Minimum number of plate appearances to be included. <br> If None is specified, the Fangraphs default ('y') is used. <br> Default = None
| split_seasons    | bool             | True if you want individual season-level data <br> False if you want aggregate data over all seasons. <br> Default = False
| month            | str              | Month to filter data by. 'ALL' to not filter by month. <br> Default = 'ALL'
| on_active_roster | bool             | Only include active roster players. <br> Default = False
| minimum_age      | int              | Minimum player age. <br> Default = 0
| maximum_age      | int              | Maximum player age. <br> Default = 100
| team             | str              | Team to filter data by. <br> Specify "0,ts" to get aggregate team data.
| position         | str              | Position to filter data by. <br> Default = ALL
| max_results      | int              | The maximum number of results to return. <br> Default = 1000000 (In effect, all results)


## Usage

```python
import pybaseball

# Individual Batting Stats
pybaseball.batting_stats(2019)

# Individual Pitching Stats
pybaseball.pitching_stats(2019)

# Team Batting Stats
pybaseball.team_batting(2019)

# Team Fielding Stats
pybaseball.team_fielding(2019)

# Team Pitching Stats
pybaseball.team_pitching(2019)
```
