from unittest.mock import patch
# from os import path
# import pandas as pd
# import pytest

# import pybaseball

# _pytest_cache_directory = path.join(pybaseball.cache.cache_config.cache_directory, '.pytest')

# @pytest.mark.parametrize(
#     "cache_type", [(x) for x in ['CSV', 'PARQUET']]
# )
# def test_cache(cache_type: str) -> None:
#     cache_config = pybaseball.cache.CacheConfig(enabled=True, cache_type=cache_type, profiling=True,
#                                                 cache_directory=_pytest_cache_directory)
#     with patch('pybaseball.cache.cache_config', cache_config):
#         # Delete any existing data just in case
#         pybaseball.cache.purge()

#         # Uncached read, cached write
#         result, _, write_time, _ = pybaseball.batting_stats(2019) # type: ignore

#         assert isinstance(write_time, float)

#         # Cached read, no write
#         result2, read_time2, _, file_size2 = pybaseball.batting_stats(2019) # type: ignore

#         assert isinstance(read_time2, float)
#         assert isinstance(file_size2, int)

#         pd.testing.assert_frame_equal(result, result2)

#         print(f"\n| {cache_type} | {write_time:.3f} | {read_time2:.3f} | {(file_size2/1000):.1f} KB |")

#         # Cleanup
#         pybaseball.cache.flush()
