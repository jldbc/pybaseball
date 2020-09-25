import pandas as pd

from .cache_type import CacheType
from typing import Optional


def load(filename: str, cache_type: CacheType) -> pd.DataFrame:
    if cache_type in [CacheType.CSV, CacheType.CSV_BZ2, CacheType.CSV_GZ, CacheType.CSV_XZ, CacheType.CSV_ZIP]:
        data = pd.read_csv(filename)
    elif cache_type in [CacheType.FEATHER, CacheType.FEATHER_LZ4, CacheType.FEATHER_UNCOMPRESSED, CacheType.FEATHER_ZSTD]:
        data = pd.read_feather(filename)
    elif cache_type in [CacheType.JSON, CacheType.JSON_BZ2, CacheType.JSON_GZ, CacheType.JSON_XZ, CacheType.JSON_ZIP]:
        data = pd.read_json(filename)
    elif cache_type in [CacheType.PARQUET, CacheType.PARQUET_GZ, CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_GZ]:
        engine = 'pyarrow'
        if cache_type in [CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_GZ]:
            engine = 'fastparquet'
        data = pd.read_parquet(filename, engine=engine)
    elif cache_type in [CacheType.PICKLE, CacheType.PICKLE_BZIP, CacheType.PICKLE_GZ, CacheType.PICKLE_XZ, CacheType.PICKLE_ZIP]:
        data = pd.read_pickle(filename)
    else:
        raise ValueError(f"cache_type of {cache_type} is unsupported.")
    data.drop(
        data.columns[data.columns.str.contains('unnamed', case=False)],
        axis=1,
        inplace=True
    )
    return data

def save(data: pd.DataFrame, filename: str, cache_type: CacheType) -> None:
    compression: Optional[str] = None
    if cache_type in [CacheType.CSV, CacheType.CSV_BZ2, CacheType.CSV_GZ, CacheType.CSV_XZ, CacheType.CSV_ZIP]:
        data.to_csv(filename)
    elif cache_type in [CacheType.FEATHER, CacheType.FEATHER_LZ4, CacheType.FEATHER_UNCOMPRESSED, CacheType.FEATHER_ZSTD]:
        if cache_type == CacheType.FEATHER_LZ4:
            compression = 'lz4'
        elif cache_type == CacheType.FEATHER_UNCOMPRESSED:
            compression = 'uncompressed'
        elif cache_type == CacheType.FEATHER_ZSTD:
            compression = 'zstd'           
        # Have to reset_index otherwise you get a ValueError:
        # ValueError: feather does not support serializing a non-default index for the index; you can
        # .reset_index() to make the index into column(s)compression: Optional[str] = None
        data.reset_index(drop=True, inplace=True)
        data.to_feather(filename, compression=compression)
    elif cache_type  in [CacheType.JSON, CacheType.JSON_BZ2, CacheType.JSON_GZ, CacheType.JSON_XZ, CacheType.JSON_ZIP]:
        data.to_json(filename)
    elif cache_type in [CacheType.PARQUET, CacheType.PARQUET_GZ, CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_GZ]:
        engine = 'pyarrow'
        if cache_type in [CacheType.PARQUET_FAST, CacheType.PARQUET_FAST_GZ]:
            engine = 'fastparquet'
        elif  cache_type in [CacheType.PARQUET_GZ, CacheType.PARQUET_FAST_GZ]:
            compression = 'gzip'
        data.to_parquet(filename, engine=engine, compression=compression)
    elif cache_type in [CacheType.PICKLE, CacheType.PICKLE_BZIP, CacheType.PICKLE_GZ, CacheType.PICKLE_XZ, CacheType.PICKLE_ZIP]:
        data.to_pickle(filename)
    else:
        raise ValueError(f"cache_type of {cache_type} is unsupported.")
