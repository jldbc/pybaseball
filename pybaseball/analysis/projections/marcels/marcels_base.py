"""
Module defining base class for marcel projections. Marcel projections are defined as the minimal projections system
that does anything reasonable. They

* make a rate projection based on last 3 seasons
    * projection is weighted average of performance plus a regression to the mean
* make a playing time projection

for batters the weights are 5, 4, 3 and for pitchers 3, 2, 1

The original description of Marcels is in this post by Tom Tango
http://www.tangotiger.net/archives/stud0346.shtml
"""
import sys
from abc import ABC
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from pybaseball.datahelpers.transform import get_age, get_primary_position
from pybaseball.lahman import fielding, people

from .age_adjustment import age_adjustment


class MarcelsProjectionsBase(ABC):
    COMPUTED_METRICS: List[str] = []
    RECIPROCAL_AGE_METRICS: List[str] = []
    LEAGUE_AVG_PT: Optional[float] = None
    NUM_REGRESSION_PLAYING_TIME: Optional[float] = None
    METRIC_WEIGHTS: Tuple[float, float, float] = (5, 4, 3)
    PT_WEIGHTS: Tuple[float, float, float] = (0.5, 0.1, 0)
    REQUIRED_COLUMNS: List[str] = []
    PLAYING_TIME_COLUMN: Optional[str] = None

    def __init__(self, stats_df: pd.DataFrame = None, primary_pos_df: pd.DataFrame = None):

        self.stats_df = stats_df if stats_df is not None else self._load_data()
        self.validate_data(self.stats_df)
        self.stats_df = self.preprocess_data(self.stats_df)

        self.primary_pos_df = (
            get_primary_position(fielding())
            if primary_pos_df is None
            else primary_pos_df
        )
        self.metric_weights = np.array(self.METRIC_WEIGHTS)
        self.pt_weights = np.array(self.PT_WEIGHTS)
        self.league_avg_pa = self.LEAGUE_AVG_PT
        self.people = people()

    def _load_data(self) -> pd.DataFrame:
        raise NotImplementedError

    def filter_non_representative_data(self, stats_df: pd.DataFrame, primary_pos_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def preprocess_data(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def validate_data(self, stats_df: pd.DataFrame) -> None:
        missing_columns = []
        for required_column in self.REQUIRED_COLUMNS:
            if required_column not in stats_df.columns:
                missing_columns.append(required_column)
        if missing_columns:
            raise ValueError(
                "the following required columns are missing {}".format(missing_columns)
            )

    def compute_playing_time_projection(
        self,
        metric_values: np.ndarray,
        pt_values: np.ndarray,
        metric_weights: np.ndarray,
        pt_weights: np.ndarray,
        seasonal_averages: np.ndarray,
        num_regression_pt: Union[float, np.ndarray],
    ) -> np.ndarray:
        """
        computes playing time projection. `metric_values`, `metric_weights`, and
        `seasonal_averages` are not used but are included for consistency with
        `compute_rate_projection`

        :param metric_values:
        :param pt_values: playing time values
        :param metric_weights:
        :param pt_weights: playing time weights
        :param seasonal_averages:
        :param num_regression_pt: number of playing-time units to use for regression
        :return:
        """

        return np.sum(pt_values * pt_weights, 1) + num_regression_pt

    def compute_rate_projection(
        self,
        metric_values: np.ndarray,
        pt_values: np.ndarray,
        metric_weights: np.ndarray,
        pt_weights: np.ndarray,
        seasonal_averages: np.ndarray,
        num_regression_pt: float,
    ) -> np.ndarray:
        """
        computes rate projection. the length of the `x_values` and `x_weights`
        have to be the same. `pt_weights` is not used but is included for
        consistency with `compute_playing_time_projection`

        :param metric_values: float array
        :param pt_values: float array
        :param metric_weights: float array
        :param pt_weights:
        :param seasonal_averages: float array
        :param num_regression_pt: float
        :return:
        """
        pt_values[pt_values == 0] = sys.float_info.min
        normalized_metric_weights = np.array(metric_weights) / sum(metric_weights)
        unregressed_player_projection = np.sum(
            metric_values * normalized_metric_weights, 1
        )

        mean_rate_projection = np.sum(
            seasonal_averages * pt_values * normalized_metric_weights, 1
        ) / np.sum(pt_values * normalized_metric_weights, 1)

        projection_numerator = (
            unregressed_player_projection + num_regression_pt * mean_rate_projection
        )
        projection_denominator = (
            np.sum(pt_values * normalized_metric_weights, 1) + num_regression_pt
        )

        return projection_numerator / projection_denominator

    def metric_projection_detail(self, metric_name: str, projected_season: int) -> pd.DataFrame:
        """
        returns the projection result for `metric_name`, including the
        detailed components separately. The use case for the details
        is primarily debugging

        :param metric_name: str
        :param projected_season: int
        :return: data frame
        """

        assert self.PLAYING_TIME_COLUMN

        season = projected_season - 1
        playing_time_column = self.PLAYING_TIME_COLUMN

        stats_df = self.filter_non_representative_data(
            self.stats_df, self.primary_pos_df
        )
        num_regression_pt = self.get_num_regression_pt(
            stats_df.query(f"yearID == {season}")
        )

        seasonal_avg_df = (
            self.seasonal_average(stats_df, metric_name, playing_time_column=playing_time_column)
            .reset_index()
            .loc[:, ["yearID", "seasonal_avg"]]
        )

        stats_df = stats_df.loc[
            :, ["playerID", "yearID", playing_time_column, metric_name]
        ]
        stats_df_season = stats_df.query(f"yearID == {season}").loc[
            :, ["playerID", "yearID"]
        ]

        metric_df = pd.concat(
            [
                (
                    stats_df_season.merge(
                        stats_df.assign(
                            yearID=lambda row: row.yearID + prior_year_offset
                        ),
                        on=["playerID", "yearID"],
                        how="left",
                        suffixes=["_x", ""],
                    )
                    .set_index(["playerID", "yearID"])
                    .loc[:, metric_name]
                )
                for prior_year_offset, _ in enumerate(self.metric_weights)
            ],
            axis=1,
        ).fillna(0)

        pa_df = pd.concat(
            [
                (
                    stats_df_season.merge(
                        stats_df.assign(
                            yearID=lambda row: row.yearID + prior_year_offset
                        ),
                        on=["playerID", "yearID"],
                        how="left",
                        suffixes=["_x", ""],
                    )
                    .set_index(["playerID", "yearID"])
                    .loc[:, playing_time_column]
                )
                for prior_year_offset, _ in enumerate(self.metric_weights)
            ],
            axis=1,
        ).fillna(0)

        sa_df = (
            seasonal_avg_df.query(
                f"yearID >= {season - len(self.metric_weights)+1} "
                f"and yearID <= {season}"
            )
            .sort_values("yearID", ascending=False)
            .loc[:, "seasonal_avg"]
        )

        assert self.LEAGUE_AVG_PT

        rate_projection = self.compute_rate_projection(
            metric_df.values,
            pa_df.values,
            self.metric_weights,
            self.pt_weights,
            sa_df.values,
            num_regression_pt=self.LEAGUE_AVG_PT,
        )

        pt_projection = self.compute_playing_time_projection(
            metric_df.values,
            pa_df.values,
            self.metric_weights,
            self.pt_weights,
            sa_df.values,
            num_regression_pt=num_regression_pt,
        )

        age_df = get_age(stats_df_season, self.people)
        age_values = age_df.age + 1
        age_adjustment_value = age_values.apply(age_adjustment).values

        if metric_name in self.RECIPROCAL_AGE_METRICS:
            age_adjustment_value = 1 / age_adjustment_value

        weighted_average = np.sum(self.metric_weights * sa_df.values) / np.sum(
            self.metric_weights
        )
        weighted_value = np.sum(
            rate_projection * age_adjustment_value * pt_projection
        ) / np.sum(pt_projection)

        rebaseline_value = weighted_average / weighted_value

        return stats_df_season.assign(
            yearID=projected_season,
            age=age_values.values,
            rate_projection=rate_projection,
            pt_projection=pt_projection,
            age_adjustment_value=age_adjustment_value,
            rebaseline_value=rebaseline_value,
            weighted_average=weighted_average,
            weighted_value=weighted_value,
        ).set_index(["playerID", "yearID"])

    def metric_projection(self, metric_name: str, projected_season: int) -> pd.DataFrame:
        """
        returns the projection for `metric_name`.

        :param metric_name: str
        :param projected_season: int
        :return: data frame
        """
        x_df = self.metric_projection_detail(metric_name, projected_season)
        return (
            x_df.assign(
                x=lambda row: row.rate_projection
                * row.pt_projection
                * row.age_adjustment_value
                * row.rebaseline_value
            )
            .rename({"x": metric_name}, axis=1)
            .loc[:, [metric_name]]
        )

    def projections(self, projected_season: int, computed_metrics: List[str] = None) -> pd.DataFrame:
        """
        returns projections for all metrics in `computed_metrics`. If
        `computed_metrics` is None it uses the default set.

        :param projected_season: int
        :param computed_metrics: list(str)
        :return: data frame
        """
        computed_metrics = computed_metrics or self.COMPUTED_METRICS

        projections = [
            self.metric_projection(metric_name, projected_season)
            for metric_name in computed_metrics
        ]
        return pd.concat(projections, axis=1)

    def seasonal_average(self, stats_df: pd.DataFrame, metric_name: str, playing_time_column: str) -> pd.DataFrame:
        """
        seasonal average rate of `metric_name`

        :param stats_df: data frame
        :param metric_name: str
        :param playing_time_column: str
        :return: data frame
        """
        return (
            stats_df.groupby("yearID")
            .agg({metric_name: sum, playing_time_column: sum})
            .assign(
                seasonal_avg=lambda row: row[metric_name] / row[playing_time_column]
            )
        )

    def get_num_regression_pt(self, stats_df: pd.DataFrame) -> Union[float, np.ndarray]:
        """

        :param stats_df: data frame
        :return: float
        """

        assert self.NUM_REGRESSION_PLAYING_TIME

        return self.NUM_REGRESSION_PLAYING_TIME
