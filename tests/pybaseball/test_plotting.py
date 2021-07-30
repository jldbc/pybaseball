import pytest
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from pybaseball.plotting import transform_coordinates


@pytest.fixture
def coords():
    return pd.DataFrame({"x": [1.0, 2.0, -1.0], "y": [1.0, 0.0, 10.0]})


def test_transform_coordinates_identity_scale(coords):
    transformed_coords = transform_coordinates(coords, scale=1)
    assert_series_equal(coords.x, transformed_coords.x)
    assert_series_equal(-coords.y, transformed_coords.y)



def test_transform_coordinates(coords):
    transformed_coords = transform_coordinates(coords, scale=2, x_center=0, y_center=0)
    assert_series_equal(2 * coords.x, transformed_coords.x)
    assert_series_equal(-2 * coords.y, transformed_coords.y)

    transformed_coords = transform_coordinates(coords, scale=2, x_center=1, y_center=1)
    expected = pd.DataFrame({"x": [1.0, 3.0, -3.0], "y": [-1.0, 1.0, -19.0]})
    assert_frame_equal(expected, transformed_coords)

    xc = 123.4
    yc = 432.1
    transformed_coords = transform_coordinates(coords, scale=0, x_center=xc, y_center=yc)
    assert_series_equal(pd.Series(name="x", data=3 * [xc]), transformed_coords.x)
    assert_series_equal(pd.Series(name="y", data=3 * [yc]), -transformed_coords.y)
