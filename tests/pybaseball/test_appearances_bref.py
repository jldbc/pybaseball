import unittest
from pybaseball.appearances_bref import appearances_bref

class TestAppearancesBref(unittest.TestCase):

    def test_wrong_season_error(self):
        # ensure error raised for season before 1871
        self.assertRaises(ValueError, appearances_bref, 1870)

    def test_year_with_no_awards(self):
        # make sure results are retrieved with no error for a year where the awards column is empty / excluded
        appearances_bref_result = appearances_bref(1871)

        # test specific value in results
        assert appearances_bref_result[appearances_bref_result["Player"] == "Dave Eggler"]["CF"].values[0] == "33"

    def test_year_with_awards(self):
        appearances_bref_result = appearances_bref(1913)

        # test awards column
        assert appearances_bref_result[appearances_bref_result["Player"] == "Walter Johnson"]["Awards"].values[0] == \
                "MVP-1"