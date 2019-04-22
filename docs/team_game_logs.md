# Team Game Logs
`team_game_logs(season, team, log_type="batting")`

Retrieves batting or pitching game logs for a single team-season from Baseball Reference.

## Arguments
`season`: year of logs

`team`: 3-letter Baseball Reference team abbreviation

`log_type`: "batting" (default) or "pitching"

## Examples

```Python
# Braves batting logs for 2019
batting_logs = team_game_logs(2019, "ATL")

# Orioles pitching logs from 2018
pitching_logs = team_game_logs(2018, "BAL", "pitching")
```