import cProfile
import gc
import io
import os
import pstats
import sys
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import requests

from pybaseball import batting_stats, pitching_stats, team_batting, team_fielding, team_pitching

ITERATIONS = 10

def mock_requests_get(html: str):
    class DummyResponse:
        def __init__(self, content: str):
            self.content = content.encode('utf-8')
            self.status_code = 200

    def fake_get(url: str, timeout: Optional[int] = None):
        return DummyResponse(html)

    requests.get = fake_get # type: ignore


def get_data_file_contents(filename: str) -> str:
    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, 'data')
    with open(os.path.join(data_dir, filename)) as _file:
        return _file.read()


def requests_get_setup(data_file: str, enable_gc: bool = True):
    def _setup():
        if enable_gc:
            gc.enable()
        mock_requests_get(get_data_file_contents(data_file))

    return _setup


def profile_batting_stats():
    batting_stats(2019)


def profile_pitching_stats():
    pitching_stats(2019)


def profile_team_batting():
    team_batting(2019)


def profile_team_fielding():
    team_fielding(2019)


def profile_team_pitching():
    team_pitching(2019)


profile_suite: List[Tuple[Callable, Callable, int]] = [
    (requests_get_setup('batting_leaders.html'), profile_batting_stats, ITERATIONS),
    (requests_get_setup('pitching_leaders.html'), profile_pitching_stats, ITERATIONS),
    (requests_get_setup('team_batting.html'), profile_team_batting, ITERATIONS),
    (requests_get_setup('team_fielding.html'), profile_team_fielding, ITERATIONS),
    (requests_get_setup('team_pitching.html'), profile_team_pitching, ITERATIONS)
]


def profile(suite : List[Tuple[Callable, Callable, int]]):
    for setup, func, iterations in suite:
        setup()
        [func() for x in range(iterations)]

if __name__ == "__main__":
    # Setup profiler
    profiler = cProfile.Profile()
    profiler.enable()

    # Run
    profile(profile_suite)

    # Print stats
    profiler.disable()
    stats_stream = io.StringIO()
    profiler_stats = pstats.Stats(profiler, stream=stats_stream).sort_stats(pstats.SortKey.PCALLS) # type: ignore
    # TODO: After https://github.com/python/typeshed/pull/4523 is integrated into a mypy release, remove ^ type annotation
    profiler_stats.print_stats()
    try:
        print(stats_stream.getvalue())
    except BrokenPipeError as bpe:
        # This is necessary so we can pipe this data to a head command
        pass
