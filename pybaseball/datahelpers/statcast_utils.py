import numpy as np
import pandas as pd


def add_spray_angle(raw_df: pd.DataFrame, adjusted: bool = False) -> pd.DataFrame:
    """Adds spray angle and adjusted spray angle to StatCast DataFrames
    - Spray angle is the raw left-right angle of the hit
    - Adjusted spray angle flips the sign for left handed batters, making it a push/pull angle

    Args:
        df (pd.DataFrame): StatCast pd.DataFrame (retrieved through statcast, statcast_batter, etc)
    Returns:
        pd.DataFrame: Input dataframe with spray angle columns appended
    """

    df = raw_df.copy()

    df["spray_angle"] = np.arctan((df["hc_x"] - 125.42) / (198.27 - df["hc_y"])) * 180 / np.pi * .75
    if adjusted:
        df["adj_spray_angle"] = df.apply(
            lambda row: -row["spray_angle"] if row["stand"] == "L" else row["spray_angle"],
            axis=1
        )
        df = df.drop(["spray_angle"], axis=1)
    return df

def add_vertical_approach_angle(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Adds vertical approach angle to a StatCast DataFrame
    - Vertical approach angle is the angle, in degrees, at which the ball crosses home plate
    Args:
        raw_df (pd.DataFrame): StatCast pd.DataFrame (retrieved through statcast, statcast_pitcher, etc)
    Returns:
        pd.DataFrame: Input dataframe with vertical approach angle column appended
    """

    df = raw_df.copy()

    vy_f = -1 * np.sqrt(df['vy0']**2 - (2 * df['ay'] * (50 - (17 / 12))))
    t = (vy_f - df['vy0']) / df['ay']
    vz_f = df['vz0'] + (df['az'] * t)
    df['vaa'] = -1 * np.arctan(vz_f / vy_f) * (180 / np.pi)

    return df