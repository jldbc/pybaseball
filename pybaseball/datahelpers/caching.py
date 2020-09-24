import copy
import hashlib
import logging
import os
import pathlib
import pickle
import re
import shutil
import time
import traceback
from datetime import datetime, timedelta
from enum import Enum, unique
from typing import Any, Callable, Dict, Hashable, Iterable, Optional, Tuple, Union

import pandas as pd


@unique
class CacheType(Enum):
    CSV = 'csv'
    CSV_BZ2 = 'csv.bz2'
    CSV_GZ = 'csv.gz'
    CSV_XZ = 'csv.xz'
    CSV_ZIP = 'csv.zip'
    EXCEL = 'xlsx'
    FEATHER = 'feather'
    FEATHER_LZ4 = 'lz4.feather'
    FEATHER_UNCOMPRESSED = 'uc.feather'
    FEATHER_ZSTD = 'zstd.feather'
    JSON = 'json'
    JSON_BZ2 = 'json.bz2'
    JSON_GZ = 'json.gz'
    JSON_XZ = 'json.xz'
    JSON_ZIP = 'json.zip'
    PARQUET = 'parquet'
    PARQUET_BROTLI = 'brotli.parquet'
    PARQUET_GZ = 'gz.parquet'
    PARQUET_SNAPPY = 'snappy.parquet'
    PARQUET_FAST = 'fast.parquet'
    PARQUET_FAST_BROTLI = 'fast.brotli.parquet'
    PARQUET_FAST_GZ = 'fast.gz.parquet'
    PARQUET_FAST_SNAPPY = 'fast.snappy.parquet'
    PICKLE = 'pickle'
    PICKLE_BZIP = 'pickle.bzip'
    PICKLE_GZ = 'pickle.gz'
    PICKLE_XZ = 'pickle.xz'
    PICKLE_ZIP = 'pickle.zip'


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
                 cache_type: CacheType = None, profiling: bool = False):
        self.enabled = enabled
        self.cache_directory = cache_directory if cache_directory else CacheConfig.DEFAULT_CACHE_DIR
        self.expiration = expiration if expiration else CacheConfig.DEFAULT_EXPIRATION
        self.cache_type = cache_type if cache_type is not None else CacheType.CSV
        self.profiling = profiling

        _mkdir(self.cache_directory)

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled


# Cache is disabled by default
cache_config = CacheConfig()

