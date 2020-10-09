# Amateur Draft

`amateur_draft(year, draft_round, keep_stats=True)`

This function retrieves the MLB amateur draft results by year and round. 

## Arguments

`year:` The year for which you wish to retrieve draft results.

`draft_round`: The round for which you wish to retrieve draft results. There is no distinction made between the competitive balance, supplementary, and main portions of a round.

`keep_stats`: A boolean parameter that controls whether the major league stats of each draftee is displayed. Default set to true. 

### Examples of valid queries

```python
from pybaseball import amateur_draft

# Get draft results for the 1st round of the 2017 draft
draftResults = amateur_draft(2017, 1)

# Get draft results for the 2nd round of the 2016 draft, do not show stats
draftResults = amateur_draft(2016, 2, False)

```
