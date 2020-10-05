from os import path
from typing import Callable
from unittest.mock import patch

import pandas as pd
import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

import pybaseball


@pytest.mark.parametrize(
    "cache_type", [(x) for x in ['CSV', 'PARQUET']]
)
@patch('pybaseball.cache.config.enabled', True)
def test_cache(monkeypatch: MonkeyPatch, cache_type: str, thrower: Callable) -> None:
    with patch('pybaseball.cache.config.cache_type', cache_type):
        # Delete any existing data just in case
        pybaseball.cache.purge()

        # Uncached read
        result = pybaseball.batting_stats(2019)  # type: ignore

        # Make requests.get throw an error so we can be sure this is coming from the cache
        monkeypatch.setattr(requests, 'get', thrower)

        # Cached read
        result2 = pybaseball.batting_stats(2019)  # type: ignore

        pd.testing.assert_frame_equal(result, result2)

        # Cleanup
        pybaseball.cache.purge()
