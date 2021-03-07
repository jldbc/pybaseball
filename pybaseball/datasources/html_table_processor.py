from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import lxml.etree
import pandas as pd
import requests

from ..datahelpers import postprocessing
from ..datahelpers.column_mapper import ColumnListMapperFunction

RowIdFunction = Optional[Callable[[Any, lxml.etree.Element], Optional[Union[int, str]]]]

class HTMLTableProcessor:
    def __init__(self, root_url: str, headings_xpath: str, data_rows_xpath: str, data_cell_xpath: str,
                 table_class: str = None):
        self.root_url = root_url
        self.table_class = table_class
        self.headings_xpath = headings_xpath.format(TABLE_XPATH=self.table_xpath)
        self.data_rows_xpath = data_rows_xpath.format(TABLE_XPATH=self.table_xpath)
        self.data_cell_xpath = data_cell_xpath

    @property
    def table_xpath(self) -> str:
        if self.table_class:
            return f'//table[@class="{self.table_class}"]'
        return '//table'

    def get_tabular_data_from_element(self, element: lxml.etree.Element, column_name_mapper: ColumnListMapperFunction = None,
                                      known_percentages: Optional[List[str]] = None, row_id_func: RowIdFunction = None,
                                      row_id_name: Optional[str] = None) -> pd.DataFrame:
        headings = element.xpath(self.headings_xpath)

        if column_name_mapper:
            headings = list(column_name_mapper(headings))

        data_rows_dom = element.xpath(self.data_rows_xpath)
        data_rows: List[List[Union[str, int, float, datetime]]] = [
            [
                postprocessing.try_parse(y, headings[index], known_percentages=known_percentages)
                for index, y in enumerate(x.xpath(self.data_cell_xpath))
            ]
            for x in data_rows_dom
        ]

        if row_id_func:
            headings = [row_id_name or 'id'] + headings
            for index in range(len(data_rows_dom)):
                data_rows[index].insert(0, row_id_func(data_rows_dom[index])) # type: ignore

        fg_data = pd.DataFrame(data_rows, columns=headings)

        return fg_data

    def get_tabular_data_from_html(self, html: Union[str, bytes], column_name_mapper: ColumnListMapperFunction = None,
                                   known_percentages: Optional[List[str]] = None, row_id_func: RowIdFunction = None,
                                      row_id_name: Optional[str] = None) -> pd.DataFrame:
        html_dom = lxml.etree.HTML(html)

        return self.get_tabular_data_from_element(
            html_dom,
            column_name_mapper=column_name_mapper,
            known_percentages=known_percentages,
            row_id_func=row_id_func,
            row_id_name=row_id_name,
        )

    def get_tabular_data_from_url(self, url: str, query_params: Dict[str, Union[str, int]] = None,
                                  column_name_mapper: ColumnListMapperFunction = None,
                                  known_percentages: Optional[List[str]] = None, row_id_func: RowIdFunction = None,
                                      row_id_name: Optional[str] = None) -> pd.DataFrame:
        response = requests.get(self.root_url + url, params=query_params)

        if response.status_code > 399:
            raise requests.exceptions.HTTPError(
                f"Error accessing '{self.root_url + url}'. Received status code {response.status_code}"
            )

        return self.get_tabular_data_from_html(
            response.content,
            column_name_mapper=column_name_mapper,
            known_percentages=known_percentages,
            row_id_func=row_id_func,
            row_id_name=row_id_name,
        )

    def get_tabular_data_from_options(self, base_url: str, query_params: Dict[str, Union[str, int]],
                                      column_name_mapper: ColumnListMapperFunction = None,
                                      known_percentages: Optional[List[str]] = None, row_id_func: RowIdFunction = None,
                                      row_id_name: Optional[str] = None) -> pd.DataFrame:
        return self.get_tabular_data_from_url(
            base_url,
            query_params=query_params,
            column_name_mapper=column_name_mapper,
            known_percentages=known_percentages,
            row_id_func=row_id_func,
            row_id_name=row_id_name,
        )
