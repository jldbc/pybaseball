# Caching Usage

* Cache is disabled by default
    * Enabling cache:
    ```python
    from pybaseball import cache
    
    cache.enable()
    ```
    * Disabling cache:
    ```python
    from pybaseball import cache
    
    cache.disable()
    ```
    * If cache is ever enabled by default later, cache is purposefully disabled before all unit tests to prevent false results.
* By default it will cache to the `.pybaseball/cache` folder in the user's home directory, so cache can be used across projects (directory will be created if not present).
* It supports the following cache storage options: CSV, GZipped CSV, Excel, Feather, JSON, Parquet, Pickle
    * Changing the storage mechanism:
    ```python
    from pybaseball import cache
    
    cache.cache_config = cache.CacheConfig(enabled=True, cache_type=cache.CacheType.PICKLE)
    ```
    * Cache speed tests. Each represents an initial load of 5 different functions, and then 9 cached loads:
        * CSV: 6.921 seconds (File sizes were from 3.7 KB to 1.2 MB)
        * CSV_GZ: 7.436 seconds (File sizes were from 1.5 KB to 373 KB)
        * EXCEL: 179.266! seconds (File sizes were from 8.3 KB to 1.2 MB)
        * FEATHER: 6.031 seconds (File sizes were from 13 KB to 856 KB)
        * JSON: 10.195 seconds (File sizes were from 5.9 KB to 2.9 MB)
        * PARQUET: 6.679 (File sizes were from 16 KB to 645 KB)
        * PICKLE: 5.875 (File sizes were from 7 KB to 2.3 MB)
    * Cache speed tests. Each represents an initial load of 5 different functions, and then 999 cached loads:
        * CSV: 118.940 seconds
        * CSV_GZ: 127.987 seconds
        * EXCEL: Not tested based off the 10 iteration result
        * FEATHER: 42.061 seconds
        * JSON: 432.338 seconds
        * PARQUET: 95.881 seconds
        * PICKLE: 22.616 seconds
    * Default cache type is CSV.
* Expirations can be set on a cache, where cache files past a certain timedelata will be ignored/discarded:
    ```python
    from datetime import timedelta
    
    from pybaseball import cache
    
    cache.cache_config = cache.CacheConfig(enabled=True, expiration=timedelta(days=7))
    ```
* Cache directory can also be configured if desired
    ```python
    from pybaseball import cache
    
    cache.cache_config = cache.CacheConfig(enabled=True, cache_directory='.')
    ```
* Lahman data is cached and `lahman.download_lahman()` places its data to the cache directory.
* This cache is intelligent only at the function parameter level, meaning that calls to the same function with the same params will reuse the same cache value. For simplicity, for now, the cache purposefully does not do any subset cache. E.g., a call to `pybaseball.batting_leaders(2000, 2020)`, a follow up call to `pybaseball.batting_leaders(2010, 2015)` will not attempt to reuse the cache, despite likely having the data to do so.
