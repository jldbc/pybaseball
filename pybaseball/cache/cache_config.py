import pathlib
from datetime import timedelta
from os import path
from typing import Optional, cast
from typing_extensions import Literal

from .file_utils import _mkdir

CacheType = Literal['CSV', 'PARQUET']

class CacheConfig:
    DEFAULT_CACHE_DIR = path.join(pathlib.Path.home(), '.pybaseball', 'cache')
    DEFAULT_EXPIRATION = timedelta(hours=24)
    DEFAULT_CACHE_TYPE: CacheType = 'PARQUET'

    # pylint: disable=too-many-arguments
    def __init__(self, enabled: bool = False, cache_directory: str = None, expiration: timedelta = None,
                 cache_type: Optional[CacheType] = None, profiling: bool = False):
        self.enabled = enabled
        self.cache_directory = cache_directory if cache_directory else CacheConfig.DEFAULT_CACHE_DIR
        self.expiration = expiration if expiration else CacheConfig.DEFAULT_EXPIRATION
        if cache_type is not None:
            self.cache_type = cast(CacheType, cache_type.upper())
        else:
            self.cache_type = self.DEFAULT_CACHE_TYPE
        self.profiling = profiling

        _mkdir(self.cache_directory)

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled
