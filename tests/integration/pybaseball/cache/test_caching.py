from unittest.mock import patch
from os import path
import pandas as pd
import pytest

import pybaseball

_pytest_cache_directory = path.join(pybaseball.cache.cache_config.cache_directory, '.pytest')

@pytest.mark.parametrize(
    "cache_type", [(x) for x in pybaseball.cache.CacheType]
)
def test_cache(cache_type: pybaseball.cache.CacheType) -> None:
    with patch('pybaseball.cache.cache_config',
               pybaseball.cache.CacheConfig(enabled=True, cache_type=cache_type, profiling=True,
                                            cache_directory=_pytest_cache_directory)
    ):
        # Delete any existing data just in case
        pybaseball.cache.flush()

        # Uncached read, cached write
        result, _, write_time, _ = pybaseball.batting_stats(2019) # type: ignore

        # Cached read, no write
        result2, read_time2, _, file_size2 = pybaseball.batting_stats(2019) # type: ignore

        pd.testing.assert_frame_equal(result, result2)

        print(f"\n| {cache_type} | {write_time:.3f} | {read_time2:.3f} | {(file_size2/1000):.1f} KB |")

        # Cleanup
        pybaseball.cache.flush()
