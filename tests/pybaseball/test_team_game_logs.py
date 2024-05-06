import pandas as pd
from pybaseball.team_game_logs import team_game_logs
import pytest


@pytest.fixture(name="sample_processed_result")
def sample_processed_result() -> pd.DataFrame:
    return pd.read_csv('team_gamelogs.csv')


def test_team_game_logs(sample_processed_result):
    test_output = team_game_logs(2024, "BAL", "batting")
    test_output.reset_index(drop=True, inplace=True)
    test_output_first_five = test_output.head(5)
    pd.testing.assert_frame_equal(test_output_first_five, sample_processed_result, check_dtype=False)
