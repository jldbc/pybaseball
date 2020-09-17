from pybaseball.datahelpers.column_mapper import BattingStatsColumnMapper, GenericColumnMapper


class TestGenericColumnWrapper:
    def test_generic_column_mapper(self):
        mapper = GenericColumnMapper()

        assert mapper.map('FB%') == 'FB%'

        assert mapper.map('HR') == 'HR'

        assert mapper.map('FB%') == 'FB% 2'

        assert mapper.map('HR') == 'HR 2'

class TestBattingStatsColumnWrapper:
    def test_batting_stats_column_mapper(self):
        mapper = BattingStatsColumnMapper()

        assert mapper.map('FB%') == 'FB%'

        assert mapper.map('HR') == 'HR'

        assert mapper.map('FB%') == 'FB% (Pitch)'

        assert mapper.map('HR') == 'HR 2'
