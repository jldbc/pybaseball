import re
from datetime import datetime
from typing import List, Union

import numpy as np
import pandas as pd

null_regexes = [r'^\s*$', r'^null$']
date_formats = [
    '%Y-%m-%d',              # Standard statcast format
    '%Y-%m-%dT%H:%M:%S.%fZ', # Just in case (https://github.com/jldbc/pybaseball/issues/104)
]

def try_parse(
    value: str,
    column_name: str,
    null_replacement: Union[str, int, float, datetime] = np.nan,
    known_percentages: List[str] = []
) -> Union[str, int, float, datetime]:
    for regex in null_regexes:
        if re.compile(regex).match(value):
            return null_replacement

    percentage = False

    # Is it a date?
    for date_format in date_formats:
        try:
            return datetime.strptime(value, date_format)
        except:
            pass

    # Is it an float or an int (including percetages)?
    try:
        if value.endswith('%') or column_name.endswith('%') or column_name in known_percentages:
            percentage = True

        if '.' in value:
            return float(value.strip(' %')) / (1 if not percentage else 100.0)
        else:
            result = int(value.strip(' %'))
            return result if not percentage else result / 100.0
    except:
        pass

    return value


def coalesce_nulls(data: pd.DataFrame, value: Union[str, int, float] = np.nan) -> pd.DataFrame:
    # Fill missing values with NaN
    for regex in null_regexes:
        data.replace(regex, value, regex=True, inplace=True)

    return data


def columns_except(data: pd.DataFrame, columns: List[str]) -> List[str]:
    return list(np.setdiff1d(data.columns, columns))


def convert_numeric(data: pd.DataFrame, numeric_columns: List[str]):
    # data.loc[data[numeric_cols] == ''] = None
    # data[numeric_cols] = data[numeric_cols].astype(float)
    # Ideally we'd do it the pandas way ^, but it's barfing when some columns have no data

    for col in numeric_columns:
        data[col] = data[col].astype(float)

    return data


def convert_percentages(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    # convert percent strings to float values
    for col in columns:
        # Skip if column is all NA (happens for some of the more obscure stats + in older seasons)
        if col in data.columns and data[col].count() > 0:
            data[col] = data[col].str.strip(' %')
            data[col] = data[col].astype(float)/100.0
        else:
            # print(col)
            pass

    return data
