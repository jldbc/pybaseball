from pybaseball.datahelpers.postprocessing import (
    augment_lahman_batting,
    aggregate_by_season,
)
from pybaseball.datasources.lahman import batting
from .marcels_base import MarcelsProjectionsBase


class MarcelProjectionsBatting(MarcelsProjectionsBase):
    COMPUTED_METRICS = [
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
    RECIPROCAL_AGE_METRICS = ["SO", "CS"]
    LEAGUE_AVG_PT = 100
    NUM_REGRESSION_PLAYING_TIME = 200
    METRIC_WEIGHTS = (5, 4, 3)
    PT_WEIGHTS = (0.5, 0.1, 0)
    REQUIRED_COLUMNS = ["AB", "BB"]
    PLAYING_TIME_COLUMN = "PA"

    def _load_data(self):
        return batting()

    def preprocess_data(self, stats_df):
        """
        preprocesses the data.
        :param stats_df: a data frame like Lahman batting
        :return: data frame
        """
        return aggregate_by_season(augment_lahman_batting(stats_df))

    def filter_non_representative_data(self, stats_df, primary_pos_df):
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
