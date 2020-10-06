import cProfile
import gc
import io
import os
import pstats
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple
import argparse

import numpy as np
import requests

from pybaseball import batting_stats, pitching_stats, team_batting, team_fielding, team_pitching, datahelpers, cache

_ProfileRun = Tuple[Callable, Callable, int]

ITERATIONS = 10

def mock_requests_get(html: str):
    class DummyResponse:
        def __init__(self, content: str):
            self.content = content.encode('utf-8')
            self.status_code = 200

    def fake_get(*args: Any, **kwargs: Any) -> DummyResponse:
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

def get_profile_suite(iterations: int = ITERATIONS) -> List[_ProfileRun]:
    return [
        (requests_get_setup('batting_leaders.html'), profile_batting_stats, iterations),
        (requests_get_setup('pitching_leaders.html'), profile_pitching_stats, iterations),
        (requests_get_setup('team_batting.html'), profile_team_batting, iterations),
        (requests_get_setup('team_fielding.html'), profile_team_fielding, iterations),
        (requests_get_setup('team_pitching.html'), profile_team_pitching, iterations)
    ]


def profile(suite : List[_ProfileRun]):
    for setup, func, iterations in suite:
        setup()
        [func() for x in range(iterations)]

if __name__ == "__main__":
    # Setup profiler
    profiler = cProfile.Profile()
    profiler.enable()

    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-enabled', action='store_true', default=False)
    parser.add_argument('--cache-type', default=None)
    parser.add_argument('--iterations', default=ITERATIONS, type=int)
    args = parser.parse_args()

    if args.cache_enabled and args.cache_type is not None:
        cache.flush()
        cache.config = cache.CacheConfig(enabled=True, cache_type=args.cache_type)
    else:
        cache.disable()

    # Run
    profile(get_profile_suite(args.iterations))

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
