from typing import List

import numpy as np
import pandas as pd


def coalesce_nulls(data: pd.DataFrame, value: any = np.nan) -> pd.DataFrame:
    # fill missing values with NaN
    data.replace(r'^\s*$', value, regex=True, inplace=True)
    data.replace(r'^null$', value, regex=True, inplace=True)

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
