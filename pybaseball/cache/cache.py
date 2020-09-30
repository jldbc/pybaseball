import os
import glob
import abc
from typing import Union, Optional, Tuple, Any, Callable

import pandas as pd

from .cache_config import CacheConfig, autoload_cache
from .cache_record import CacheRecord
from .func_utils import get_func_name
# Cache is disabled by default
cache_config = autoload_cache()

def enable() -> None:
    cache_config.enable(True)

def disable() -> None:
    cache_config.enable(False)

def purge() -> None:
    ''' Remove all records from the cache '''
    record_files = glob.glob(os.path.join(cache_config.cache_directory, '*.cache_record.json'))
    records = [CacheRecord(filename) for filename in record_files]
    for record in records:
        record.delete()

def flush() -> None:
    ''' Remove all expired files from the cache '''
    record_files = glob.glob(os.path.join(cache_config.cache_directory, '*.cache_record.json'))
    records = [CacheRecord(filename) for filename in record_files]
    for record in records:
        if record.expired:
            record.delete()


class df_cache:  # pylint: disable=invalid-name
    def __init__(self, expires: int = 7):
        self.cache_config = cache_config
        self.expires = expires

    def __call__(self, func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        def _cached(*args: Any, **kwargs: Any) -> pd.DataFrame:
            # Skip all this if cache is disabled
            if not self.cache_config.enabled:
                return func(*args, **kwargs)

            func_name = get_func_name(func)
            record_files = glob.glob(os.path.join(self.cache_config.cache_directory, '*.cache_record.json'))
            records = [CacheRecord(filename) for filename in record_files]

            arglist = list(args) # tuple won't come through the JSONIFY well
            if arglist and isinstance(arglist[0], abc.ABC): # remove the table classes when they're self
                arglist = arglist[1:]
            func_data = {'func': func_name, 'args': arglist, 'kwargs': kwargs}
            for record in records:
                if not record.expired and record.supports(func_data):
                    return record.load_df()

            result = func(*args, **kwargs)
            new_record = CacheRecord(data = func_data, expires=self.expires)
            new_record.save()
            new_record.save_df(result)
            return result

        return _cached
