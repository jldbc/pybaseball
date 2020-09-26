import pathlib
from datetime import timedelta
from os import path

from .cache_type import CacheType
from .file_utils import _mkdir

class CacheConfig:
    DEFAULT_CACHE_DIR = path.join(pathlib.Path.home(), '.pybaseball', 'cache')
    DEFAULT_EXPIRATION = timedelta(hours=24)
    DEFAULT_CACHE_TYPE = CacheType.PARQUET

    # pylint: disable=too-many-arguments
    def __init__(self, enabled: bool = False, cache_directory: str = None, expiration: timedelta = None,
                 cache_type: CacheType = None, profiling: bool = False):
        self.enabled = enabled
        self.cache_directory = cache_directory if cache_directory else CacheConfig.DEFAULT_CACHE_DIR
        self.expiration = expiration if expiration else CacheConfig.DEFAULT_EXPIRATION
        self.cache_type = cache_type if cache_type is not None else CacheConfig.DEFAULT_CACHE_TYPE
        self.profiling = profiling

        _mkdir(self.cache_directory)

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled
