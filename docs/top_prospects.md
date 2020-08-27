# Top Prospects

`top_prospects(team=None, playerType=None)`

This function retrieves the top prospects by team or leaguewide. It can return top prospect pitchers, batters, or both. 

## Arguments

`team:` The team name for which you wish to retrieve top prospects. There must be no whitespace. If not specified, the function will return leaguewide top prospects.

`playerType`: Either "pitchers" or "batters". If not specified, the function will return top prospects for both pitchers and batters. 

### Examples of valid queries

```python
from pybaseball import top_prospects

# Get top pitching prospects for the Toronto Blue Jays
topProspects = top_prospects("bluejays", "pitchers")

# Get top overall prospects leaguewide
topProspects = top_prospects()

# Get top batting prospects leaguewide
# Note if the second argument is specified, the first argument must be included, even if it has no value
topProspects = top_prospects(None, "batters")

# Get top overall prospects for the San Diego Padres
topProspects("padres")

```
