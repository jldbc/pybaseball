import re
from datetime import datetime
from typing import Any, List, Union, Optional

import attr
import numpy as np
import pandas as pd

null_regexes = [
    re.compile(r'^\s*$'),
    re.compile(r'^null$', re.RegexFlag.IGNORECASE)
]

date_formats = [
    # Standard statcast format
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'), '%Y-%m-%d'),

    # Just in case (https://github.com/jldbc/pybaseball/issues/104)
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$'), '%Y-%m-%dT%H:%M:%S.%fZ'),
]


def try_parse_dataframe(
    data: pd.DataFrame,
    parse_numerics: bool = True,
    null_replacement: Union[str, int, float, datetime] = np.nan,
    known_percentages: Optional[List[str]] = None
) -> pd.DataFrame:
    data_copy = data.copy()

    if parse_numerics:
        data_copy = coalesce_nulls(data_copy, null_replacement)
        data_copy = data_copy.apply(
            pd.to_numeric,
            errors='ignore',
            downcast='signed'
        ).convert_dtypes(convert_string=False)

    string_columns = [
        dtype_tuple[0] for dtype_tuple in data_copy.dtypes.items() if str(dtype_tuple[1]) in ["object", "string"]
    ]
    for column in string_columns:
        # Only check the first value of the column and test that;
        # this is faster than blindly trying to convert entire columns
        first_value_index = data_copy[column].first_valid_index()
        if first_value_index is None:
            # All nulls
            continue
        first_value = data_copy[column].loc[first_value_index]

        if str(first_value).endswith('%') or column.endswith('%') or \
                (known_percentages is not None and column in known_percentages):
            data_copy[column] = data_copy[column].astype(str).str.replace("%", "").astype(float) / 100.0
        else:
            # Doing it this way as just applying pd.to_datetime on
            # the whole dataframe just tries to gobble up ints/floats as timestamps
            for date_regex, date_format in date_formats:
                if isinstance(first_value, str) and date_regex.match(first_value):
                    data_copy[column] = data_copy[column].apply(pd.to_datetime, errors='ignore', format=date_format)
                    data_copy[column] = data_copy[column].convert_dtypes(convert_string=False)
                    break

    return data_copy


# pylint: disable=too-many-return-statements
def try_parse(
    value: Union[None, str, int, datetime, float],
    column_name: str,
    null_replacement: Union[str, int, float, datetime] = np.nan,
    known_percentages: Optional[List[str]] = None
) -> Union[str, int, float, datetime]:
    if value is None:
        return null_replacement

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
            except:  # pylint: disable=bare-except
                pass

    # Is it an float or an int (including percetages)?
    try:
        percentage = (
            value.endswith('%') or column_name.endswith('%') or \
            (known_percentages is not None and  column_name in known_percentages)
        )
        if percentage:
            return try_parse_percentage(value)

        if '.' in value:
            return float(value)

        return int(value)
    except:  # pylint: disable=bare-except
        pass

    return value


def try_parse_percentage(value: str) -> float:
    return float(value.strip(' %')) / 100.0


def coalesce_nulls(data: pd.DataFrame, value: Union[str, int, float, datetime] = np.nan) -> pd.DataFrame:
    # Fill missing values with NaN
    for regex in null_regexes:
        data.replace(regex.pattern, value, regex=True, inplace=True)

    return data


def columns_except(data: pd.DataFrame, columns: List[str]) -> List[str]:
    return list(np.setdiff1d(data.columns, columns))


def convert_numeric(data: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
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
            data[col] = data[col].astype(float) / 100.0
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
    plate_appearances = bat_df.loc[:, "AB"].fillna(0)
    for stat in ["BB", "HBP", "SH", "SF"]:
        plate_appearances += bat_df.loc[:, stat].fillna(0)
    return plate_appearances.astype(int)


def augment_lahman_batting(bat_df: pd.DataFrame) -> pd.DataFrame:
    """
    augments the Lahman batting data frame, with PA, X1B (singles), and TB.

    :param bat_df:
    :return:
    """
    plate_appearances = compute_pa(bat_df)
    singles = (
        bat_df.loc[:, "H"]
        - bat_df.loc[:, "2B"]
        - bat_df.loc[:, "3B"]
        - bat_df.loc[:, "HR"]
    )
    total_bases = (
        bat_df.loc[:, "HR"] * 4
        + bat_df.loc[:, "3B"] * 3
        + bat_df.loc[:, "2B"] * 2
        + singles
    )
    return bat_df.assign(
        PA=plate_appearances.astype(int),
        X1B=singles.astype(int),
        TB=total_bases.astype(int)
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

# pylint: disable=unused-argument
def check_is_zero_one(instance: Any, attribute: attr.Attribute, value: Union[int, float]) -> None:
    if value not in [0, 1]:
        raise ValueError(f"{attribute} must be either 0 or 1, not {value}")

# pylint: disable=unused-argument
def check_greater_zero(instance: Any, attribute: attr.Attribute, value: Union[int, float]) -> None:
    if value <= 0:
        raise ValueError(
            f"{attribute} must be greater than zero, not {value}"
        )

# pylint: disable=unused-argument
def check_between_zero_one(instance: Any, attribute: attr.Attribute, value: Union[int, float]) -> None:
    if not 0 <= value <= 1:
        raise ValueError(
            f"{attribute} must be between zero and one, not {value}"
        )
