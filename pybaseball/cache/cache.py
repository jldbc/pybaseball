import abc
import glob
import logging
import os
from typing import Any, Callable, Optional, Tuple, Union

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
    logging.debug(f'Purging all cache files from {config.cache_directory}')
    record_files = glob.glob(os.path.join(config.cache_directory, '*.cache_record.json'))
    records = [cache_record.CacheRecord(filename) for filename in record_files]
    for record in records:
        record.delete()


def flush() -> None:
    ''' Remove all expired files from the cache '''
    logging.debug(f'Flushing all cache files from {config.cache_directory}')
    record_files = glob.glob(os.path.join(config.cache_directory, '*.cache_record.json'))
    records = [cache_record.CacheRecord(filename) for filename in record_files]
    for record in records:
        if record.expired:
            record.delete()


class df_cache:  # pylint: disable=invalid-name
    def __init__(self, expires: int = CacheConfig.DEFAULT_EXPIRATION):
        logging.debug(f'Creating new df_cache. config={config.__dict__}, expires={expires}')
        self.cache_config = config
        self.expires = expires

    def __call__(self, func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        def _cached(*args: Any, **kwargs: Any) -> pd.DataFrame:
            try:
                func_name = func_utils.get_func_name(func)

                # Skip all this if cache is disabled
                if not self.cache_config.enabled:
                    logging.debug(f'Caching disabled. Calling {func_name}')
                    return func(*args, **kwargs)

                logging.debug(f"Checking cache for: {func_name}")

                glob_path = os.path.join(self.cache_config.cache_directory, f'{func_name}*.cache_record.json')
                logging.debug(glob_path)

                record_files = glob.glob(glob_path)
                logging.debug(f"Relevant record files found: {record_files}")

                records = [cache_record.CacheRecord(filename) for filename in record_files]

                arglist = list(args)  # tuple won't come through the JSONify well
                if arglist and isinstance(arglist[0], abc.ABC):  # remove the table classes when they're self
                    arglist = arglist[1:]
                func_data = {'func': func_name, 'args': arglist, 'kwargs': kwargs}

                logging.debug(f"Trying to find a prior call for {func_data}")
                for record in records:
                    if not record.expired and record.supports(func_data):
                        logging.debug(f"Found a cache in {record.filename}")
                        return record.load_df()

                logging.debug(f"No cache found. Calling {func_name} and caching it for future use.")
            except Exception as ex:
                logging.error("Error trying to load a prior cache. Continuing.", exc_info=ex)

            result = func(*args, **kwargs)

            try:
                logging.debug(f"Saving cache for next time: data={func_data}, expires={self.expires}")
                new_record = cache_record.CacheRecord(data=func_data, expires=self.expires)
                new_record.save()
                new_record.save_df(result)
            except Exception as ex:
                logging.error("Error trying to save results to the cache. Continuing.", exc_info=ex)

            return result

        return _cached
