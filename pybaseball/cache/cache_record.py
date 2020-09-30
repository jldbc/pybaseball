import json
import os
from datetime import datetime, date, timedelta

import pandas as pd
from typing import Dict, List, Tuple, Union, Optional
from .cache_config import CacheConfig, autoload_cache
from .file_utils import safe_jsonify, load_json, _remove
from .dataframe_utils import load_df, save_df

cfg = autoload_cache()

DateOrNumDays = Union[date, int]

class CacheRecord:
    def __init__(self, filename: str = None, data: Dict = None, expires: Optional[DateOrNumDays] = None):
        ''' Create a new cache record. Loads from file if filename is provided, otherwise creates from data, expires '''
        if filename:
            self.data = load_json(filename)
            self.expiration_date = datetime.strptime(self.data['expires'], "%Y-%m-%d").date()
            self.filename = filename
            return
        
        if 'expires' not in data:
            if type(expires) == int:
                expires = date.today() + timedelta(days=expires)
            expires = expires or date.today() + cfg.DEFAULT_EXPIRATION # Note: day level resolution?
            self.expiration_date = expires
            data['expires'] = str(expires)
        else:
            self.expiration_date = datetime.strptime(self.data['expires'], "%Y-%m-%d").date()
        self.data = data
        base = self.data.get('func', 'unknown_call') + str(datetime.now().timestamp())
        base = os.path.join(cfg.cache_directory, base)
        frame_name = base + '.' + cfg.cache_type
        self.data['dataframe'] = frame_name
        self.filename = base + '.cache_record.json'
    
    def save(self) -> None:
        ''' Store the cache record to disk '''
        safe_jsonify(cfg.cache_directory, self.filename, self.data)

    @property
    def expired(self) -> bool:
        return date.today() > self.expiration_date

    def load_df(self):
        return load_df(self.data['dataframe'])

    def save_df(self, df: pd.DataFrame) -> None:
        save_df(df, self.data['dataframe'])

    def delete(self):
        df_filename = self.data.get('dataframe')
        if df_filename:
            _remove(df_filename)
        _remove(self.filename)

    def supports(self, function_data: Dict) -> bool:
        ''' Check if this record matches the function data '''
        keys = ('func', 'args', 'kwargs')
        for key in keys:
            if self.data.get(key) != function_data.get(key):
                return False
        return True

