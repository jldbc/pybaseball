
import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock
from typing import Generator
import pytest

from pybaseball import plotting


@pytest.fixture(autouse=True)
def before_after() -> Generator:
    # Before test runs
    importlib.reload(plotting)

    yield

    # After test runs
    importlib.reload(plotting)

    sys.modules['altair'] = None


@pytest.fixture(name="altair_mock")
def _altair_mock() -> ModuleType:
    altair = type(pytest)('altair')
    altair.Chart = MagicMock()
    altair.Color = MagicMock()
    altair.LayerChart = MagicMock()
    altair.Scale = MagicMock()
    altair.X = MagicMock()
    altair.Y = MagicMock()

    sys.modules['altair'] = altair

    importlib.reload(plotting)

    return altair


def test_altair_deprecated(altair_mock: ModuleType) -> None:
    with pytest.deprecated_call():
        assert plotting.spraychart == plotting.spraychart_altair
        assert plotting.plot_stadium == plotting.plot_stadium_altair

        plotting.plot_stadium('rays')


def test_pyplot_default(recwarn) -> None:
    assert plotting.spraychart == plotting.spraychart_pyplot
    assert plotting.plot_stadium == plotting.plot_stadium_pyplot

    plotting.plot_stadium('rays')

    assert len(recwarn) == 0
