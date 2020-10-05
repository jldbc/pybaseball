import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional, Union, cast

import pandas as pd

from . import cache_config, dataframe_utils, file_utils

cfg = cache_config.autoload_cache()

DateOrNumDays = Union[date, int]


class CacheRecord:
    def __init__(self, filename: str = None, data: Optional[Dict[str, Any]] = None,
                 expires: DateOrNumDays = cache_config.CacheConfig.DEFAULT_EXPIRATION):
        ''' Create a new cache record. Loads from file if filename is provided, otherwise creates from data, expires '''

        if filename is None and data is None:
            raise ValueError("CacheRecord must be instantiated with either a file or source data.")

        if filename:
            self.data = cast(Dict[str, Any], file_utils.load_json(filename))
            assert isinstance(self.data, dict)
            self.expiration_date = datetime.strptime(self.data['expires'], "%Y-%m-%d").date()
            self.filename = filename
            return

        assert data is not None

        if 'expires' not in data:
            if isinstance(expires, int):
                expires = date.today() + timedelta(days=expires)
            self.expiration_date = expires
            data['expires'] = str(expires)

        self.data = cast(Dict, data)
        base = self.data.get('func', 'unknown_call') + str(datetime.now().timestamp())
        base = os.path.join(cfg.cache_directory, base)
        frame_name = base + '.' + cfg.cache_type
        self.data['dataframe'] = frame_name
        self.filename = base + '.cache_record.json'

    def save(self) -> None:
        ''' Store the cache record to disk '''
        file_utils.safe_jsonify(cfg.cache_directory, self.filename, self.data)

    @property
    def expired(self) -> bool:
        return date.today() > self.expiration_date

    def load_df(self) -> pd.DataFrame:
        return dataframe_utils.load_df(self.data['dataframe'])

    def save_df(self, df: pd.DataFrame) -> None:
        dataframe_utils.save_df(df, self.data['dataframe'])

    def delete(self) -> None:
        df_filename = self.data.get('dataframe')
        if df_filename and os.path.exists(df_filename):
            file_utils.remove(df_filename)
        file_utils.remove(self.filename)

    def supports(self, function_data: Dict) -> bool:
        ''' Check if this record matches the function data '''
        for key in ('func', 'args', 'kwargs'):
            if self.data.get(key) != function_data.get(key):
                return False
        return True
