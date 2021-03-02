from unittest.mock import MagicMock, patch

import pandas as pd

from pybaseball.teamid_lookup import _DATA_FILENAME, _generate_teams


def test_generate_fangraphs_teams() -> None:
    with patch.object(pd.DataFrame, 'to_csv', MagicMock()) as to_csv_mock:
        result = _generate_teams()

        assert result is not None
        assert not result.empty

        # Remove newer results to ensure we get the count right
        result = result.query('yearID <= 2019')

        assert len(result.columns) == 7
        assert len(result) == 2925

        to_csv_mock.assert_called_once_with(_DATA_FILENAME)
