import lxml
from typing import List

import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing

ROOT_URL = 'https://www.fangraphs.com'


def get_fangraphs_tabular_data_from_html(html: str, xpath: str, percentage_columns: List[str] = None, non_numeric_columns: List[str] = None) -> pd.DataFrame:
    html_dom = lxml.etree.HTML(html)

    headings_xpath = f"({xpath}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
    headings = html_dom.xpath(headings_xpath)

    data_rows_xpath = f"({xpath}/tbody//tr)"
    data_rows_dom = html_dom.xpath(data_rows_xpath)
    data_rows = [
        [y.strip() for y in x.xpath('td[position()>1]/descendant-or-self::*/text()')] for x in data_rows_dom
    ]

    fg_data = pd.DataFrame(data_rows, columns=headings)

    postprocessing.coalesce_nulls(fg_data)

    if percentage_columns:
        postprocessing.convert_percentages(fg_data, percentage_columns)

    if non_numeric_columns:
        postprocessing.convert_numeric(
            fg_data,
            postprocessing.columns_except(
                fg_data,
                non_numeric_columns
            )
        )
    else:
        postprocessing.convert_numeric(fg_data, fg_data.columns)

    return fg_data


def get_fangraphs_tabular_data_from_url(url: str, xpath: str, percentage_columns: List[str] = None, non_numeric_columns: List[str] = None) -> pd.DataFrame:
    content = requests.get(ROOT_URL + url).content

    return get_fangraphs_tabular_data_from_html(content, xpath, percentage_columns, non_numeric_columns)
