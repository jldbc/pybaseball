from typing import List, Tuple

import pandas as pd

from pybaseball.datahelpers.postprocessing import aggregate_by_season, augment_lahman_batting
from pybaseball.lahman import batting

from .marcels_base import MarcelsProjectionsBase


class MarcelProjectionsBatting(MarcelsProjectionsBase):
    COMPUTED_METRICS: List[str] = [
        "1B",
        "2B",
        "3B",
        "HR",
        "BB",
        "HBP",
        "SB",
        "CS",
        "SO",
        "SH",
        "SF",
    ]
    RECIPROCAL_AGE_METRICS: List[str] = ["SO", "CS"]
    LEAGUE_AVG_PT: float = 100
    NUM_REGRESSION_PLAYING_TIME: float = 200
    METRIC_WEIGHTS: Tuple[float, float, float]  = (5, 4, 3)
    PT_WEIGHTS: Tuple[float, float, float] = (0.5, 0.1, 0)
    REQUIRED_COLUMNS: List[str] = ["AB", "BB"]
    PLAYING_TIME_COLUMN: str = "PA"

    def _load_data(self) -> pd.DataFrame:
        return batting()

    def preprocess_data(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """
        preprocesses the data.
        :param stats_df: a data frame like Lahman batting
        :return: data frame
        """
        return aggregate_by_season(augment_lahman_batting(stats_df))

    def filter_non_representative_data(self, stats_df: pd.DataFrame, primary_pos_df: pd.DataFrame) -> pd.DataFrame:
        """
        filters pitchers-as-batters. primary_pos_df is a data frame
        containing playerID, yearID, and primaryPos

        :param stats_df: a data frame like Lahman batting
        :param primary_pos_df: data frame
        :return:
        """
        return (
            stats_df.merge(primary_pos_df, on=["playerID", "yearID"], how="left")
            .query(r'primaryPos != "P"')
            .drop("primaryPos", axis=1)
        )
