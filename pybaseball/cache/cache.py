import abc
import functools
import glob
import os
from typing import Any, Callable, Dict, Optional

import pandas as pd

from . import cache_record, func_utils
from .cache_config import CacheConfig, autoload_cache

# Cache is disabled by default
config = autoload_cache()


def enable() -> None:
    config.enable(True)


def disable() -> None:
    config.enable(False)


def purge() -> None:
    ''' Remove all records from the cache '''
    record_files = glob.glob(os.path.join(config.cache_directory, '*.cache_record.json'))
    records = [cache_record.CacheRecord(filename) for filename in record_files]
    for record in records:
        record.delete()


def flush() -> None:
    ''' Remove all expired files from the cache '''
    record_files = glob.glob(os.path.join(config.cache_directory, '*.cache_record.json'))
    records = [cache_record.CacheRecord(filename) for filename in record_files]
    for record in records:
        if record.expired:
            record.delete()

 # pylint: disable=invalid-name
 # pylint: disable=too-few-public-methods
class df_cache:
    def __init__(self, expires: int = CacheConfig.DEFAULT_EXPIRATION):
        self.cache_config = config
        self.expires = expires

    def __call__(self, func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def _cached(*args: Any, **kwargs: Any) -> pd.DataFrame:
            func_data = self._safe_get_func_data(func, args, kwargs)
            result = self._safe_load_func_cache(func_data)

            if result is None:
                result = func(*args, **kwargs)
                self._safe_save_func_cache(func_data, result)

            return result

        return _cached

    def _safe_get_func_data(self, func: Callable[..., pd.DataFrame], args: Any, kwargs: Any) -> Dict:
        try:
            func_name = func_utils.get_func_name(func)

            # Skip all this if cache is disabled
            if not self.cache_config.enabled:
                return {}

            arglist = list(args)  # tuple won't come through the JSONify well
            if arglist and isinstance(arglist[0], abc.ABC):  # remove the table classes when they're self
                arglist = arglist[1:]
            return {'func': func_name, 'args': arglist, 'kwargs': kwargs}
        except:  # pylint: disable=bare-except
            return {}

    def _safe_load_func_cache(self, func_data: Dict) -> Optional[pd.DataFrame]:
        try:
            glob_path = os.path.join(self.cache_config.cache_directory, f'{func_data["func"]}*.cache_record.json')

            record_files = glob.glob(glob_path)

            records = [cache_record.CacheRecord(filename) for filename in record_files]

            for record in records:
                if not record.expired and record.supports(func_data):
                    return record.load_df()

            return None
        except:  # pylint: disable=bare-except
            return None

    def _safe_save_func_cache(self, func_data: Dict, result: pd.DataFrame) -> None:
        try:
            if self.cache_config.enabled and func_data:
                new_record = cache_record.CacheRecord(data=func_data, expires=self.expires)
                new_record.save()
                new_record.save_df(result)
        except:  # pylint: disable=bare-except
            pass

