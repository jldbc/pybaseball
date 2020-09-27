import logging
import os
import time
import traceback
from datetime import datetime
from typing import Union, Optional, Tuple, Any, Callable

import pandas as pd

from . import dataframe_utils
from .cache_config import CacheConfig, CacheType
from .file_utils import _mkdir, _remove, _rmtree
from .func_utils import MAX_ARGS_KEY_LENGTH, get_func_hash, get_func_name, get_value_hash

# Cache is disabled by default
cache_config = CacheConfig()

def enable() -> None:
    cache_config.enable(True)

def disable() -> None:
    cache_config.enable(False)

_ProfiledCachedDataFrame = Union[pd.DataFrame, Tuple[pd.DataFrame, Optional[float], Optional[float], Optional[float]]]

class dataframe_cache:  # pylint: disable=invalid-name
    @property
    def extension(self) -> str:
        return str(self.cache_config.cache_type.lower())

    @property
    def cache_config(self) -> CacheConfig:
        if self.cache_config_override:
            return self.cache_config_override

        return cache_config
    
    cache_config_override: Optional[CacheConfig] = None

    def __init__(self, cache_config_override: Optional[CacheConfig] = None, reset_cache: bool = False, reset_index: bool = True):
        self.cache_config_override = cache_config_override
        self.reset_cache = reset_cache
        self.reset_index = reset_index
        _mkdir(self.cache_config.cache_directory)

    def __call__(self, func: Callable[..., pd.DataFrame]) -> Callable[..., _ProfiledCachedDataFrame]:
        def _cached(*args: Any, **kwargs: Any) -> _ProfiledCachedDataFrame:
            # Skip all this if cache is disabled
            if not self.cache_config.enabled:
                return func(*args, **kwargs)

            read_time = None
            write_time = None
            filename = None

            try:
                f_hash = get_func_hash(func, args, kwargs)
                filename = os.path.join(self.cache_config.cache_directory, f"{f_hash}.{self.extension}")

                if os.path.exists(filename):
                    modified = datetime.fromtimestamp(os.path.getmtime(filename))
                    if (modified + self.cache_config.expiration) > datetime.now():
                        # Hasn't expired yet
                        if self.cache_config.profiling:
                            start = time.perf_counter()
                            data = self.load(filename)
                            read_time = time.perf_counter() - start
                        else:
                            data = self.load(filename)
                        if self.reset_index:
                            data = data.reset_index(drop=True)
                        if read_time:
                            return data, read_time, write_time, os.path.getsize(filename)
                        else:
                            return data
            except:  # pylint: disable=broad-except
                # If this fails, log it, and then go ahead and make the function call
                # No need to crash the real work in this phase
                for ex in traceback.format_exc().split('\n'):
                    logging.debug(ex)
            result = func(*args, **kwargs)

            if filename and result is not None and isinstance(result, pd.DataFrame) and not result.empty:
                if self.reset_index:
                    result = result.reset_index(drop=True)
                if self.cache_config.profiling:
                    start = time.perf_counter()
                    self.save(result, str(filename))
                    write_time = time.perf_counter() - start
                else:
                    self.save(result, filename)

            if write_time and filename:
                return result, read_time, write_time, os.path.getsize(filename)
            else:
                return result

        if self.reset_cache:
            self.flush(func)

        return _cached

    def flush(self, func: Callable) -> None:
        cache_files = [
            x for x in os.listdir(self.cache_config.cache_directory) if x.startswith(f"{func.__name__}(")
        ]
        for cache_file in cache_files:
            _remove(os.path.join(self.cache_config.cache_directory, cache_file))
        self.reset_cache = False

    def load(self, filename: str) -> pd.DataFrame:
        return dataframe_utils.load(filename, self.cache_config.cache_type)

    def save(self, data: pd.DataFrame, filename: str) -> None:
        dataframe_utils.save(data, filename, self.cache_config.cache_type)

def flush() -> None:
    try:
        _rmtree(cache_config.cache_directory)
    except:
        pass
    _mkdir(cache_config.cache_directory)
