from enum import Enum, unique

@unique
class CacheType(Enum):
    CSV = 'csv'
    PARQUET = 'parquet'
    PICKLE = 'pickle'
