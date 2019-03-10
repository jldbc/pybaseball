# Constants

Constants has three functions, corresponding to the three tables on FanGraphs' 'Guts!' page.

`woba_fip_constants()`

The `woba_fip_constants` function returns the table of wOBA and FIP constants from FanGraphs.

`park_factors(season)`

The `park_factors` function returns the park factors table from FanGraphs, this is *not* disambiguated by handedness.

`handedness_park_factors(season)`

The `handedness_park_factors` function returns the handedness park factors table from FanGraphs, this *is* disambiguated by handedness.

Note: it may lag behind (as of writing, 2018 stats are available for `park_factors` but not `handedness_park_factors`.

### Examples

The following code adds wOBA to the Lahman batting table.

```python
from pybaseball import batting, woba_fip_constants

bat = batting().fillna(0)

woba_table = woba_fip_constants()

lookup = woba_table.set_index('Season').to_dict('index')

cons = pd.DataFrame([lookup[year] for year in bat.yearID])

bat['1B'] = bat.H - bat.HR - bat['3B'] - bat['2B']
bat['wOBA'] = (cons.wBB * bat.BB + cons.wHBP * bat.HBP + cons.w1B * bat['1B']
    + cons.w2B * bat['2B'] + cons.w3B * bat['3B'] + cons.wHR * bat.HR) / (
    bat.AB + bat.BB - bat.IBB + bat.SF + bat.HBP)
```
