import pandas as pd

from .cache_type import CacheType
from typing import Optional


def load(filename: str, cache_type: CacheType) -> pd.DataFrame:
    if cache_type == CacheType.CSV:
        data = pd.read_csv(filename)
    elif cache_type == CacheType.PARQUET:
        data = pd.read_parquet(filename)
    elif cache_type == CacheType.PICKLE:
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
    if cache_type == CacheType.CSV:
        data.to_csv(filename)
    elif cache_type == CacheType.PARQUET:
        data.to_parquet(filename)
    elif cache_type == CacheType.PICKLE:
        data.to_pickle(filename)
    else:
        raise ValueError(f"cache_type of {cache_type} is unsupported.")
