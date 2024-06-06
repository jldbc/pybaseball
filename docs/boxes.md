# boxes

`boxes(team: str, date: str)`

Get Baseball Reference's box score data for a particular game.

## Arguments
`team` String. The team name abbrevation format.
`date` String. The date of the game which we want to find the box score.
`doubleheader` Integer. 0 for the first game of the day, and 1 for the second game. Default is 0.

## Examples of valid queries

```python
from pybaseball import boxes

team = 'DET'
date = '2010-07-19'

boxes(team, date)

```

