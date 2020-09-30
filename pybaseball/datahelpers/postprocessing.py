import re
from datetime import datetime
from typing import List, Union

import numpy as np
import pandas as pd

null_regexes = [
    re.compile(r'^\s*$'),
    re.compile(r'^null$', re.RegexFlag.IGNORECASE)
]

date_formats = [
    # Standard statcast format
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'),                            '%Y-%m-%d'),

    # Just in case (https://github.com/jldbc/pybaseball/issues/104)
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$'), '%Y-%m-%dT%H:%M:%S.%fZ'),
]

def try_parse_dataframe(
    data: pd.DataFrame,
    null_replacement: Union[str, int, float, datetime] = np.nan,
    known_percentages: List[str] = []
) -> pd.DataFrame:
    values = [
        {column: try_parse(data[column][row_i], column) for column in data.columns}
        for row_i in range(len(data)) 
    ]

    return pd.DataFrame(values)

def try_parse(
    value: str,
    column_name: str,
    null_replacement: Union[str, int, float, datetime] = np.nan,
    known_percentages: List[str] = []
) -> Union[str, int, float, datetime]:
    if not isinstance(value, str):
        return value

    for regex in null_regexes:
        if regex.match(value):
            return null_replacement

    # Is it a date?
    for date_regex, date_format in date_formats:
        if date_regex.match(value):
            try:
                return datetime.strptime(value, date_format)
            except:
                pass

    # Is it an float or an int (including percetages)?
    try:
        percentage = (value.endswith('%') or column_name.endswith('%') or column_name in known_percentages)
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


def compute_pa(bat_df: pd.DataFrame) -> pd.Series:
    """
    Computes PA, using AB, HBP, SH, and SF. If any of those columns are null,
    they're filled with 0

    :param bat_df:
    :return:
    """
    PA = bat_df.loc[:, "AB"].fillna(0)
    for stat in ["BB", "HBP", "SH", "SF"]:
        PA += bat_df.loc[:, stat].fillna(0)
    return PA.astype(int)


def augment_lahman_batting(bat_df: pd.DataFrame) -> pd.DataFrame:
    """
    augments the Lahman batting data frame, with PA, X1B (singles), and TB.

    :param bat_df:
    :return:
    """
    PA = compute_pa(bat_df)
    X1B = (
        bat_df.loc[:, "H"]
        - bat_df.loc[:, "2B"]
        - bat_df.loc[:, "3B"]
        - bat_df.loc[:, "HR"]
    )
    TB = (
        bat_df.loc[:, "HR"] * 4
        + bat_df.loc[:, "3B"] * 3
        + bat_df.loc[:, "2B"] * 2
        + X1B
    )
    return bat_df.assign(
        PA=PA.astype(int), X1B=X1B.astype(int), TB=TB.astype(int)
    ).rename({"X1B": "1B"}, axis=1)


def augment_lahman_pitching(stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    augments the Lahman pitching data frame. currently a noop.

    :param stats_df:
    :return:
    """
    return stats_df

def aggregate_by_season(stats_df: pd.DataFrame) -> pd.DataFrame:
    return stats_df.groupby(["playerID", "yearID"]).sum().reset_index()

def check_is_zero_one(instance, attribute, value):
    if value not in [0, 1]:
        raise ValueError(f"{attribute} must be either 0 or 1, not {value}")


def check_greater_zero(instance, attribute, value):
    if value <= 0:
        raise ValueError(
            f"{attribute} must be greater than zero, not {value}"
        )


def check_between_zero_one(instance, attribute, value):
    if not 0 <= value <= 1:
        raise ValueError(
            f"{attribute} must be between zero and one, not {value}"
        )
