
import pandas as pd

from pybaseball.lahman import people


def get_age(stats_df: pd.DataFrame, people_df: pd.DataFrame = None) -> pd.DataFrame:
    if people_df is None:
        people_df = people()
    return (
        stats_df.merge(
            people_df.filter(["playerID", "birthYear"], axis=1), on="playerID"
        )
        .assign(age=lambda row: (row.yearID - row.birthYear).astype(pd.Int32Dtype()))
        .filter(["playerID", "yearID", "age"], axis=1)
    )


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
