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

@pytest.fixture(name='unprocessed_vaa_data')
def _unprocessed_vaa_data() -> pd.DataFrame:
    return pd.DataFrame([
        [-5.045042, -136.632241, -14.79299, 11.115757, 29.865813, -9.074346],
        [4.235708, -131.933251, 3.388941, -5.795787, 30.314587, -16.130632]
    ],
    columns=['vx0', 'vy0', 'vz0', 'ax', 'ay', 'az'])

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

def test_add_vertical_approach_angle(unprocessed_vaa_data: pd.DataFrame) -> None:
    vaa_df = statcast_utils.add_vertical_approach_angle(unprocessed_vaa_data)

    expected = pd.DataFrame([
        [-5.045042, -136.632241, -14.79299, 11.115757, 29.865813, -9.074346, -8.227591],
        [4.235708, -131.933251, 3.388941, -5.795787, 30.314587, -16.130632, -1.346296],
    ],
    columns=['vx0', 'vy0', 'vz0', 'ax', 'ay', 'az','vaa'])

    pd.testing.assert_frame_equal(vaa_df, expected)