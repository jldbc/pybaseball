from typing import Callable, List, Union

import lxml
import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing

ROOT_URL = 'https://www.fangraphs.com'


def get_fangraphs_tabular_data_from_html(html: Union[str, bytes], column_name_mapper: Callable = None, known_percentages: List[str] = []) -> pd.DataFrame:
    xpath: str = '//table[@class="rgMasterTable"]'
    html_dom = lxml.etree.HTML(html)

    headings_xpath = f"({xpath}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
    headings = html_dom.xpath(headings_xpath)

    if column_name_mapper:
        headings = [column_name_mapper(h) for h in headings]

    data_rows_xpath = f"({xpath}/tbody//tr)"
    data_rows_dom = html_dom.xpath(data_rows_xpath)
    data_rows = [
        [
            postprocessing.try_parse(y, headings[index], known_percentages=known_percentages)
            for index, y in enumerate(x.xpath('td[position()>1]/descendant-or-self::*/text()'))
        ]
        for x in data_rows_dom
    ]

    fg_data = pd.DataFrame(data_rows, columns=headings)

    return fg_data


def get_fangraphs_tabular_data_from_url(url: str, column_name_mapper: Callable = None, known_percentages: List[str] = []) -> pd.DataFrame:
    content = requests.get(ROOT_URL + url).content

    return get_fangraphs_tabular_data_from_html(
        content,
        column_name_mapper=column_name_mapper,
        known_percentages=known_percentages
    )
