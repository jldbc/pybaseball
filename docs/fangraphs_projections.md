# Projection Stats

`fg_projections(proj_source = "zips", position = "batters", league = "mlb", team = "") -> pd.DataFrame`

Returns player projection statistics sourced on Fangraphs. 

## Arguments
`proj_source:` String. The projection source, including pre-season, rest of season, updated in-season, 3 year, and on pace leader options. Defaults to `zips`. Options include:
- pre-season: `zips`, `zipsdc`, `steamer`, `fangraphsdc`, `atc`, `thebat`, `thebatx`
- updated rest of season: `rzips`, `steamerr`, `rfangraphsdc`, `rthebat`, `rthebatx`
- updated in-season: `uzips`, `steameru`
- 600 pa/200 IP: `steamer600`
- 3 year: `zipsp1` (current season + 1), `zipsp2` (current season + 2)
- on pace leaders: `onpaceegp` (every game played), `onpacegpp` (games played %)

Some or all sources will return no data during varying periods of the offseason. For more information on these projection sources review the disclaimer at the bottom of the [Fangraphs Projections page](https://www.fangraphs.com/projections).

`position:` String. The player position to filter the results by. Defaults to all batters. Options include:
`batters`, `pitchers`, `c`, `1b`, `2b`, `3b`, `ss`, `lf`, `cf`, `rf`, `of`, `dh`, `sp`, `rp`

`league:` String. Options include `mlb` (default), `al`, or `nl`

`team:` String. Filter to a specific team by team abbreviation (i.e. for the Philadelphia Phillies, use `PHI`). Defaults to empty (all teams)

## Query Examples

```python
from pybaseball import fg_projections

# get zips projections for all mlb batters
data = fg_projections()

# get steamer projections for American League pitchers
data = fg_projections(proj_source = "steamer", position = "pitchers", league = "al")

# get atc projections for National League outfielders
data = fg_projections(proj_source = "atc", position = "of", league = "nl")

# get on pace leaders for San Diego Padres starting pitchers
data = fg_projections(proj_source = "onpaceegp", position = "sp", team = "SDP")

```