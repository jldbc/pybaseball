from typing import Callable

import lxml
import numpy as np
import pandas as pd
import pytest

from pybaseball.datasources.html_table_processor import HTMLTableProcessor
from pybaseball.datahelpers.column_mapper import GenericColumnMapper

@pytest.fixture()
def sample_html() -> str:
    return """
        <html>
        <head></head>
        <body>
            <table class="rgMasterTable">
                <thead>
                    <tr>
                        <th class="rgHeader">Team</th>
                        <th class="rgHeader">Runs</th>
                        <th class="rgHeader">Hits</th>
                        <th class="rgHeader">CS%</th>
                        <th class="rgHeader">HR</th>
                        <th class="rgHeader">Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>TBR</td>
                        <td>1.0</td>
                        <td>2</td>
                        <td>50 %</td>
                        <td>8</td>
                        <td>60</td>
                    </tr>
                    <tr>
                        <td>NYY</td>
                        <td>3.5</td>
                        <td>4</td>
                        <td>45%</td>
                        <td>Null</td>
                        <td>30</td>
                    </tr>
                </tbody>
            </table>
        </body>
    """


@pytest.fixture()
def sample_processed_result() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ['TBR', 1, 2, 0.50, 8, .6],
            ['NYY', 3.5, 4, 0.45, np.nan, .3]
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR', 'Percentage']
    ).reset_index(drop=True)

@pytest.fixture(name='html_table_processor')
def _html_table_processor() -> HTMLTableProcessor:
    root_url = 'https://127.0.0.1'
    headings_xpath = '{TABLE_XPATH}/thead//th[contains(@class, "rgHeader")]/descendant-or-self::*/text()'
    data_rows_xpath = '{TABLE_XPATH}/tbody//tr'
    data_cell_xpath = 'td/descendant-or-self::*/text()'
    table_class = 'rgMasterTable'
    return HTMLTableProcessor(root_url, headings_xpath, data_rows_xpath, data_cell_xpath, table_class)

class TestHTMLTableProcessor:
    def test_get_table_html(self, html_table_processor: HTMLTableProcessor, sample_html: str,
                            sample_processed_result: pd.DataFrame) -> None:
        actual_result = html_table_processor.get_tabular_data_from_html(
            sample_html,
            column_name_mapper=GenericColumnMapper().map_list,
            known_percentages=['Percentage']
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(sample_processed_result, actual_result, check_dtype=False)

    def test_get_table_element(self, html_table_processor: HTMLTableProcessor, sample_html: str,
                               sample_processed_result: pd.DataFrame) -> None:
        html_dom = lxml.etree.HTML(sample_html)
        actual_result = html_table_processor.get_tabular_data_from_element(
            html_dom,
            column_name_mapper=GenericColumnMapper().map_list,
            known_percentages=['Percentage']
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(sample_processed_result, actual_result, check_dtype=False)

    def test_get_table_url(self, html_table_processor: HTMLTableProcessor, sample_html: str, sample_processed_result: pd.DataFrame,
                           response_get_monkeypatch: Callable) -> None:
        response_get_monkeypatch(sample_html)
        actual_result = html_table_processor.get_tabular_data_from_url(
            '/test',
            column_name_mapper=GenericColumnMapper().map_list,
            known_percentages=['Percentage']
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(sample_processed_result, actual_result, check_dtype=False)

    def test_get_table_options(self, html_table_processor: HTMLTableProcessor, sample_html: str, sample_processed_result: pd.DataFrame,
                           response_get_monkeypatch: Callable) -> None:
        response_get_monkeypatch(sample_html)
        actual_result = html_table_processor.get_tabular_data_from_options(
            '/test',
            query_params={'a': 'b'},
            column_name_mapper=GenericColumnMapper().map_list,
            known_percentages=['Percentage']
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(sample_processed_result, actual_result, check_dtype=False)
