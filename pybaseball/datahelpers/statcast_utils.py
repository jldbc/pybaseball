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
