from unittest.mock import patch

import pandas as pd
import pytest

import pybaseball

@pytest.mark.parametrize(
    "cache_type", [(x) for x in pybaseball.datahelpers.caching.CacheType]
)
def test_cache(cache_type: pybaseball.datahelpers.caching.CacheType) -> None:
    with patch('pybaseball.datahelpers.caching.cache_config',
               pybaseball.datahelpers.caching.CacheConfig(enabled=True, cache_type=cache_type)
    ):
        # Delete any existing data just in case
        pybaseball.datahelpers.caching.bust_cache()

        # Uncached
        result = pybaseball.batting_stats(2019)

        # Cached
        result2 = pybaseball.batting_stats(2019)

        pd.testing.assert_frame_equal(result, result2)
