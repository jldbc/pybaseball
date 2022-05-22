
import sys
import pybaseball
import pandas as pd

if __name__ == "__main__":
    season = 2020
    pybaseball.cache.enable()
    batting = pybaseball.batting_stats(season)
    pitching = pybaseball.pitching_stats(season)
    columns_same = list(batting.columns) == list(pitching.columns)
    shape_same = batting.shape == pitching.shape
    cache_failed = columns_same and shape_same
    sys.exit(int(cache_failed))
