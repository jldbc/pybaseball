from pybbda.data.tools.processing.aggregate import aggregate_by_season
from pybbda.data.tools.lahman.data import augment_lahman_pitching
from pybbda.analysis.projections.marcels.marcels_base import MarcelsProjectionsBase


class MarcelProjectionsPitching(MarcelsProjectionsBase):
    COMPUTED_METRICS = ["H", "HR", "ER", "BB", "SO", "HBP", "R"]
    RECIPROCAL_AGE_METRICS = ["H", "HR", "ER", "BB", "HBP", "R"]
    LEAGUE_AVG_PT = 134
    METRIC_WEIGHTS = (3, 2, 1)
    PT_WEIGHTS = (0.5, 0.1, 0)
    REQUIRED_COLUMNS = ["IPouts"]
    PLAYING_TIME_COLUMN = "IPouts"

    def __init__(self, stats_df=None, primary_pos_df=None):
        super().__init__(stats_df, primary_pos_df)

    def _load_data(self):
        return self.ld.pitching

    def preprocess_data(self, stats_df):
        """
        preprocesses teh data.
        :param stats_df: data frame like Lahman pitching
        :return: data frame
        """
        return aggregate_by_season(augment_lahman_pitching(stats_df))

    def filter_non_representative_data(self, stats_df, primary_pos_df):
        """
        filter batters-as-pitchers. primary_pos_df is a data frame
        containing playerID, yearID, and primaryPos

        :param stats_df: data frame like Lahman pitching
        :param primary_pos_df: data frame
        :return: data frame
        """
        return (
            stats_df.merge(primary_pos_df, on=["playerID", "yearID"], how="left")
            .query(r'primaryPos == "P"')
            .drop("primaryPos", axis=1)
        )

    def get_num_regression_pt(self, stats_df):
        """
        gets the number of batters-faced for the regression component.
        computed as a function of fraction of games as a starter.

        :param stats_df: data frame like Lahman pitching
        :return: numpy array
        """
        fraction_games_started = stats_df.apply(
            lambda row: row["GS"] / row["G"], axis=1
        ).values
        return 75 + 105 * fraction_games_started
