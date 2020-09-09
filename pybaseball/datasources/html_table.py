from typing import Callable, Dict, List, Union

import lxml
import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing


class HTMLTable:
    def __init__(self, root_url: str, headings_xpath: str, data_rows_xpath: str, data_cell_xpath: str):
        self.root_url = root_url
        self.headings_xpath = headings_xpath
        self.data_rows_xpath = data_rows_xpath
        self.data_cell_xpath = data_cell_xpath

    def _create_url(self, url_base: str, query_string_params: Dict[str, Union[str, int]] = {}):
        query_string = ''

        if query_string_params and isinstance(query_string_params, dict):
            query_string = "?" + "&".join([f"{key}={value}" for key, value in query_string_params.items()])

        return url_base + query_string

    def get_tabular_data_from_html(self, html: Union[str, bytes], column_name_mapper: Callable = None, known_percentages: List[str] = []) -> pd.DataFrame:
        html_dom = lxml.etree.HTML(html)

        headings = html_dom.xpath(self.headings_xpath)

        if column_name_mapper:
            headings = [column_name_mapper(h) for h in headings]

        data_rows_dom = html_dom.xpath(self.data_rows_xpath)
        data_rows = [
            [
                postprocessing.try_parse(y, headings[index], known_percentages=known_percentages)
                for index, y in enumerate(x.xpath(self.data_cell_xpath))
            ]
            for x in data_rows_dom
        ]

        fg_data = pd.DataFrame(data_rows, columns=headings)

        return fg_data


    def get_tabular_data_from_url(self, url: str, column_name_mapper: Callable = None,
                                known_percentages: List[str] = []) -> pd.DataFrame:
        response = requests.get(self.root_url + url)

        if response.status_code > 399:
            raise requests.exceptions.HTTPError(f"Error accessing '{self.root_url + url}'. Received status code {response.status_code}")

        return self.get_tabular_data_from_html(
            response.content,
            column_name_mapper=column_name_mapper,
            known_percentages=known_percentages
        )
