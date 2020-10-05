import pandas as pd
import pytest

from pybaseball.datasources.fangraphs import fg_pitching_data


class TestFGPitchingData:
    ALL_DATA_COLUMNS_COUNT = 330
    DEFAULT_MAX_RESULTS = 10

    def test_fg_pitching_data(self) -> None:
        season = 2019

        data = fg_pitching_data(season, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == self.DEFAULT_MAX_RESULTS
        
        seasons = list(set(data['Season']))

        assert len(seasons) == 1
        assert seasons[0] == season

    def test_fg_pitching_data_future_season(self) -> None:
        season = 3000

        with pytest.raises(ValueError):
            fg_pitching_data(season, max_results=self.DEFAULT_MAX_RESULTS)

    def test_fg_pitching_data_end_season(self) -> None:
        data = fg_pitching_data(2018, end_season=2019, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == self.DEFAULT_MAX_RESULTS

    def test_fg_pitching_data_end_season_no_split_season(self) -> None:
        data = fg_pitching_data(2018, end_season=2019, split_seasons=False, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT - 1
        assert 'Season' not in data.columns
        assert len(data.index) == self.DEFAULT_MAX_RESULTS

    def test_fg_pitching_data_single_stat_columns(self) -> None:
        data = fg_pitching_data(2019, stat_columns='ERA', max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == 5
        assert len(data.index) == self.DEFAULT_MAX_RESULTS

    def test_fg_pitching_data_multiple_stat_columns(self) -> None:
        data = fg_pitching_data(2019, stat_columns=['ERA', 'BB'], max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == 6
        assert len(data.index) == self.DEFAULT_MAX_RESULTS

    def test_fg_pitching_data_league(self, assert_frame_not_equal) -> None:
        data_al = fg_pitching_data(2019, league='AL', max_results=self.DEFAULT_MAX_RESULTS)

        assert data_al is not None
        assert not data_al.empty
        assert len(data_al.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data_al.index) == self.DEFAULT_MAX_RESULTS
        
        data_nl = fg_pitching_data(2019, league='NL', max_results=self.DEFAULT_MAX_RESULTS)

        assert data_nl is not None
        assert not data_nl.empty
        assert len(data_nl.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data_nl.index) == self.DEFAULT_MAX_RESULTS

        assert assert_frame_not_equal(data_al, data_nl)

    def test_fg_pitching_data_qual(self) -> None:
        data = fg_pitching_data(2019, qual=210, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == 4

    def test_fg_pitching_data_on_active_roster(self, assert_frame_not_equal) -> None:
        data = fg_pitching_data(2018, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == self.DEFAULT_MAX_RESULTS
        
        oar_data = fg_pitching_data(2018, on_active_roster=True, max_results=self.DEFAULT_MAX_RESULTS)

        assert oar_data is not None
        assert not oar_data.empty
        assert len(oar_data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(oar_data.index) == self.DEFAULT_MAX_RESULTS

        assert_frame_not_equal(data, oar_data)

    def test_fg_pitching_minimum_age(self) -> None:
        data = fg_pitching_data(2019, minimum_age=37, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == 1

    def test_fg_pitching_maximum_age(self) -> None:
        data = fg_pitching_data(2019, maximum_age=21, max_results=self.DEFAULT_MAX_RESULTS)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == 1

    def test_fg_pitching_team(self, assert_frame_not_equal) -> None:
        data_1 = fg_pitching_data(2019, team='3', max_results=self.DEFAULT_MAX_RESULTS)

        assert data_1 is not None
        assert not data_1.empty
        assert len(data_1.columns) == self.ALL_DATA_COLUMNS_COUNT - 1
        assert 'Team' not in data_1.columns
        assert len(data_1.index) == 2
        
        data_2 = fg_pitching_data(2019, team='4', max_results=self.DEFAULT_MAX_RESULTS)

        assert data_2 is not None
        assert not data_2.empty
        assert len(data_2.columns) == self.ALL_DATA_COLUMNS_COUNT - 1
        assert 'Team' not in data_2.columns
        assert len(data_2.index) == 3

        assert_frame_not_equal(data_1, data_2)
    
    def test_fg_pitching_data_max_results(self) -> None:
        season = 2019

        data = fg_pitching_data(season)

        assert data is not None
        assert not data.empty
        assert len(data.columns) == self.ALL_DATA_COLUMNS_COUNT
        assert len(data.index) == 61
