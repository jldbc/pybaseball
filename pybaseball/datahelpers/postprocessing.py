import re
from datetime import datetime
from typing import Dict, List, Union

import numpy as np
import pandas as pd

null_regexes = [r'^\s*$', r'^null$']
date_formats = [
    '%Y-%m-%d',              # Standard statcast format
    '%Y-%m-%dT%H:%M:%S.%fZ', # Just in case (https://github.com/jldbc/pybaseball/issues/104)
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



def get_primary_position(fielding_df: pd.DataFrame) -> pd.DataFrame:
    """
    Determines the primary position of a player during a season. `fielding_df` is
    a DataFrame similar to Lahman Fielding, i.e. it must contain columns, `playerID`,
    `yearID`, `POS`, and `G`.

    :param fielding_df:
    :return: DataFrame
    """

    fld_combined_stints = (
        fielding_df.groupby(["playerID", "yearID", "POS"]).sum().reset_index()
    )
    gm_rank_df = (
        fld_combined_stints.groupby(["playerID", "yearID"])
        .G.rank(method="first", ascending=False)
        .to_frame()
        .rename({"G": "gm_rank"}, axis=1)
    )
    return (
        pd.concat((fld_combined_stints, gm_rank_df), axis=1)
        .query("gm_rank == 1")
        .drop("gm_rank", axis=1)
        .filter(["playerID", "yearID", "POS"])
        .rename({"POS": "primaryPos"}, axis=1)
    )


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
