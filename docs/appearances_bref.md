# Appearances Bref

`appearances_bref(season)`

Get defensive appearances for a given season.

## Arguments
`season:` Integer. Defaults to the current calendar year if no value is provided. 

## Examples of valid queries

```python
from pybaseball import appearances_bref

# get the current season's up-to-date appearances
data = appearances_bref()

# get the end-of-season appearances for the 1960 season
data = appearances_bref(1960)

```
