from unittest.mock import patch
from os import path
import pandas as pd
import pytest

import pybaseball

@pytest.mark.parametrize(
    "cache_type", [(x) for x in pybaseball.datahelpers.caching.CacheType]
)
def test_cache(cache_type: pybaseball.datahelpers.caching.CacheType) -> None:
    with patch('pybaseball.datahelpers.caching.cache_config',
               pybaseball.datahelpers.caching.CacheConfig(enabled=True, cache_type=cache_type, profiling=True,
                                                          cache_directory=path.join(pybaseball.datahelpers.caching.cache_config.cache_directory, '.pytest'))
    ):
        # Delete any existing data just in case
        pybaseball.datahelpers.caching.bust_cache()

        # Uncached read, cached write
        result, _, write_time, _ = pybaseball.batting_stats(2019) # type: ignore

        # Cached read, no write
        result2, read_time2, _, file_size2 = pybaseball.batting_stats(2019) # type: ignore

        pd.testing.assert_frame_equal(result, result2)

        print(f"\n| {cache_type} | {write_time:.3f} | {read_time2:.3f} | {(file_size2/1000):.1f} KB |")

        # Cleanup
        pybaseball.datahelpers.caching.bust_cache()
