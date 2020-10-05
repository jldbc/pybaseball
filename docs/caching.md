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
* It supports the following cache storage options: 'CSV' or 'Parquet'
    * Changing the storage mechanism:
    ```python
    from pybaseball import cache
    
    cache.enable()
    cache.config.cache_type='csv'
    cache.config.save()
    ```
    * Default cache type is Parquet.
* Cache directory can also be configured by setting the `PYBASEBALL_CACHE` environment variable to your desired cache directory.
* Lahman data is cached and `lahman.download_lahman()` places its data to the cache directory.
* This cache is intelligent only at the function parameter level, meaning that calls to the same function with the same params will reuse the same cache value. For simplicity, for now, the cache purposefully does not do any subset cache. E.g., a call to `pybaseball.batting_leaders(2000, 2020)`, a follow up call to `pybaseball.batting_leaders(2010, 2015)` will not attempt to reuse the cache, despite likely having the data to do so.
