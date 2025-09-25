# Roster

`active_roster(team)`

Get current 40-man roster for a given team. Contents of the table at 
https://www.baseball-reference.com/teams/WSN/2025.shtml#all_the40man for example. Adds two columns: one
for player's bref ID, and one for the alternate URL for minor leaguers.

## Arguments
`team:` String. Must be a three-letter abbreviation that bref uses for an active MLB team.

## Examples of valid queries

```python
from pybaseball import active_roster

# get the Nationals' current 40-man roster
data = active_roster('WSN')

```