_ProfiledCachedDataFrame = Union[pd.DataFrame, Tuple[pd.DataFrame, Optional[float], Optional[float], Optional[float]]]

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
            # Skip all this if caching is disabled
            if not self.cache_config.enabled:
                return func(*args, **kwargs)

            read_time = None
            write_time = None
            filename = None

            try:
                f_hash = dataframe_cache._get_f_hash(func, args, kwargs)
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
                    print(f"EXCEPTION: {ex}")
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
        if self.cache_config.cache_type in [CacheType.CSV, CacheType.CSV_BZ2, CacheType.CSV_GZ, CacheType.CSV_XZ, CacheType.CSV_ZIP]:
            data = pd.read_csv(filename)
        elif self.cache_config.cache_type == CacheType.EXCEL:
            data = pd.read_excel(filename, engine='openpyxl')
        elif self.cache_config.cache_type in [CacheType.FEATHER, CacheType.FEATHER_LZ4, CacheType.FEATHER_UNCOMPRESSED, CacheType.FEATHER_ZSTD]:
            data = pd.read_feather(filename)
        elif self.cache_config.cache_type in [CacheType.JSON, CacheType.JSON_BZ2, CacheType.JSON_GZ, CacheType.JSON_XZ, CacheType.JSON_ZIP]:
            data = pd.read_json(filename)
        elif self.cache_config.cache_type in [CacheType.PARQUET, CacheType.PARQUET_BROTLI, CacheType.PARQUET_GZ, CacheType.PARQUET_SNAPPY, CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_BROTLI, CacheType.PARQUET_FAST_GZ, CacheType.PARQUET_FAST_SNAPPY]:
            engine = 'pyarrow'
            if self.cache_config.cache_type in [CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_BROTLI, CacheType.PARQUET_FAST_GZ, CacheType.PARQUET_FAST_SNAPPY]:
                engine = 'fastparquet'
            data = pd.read_parquet(filename, engine=engine)
        elif self.cache_config.cache_type in [CacheType.PICKLE, CacheType.PICKLE_BZIP, CacheType.PICKLE_GZ, CacheType.PICKLE_XZ, CacheType.PICKLE_ZIP]:
            data = pd.read_pickle(filename)
        else:
            raise ValueError(f"cache_type of {self.cache_config.cache_type} is unsupported.")
        data.drop(
            data.columns[data.columns.str.contains('unnamed', case=False)],
            axis=1,
            inplace=True
        )
        return data

    def save(self, data: pd.DataFrame, filename: str) -> None:
        compression: Optional[str] = None
        if self.cache_config.cache_type in [CacheType.CSV, CacheType.CSV_BZ2, CacheType.CSV_GZ, CacheType.CSV_XZ, CacheType.CSV_ZIP]:
            data.to_csv(filename)
        elif self.cache_config.cache_type == CacheType.EXCEL:
            data.to_excel(filename, engine='openpyxl')
        elif self.cache_config.cache_type in [CacheType.FEATHER, CacheType.FEATHER_LZ4, CacheType.FEATHER_UNCOMPRESSED, CacheType.FEATHER_ZSTD]:
            if self.cache_config.cache_type == CacheType.FEATHER_LZ4:
                compression = 'lz4'
            elif self.cache_config.cache_type == CacheType.FEATHER_UNCOMPRESSED:
                compression = 'uncompressed'
            elif self.cache_config.cache_type == CacheType.FEATHER_ZSTD:
                compression = 'zstd'           
            # Have to reset_index otherwise you get a ValueError:
            # ValueError: feather does not support serializing a non-default index for the index; you can
            # .reset_index() to make the index into column(s)compression: Optional[str] = None
            data.reset_index(drop=True, inplace=True)
            data.to_feather(filename, compression=compression)
        elif self.cache_config.cache_type  in [CacheType.JSON, CacheType.JSON_BZ2, CacheType.JSON_GZ, CacheType.JSON_XZ, CacheType.JSON_ZIP]:
            data.to_json(filename)
        elif self.cache_config.cache_type in [CacheType.PARQUET, CacheType.PARQUET_BROTLI, CacheType.PARQUET_GZ, CacheType.PARQUET_SNAPPY, CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_BROTLI, CacheType.PARQUET_FAST_GZ, CacheType.PARQUET_FAST_SNAPPY]:
            engine = 'pyarrow'
            if self.cache_config.cache_type in [CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_BROTLI, CacheType.PARQUET_FAST_GZ, CacheType.PARQUET_FAST_SNAPPY]:
                engine = 'fastparquet'
            if self.cache_config.cache_type in [CacheType.PARQUET_BROTLI, CacheType.PARQUET_FAST_BROTLI]:
                # compression = 'brotli'
                # This should work according to
                # However, getting:
                # RuntimeError: Compression 'brotli' not available.  Options: ['GZIP', 'SNAPPY', 'UNCOMPRESSED']
                # So we'll treat this like default Parquet for now.
                pass
            elif  self.cache_config.cache_type in [CacheType.PARQUET_GZ, CacheType.PARQUET_FAST_GZ]:
                compression = 'gzip'
            elif self.cache_config.cache_type in [CacheType.PARQUET_SNAPPY, CacheType.PARQUET_FAST_SNAPPY]:
                compression = 'snappy'
            data.to_parquet(filename, engine=engine, compression=compression)
        elif self.cache_config.cache_type in [CacheType.PICKLE, CacheType.PICKLE_BZIP, CacheType.PICKLE_GZ, CacheType.PICKLE_XZ, CacheType.PICKLE_ZIP]:
            data.to_pickle(filename)
        else:
            raise ValueError(f"cache_type of {self.cache_config.cache_type} is unsupported.")


def bust_cache() -> None:
    try:
        _rmtree(cache_config.cache_directory)
    except:
        pass
    _mkdir(cache_config.cache_directory)
