import lxml.etree
import requests

from pybaseball.enums.fangraphs.fielding_data_enum import FangraphsFieldingStats
from tests.integration.pybaseball.enums.fangraphs.transforms import transform_leaderboard_item


def test_enums_vs_fangraphs_column_list() -> None:
    """
        Go and get all the supported columns out of Fangraphs' "Custom Query" column selector. Compare this list
        to our enum of supported columns and ensure we've covered them 100%.
    """

    sample_pitching_url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=fld&type=c,3&lg=all&qual=y&type=8&season=2020&month=0&season1=2020&ind=0"
    sample_pitching_result = requests.get(sample_pitching_url)

    parsed_result = lxml.etree.HTML(sample_pitching_result.content.decode('utf-8'))

    custom_leaderboards_items = sorted(
        list({x for x in parsed_result.xpath('//ul[@class="rlbList"]/li[@class="rlbItem"]/text()')
              if x != 'Line Break'})
    )

    custom_leaderboards_items = sorted([transform_leaderboard_item(x) for x in custom_leaderboards_items])

    current_leaderboard_items = sorted(
        [str(x).split('.')[1] for x in FangraphsFieldingStats.ALL()
         if x not in [FangraphsFieldingStats.COMMON, FangraphsFieldingStats.LINE_BREAK]] + [FangraphsFieldingStats.POS.name]
    )

    assert custom_leaderboards_items == current_leaderboard_items
