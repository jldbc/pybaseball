import copy
import hashlib
import logging
import os
import pathlib
import pickle
import re
import shutil
import traceback
from datetime import datetime, timedelta
from enum import Enum, unique
from typing import Any, Callable, Dict, Hashable, Iterable, Optional, Tuple, Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


@unique
class CacheType(Enum):
    CSV = 'csv'
    CSV_GZ = 'csv.gz'
    PARQUET = 'parquet'
    PICKLE = 'pickle'


# Splitting this out for testing with no side effects
def _mkdir(directory: str) -> None:
    return pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

# Splitting this out for testing with no side effects
def _remove(filename: str) -> None:
    return os.remove(filename)

# Splitting this out for testing with no side effects
def _rmtree(directory: str) -> None:
    return shutil.rmtree(directory)


class CacheConfig:
    DEFAULT_CACHE_DIR = os.path.join(pathlib.Path.home(), '.pybaseball', 'cached_data')
    DEFAULT_EXPIRATION = timedelta(hours=24)

    # pylint: disable=too-many-arguments
    def __init__(self, enabled: bool = False, cache_directory: str = None, expiration: timedelta = None,
                 cache_type: CacheType = None):
        self.enabled = enabled
        self.cache_directory = cache_directory if cache_directory else CacheConfig.DEFAULT_CACHE_DIR
        self.expiration = expiration if expiration else CacheConfig.DEFAULT_EXPIRATION
        self.cache_type = cache_type if cache_type is not None else CacheType.CSV

        _mkdir(self.cache_directory)

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled


# Cache is disabled by default
cache_config = CacheConfig(enabled=False)


class dataframe_cache:  # pylint: disable=invalid-name
    MAX_ARGS_KEY_LENGTH = 256

    @staticmethod
    def _get_value_hash(value: Optional[Union[str, Dict, Hashable, Iterable]], include_designators: bool = True) -> str:
        if value is None:
            return 'None'

        if isinstance(value, str):
            # Remove invalid filename characters
            stripped = copy.copy(value)
            stripped = str(stripped).strip().replace(' ', '_')
            stripped = re.sub(r'(?u)[^-\w.]', '', stripped)
            if value == stripped:
                # If nothing got changed, then the value is safe
                if include_designators:
                    return f"'{value}'" if "'" not in value else f"\"{value}\""
                return f"{value}"

        if isinstance(value, dict):
            values = ', '.join([
                f"{dataframe_cache._get_value_hash(key, include_designators=False)}={dataframe_cache._get_value_hash(value[key])}"
                for key in value.keys()
            ]).strip(', ')
            if include_designators:
                return "{" + values + "}"
            return values

        if isinstance(value, tuple):
            values = ', '.join([f"{dataframe_cache._get_value_hash(sub_value)}" for sub_value in value]).strip(', ')
            if include_designators:
                return f"({values})"
            return f"{values}"

        if isinstance(value, list):
            values = ', '.join([f"{dataframe_cache._get_value_hash(sub_value)}" for sub_value in value]).strip(', ')
            if include_designators:
                return f"[{values}]"
            return f"{values}"

        try:
            return str(value.__hash__())
        except:
            raise ValueError(f"value {value} of type {type(value)} is not hashable.")

    @staticmethod
    def _get_f_name(func: Callable) -> str:
        if '__self__' in dir(func):
            # This is a class method
            return f"{func.__getattribute__('__self__').__class__.__name__}.{func.__name__}"
        return f"{func.__name__}"

    @staticmethod
    def _get_f_hash(func: Callable, args: Tuple, kwargs: Dict) -> str:
        f_hash = f"{dataframe_cache._get_f_name(func)}"

        args_hash = dataframe_cache._get_value_hash(args, include_designators=False)
        kwargs_hash = dataframe_cache._get_value_hash(kwargs, include_designators=False)

        args_key = ', '.join([args_hash, kwargs_hash]).strip(', ')

        # If the args_key is very long, just use a sha hash

        if len(args_key) > dataframe_cache.MAX_ARGS_KEY_LENGTH:
            # Let's hash this to make the filename shorter
            args_key = hashlib.sha256(args_key.encode('utf-8')).hexdigest()

        return f"{f_hash}({args_key})"

    @property
    def extension(self) -> str:
        return str(self.cache_config.cache_type.value)

    def __init__(self, cache_config_override: CacheConfig = None, reset_cache: bool = False):
        if cache_config_override:
            self.cache_config = cache_config_override
        else:
            self.cache_config = cache_config
        self.reset_cache = reset_cache
        _mkdir(self.cache_config.cache_directory)

    def __call__(self, func: Callable[..., pd.DataFrame]) -> Callable:
        def _cached(*args: Any, **kwargs: Any) -> pd.DataFrame:
            # Skip all this if caching is disabled
            if not self.cache_config.enabled:
                return func(*args, **kwargs)

            filename = None

            try:
                f_hash = dataframe_cache._get_f_hash(func, args, kwargs)
                filename = os.path.join(self.cache_config.cache_directory, f"{f_hash}.{self.extension}")

                if os.path.exists(filename):
                    modified = datetime.fromtimestamp(os.path.getmtime(filename))
                    if (modified + self.cache_config.expiration) > datetime.now():
                        # Hasn't expired yet
                        return self.load(filename)
            except:  # pylint: disable=broad-except
                # If this fails, log it, and then go ahead and make the function call
                # No need to crash the real work in this phase
                for ex in traceback.format_exc().split('\n'):
                    logging.error(ex)

            result = func(*args, **kwargs)

            if filename and result is not None and isinstance(result, pd.DataFrame) and not result.empty:
                self.save(result, filename)

            return result

        if self.reset_cache:
            self.bust_cache(func)

        return _cached

    def bust_cache(self, func: Callable) -> None:
        cache_files = [
            x for x in os.walk(self.cache_config.cache_directory).__next__()[2] if x.startswith(f"{func.__name__}(")
        ]
        for cache_file in cache_files:
            _remove(os.path.join(self.cache_config.cache_directory, cache_file))
        self.reset_cache = False

    def load(self, filename: str) -> pd.DataFrame:
        if self.cache_config.cache_type in [CacheType.CSV, CacheType.CSV_GZ]:
            data = pd.read_csv(filename)
        elif self.cache_config.cache_type == CacheType.PARQUET:
            data = pq.read_table(filename).to_pandas()
        elif self.cache_config.cache_type == CacheType.PICKLE:
            with open(filename, 'rb') as data_pickled:
                data = pickle.load(data_pickled)
        else:
            raise ValueError(f"cache_type of {self.cache_config.cache_type} is unsupported.")
        data.drop(
            data.columns[data.columns.str.contains('unnamed', case=False)],
            axis=1,
            inplace=True
        )
        return data

    def save(self, data: pd.DataFrame, filename: str) -> None:
        if self.cache_config.cache_type in [CacheType.CSV, CacheType.CSV_GZ]:
            data.to_csv(filename)
        elif self.cache_config.cache_type == CacheType.PARQUET:
            pq.write_table(pa.Table.from_pandas(data), filename)
        elif self.cache_config.cache_type == CacheType.PICKLE:
            with open(filename, 'wb') as data_pickled:
                pickle.dump(data, data_pickled)
        else:
            raise ValueError(f"cache_type of {self.cache_config.cache_type} is unsupported.")


def bust_cache() -> None:
    _rmtree(cache_config.cache_directory)
    _mkdir(cache_config.cache_directory)
