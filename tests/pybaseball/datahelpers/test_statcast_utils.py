from pybaseball.datahelpers import statcast_utils
import pandas as pd
import pytest

@pytest.fixture(name='unprocessed_data')
def _unprocessed_data() -> pd.DataFrame:
    return pd.DataFrame([
        ['L', 139.98, 150.23],
        ['R', 23.86, 96.65]
    ],
    columns=['stand', 'hc_x', 'hc_y'])

def test_add_spray_angle(unprocessed_data: pd.DataFrame) -> None:
    spray_angle_df = statcast_utils.add_spray_angle(unprocessed_data)

    expected = pd.DataFrame([
        ['L', 139.98, 150.23, 12.6457],
        ['R', 23.86, 96.65, -33.7373]
    ],
    columns=['stand', 'hc_x', 'hc_y', 'spray_angle'])

    pd.testing.assert_frame_equal(spray_angle_df, expected)

def test_add_spray_angle_adjusted(unprocessed_data: pd.DataFrame) -> None:
    spray_angle_df = statcast_utils.add_spray_angle(unprocessed_data, adjusted=True)

    expected = pd.DataFrame([
        ['L', 139.98, 150.23, -12.6457],
        ['R', 23.86, 96.65, -33.7373]
    ],
    columns=['stand', 'hc_x', 'hc_y', 'adj_spray_angle'])

    pd.testing.assert_frame_equal(spray_angle_df, expected)

