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

        to_csv_mock.assert_called_once_with(_DATA_FILENAME)

        # Each franchID should match one and only one teamIDfg
        for franch_id in set(result['franchID'].values):
            teams = result.query(f"franchID == '{franch_id}'")
            franchises = teams.groupby("teamIDfg").size()
            if len(franchises.index) > 1:
                # Print it out so we know who the offender is
                print('franch_id', franch_id)
                print('franchises', franchises)
                print(teams)
            
            assert len(franchises.index) == 1
