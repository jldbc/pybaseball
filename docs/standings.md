# Standings

`standings(season)`

Get division standings for a given season. Data exists from 1969 season to present, since this is when divisions were introduced. 

## Arguments
`season:` Integer. Defaults to the current calendar year if no value is provided. 

## Examples of valid queries

```python
from pybaseball import standings

# get the current season's up-to-date standings
data = standings()

# get the end-of-season division standings for the 1980 season
data = standings(1980)
```
