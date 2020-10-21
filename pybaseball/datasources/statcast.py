import io
import os
from datetime import datetime
from typing import List, Union

import numpy as np
import pandas as pd
import requests

from .. import cache
from ..datahelpers import postprocessing

ROOT_URL = 'https://baseballsavant.mlb.com'


@cache.df_cache()
def get_statcast_data_from_csv_url(
    url: str,
    null_replacement: Union[str, int, float, datetime] = np.nan,
    known_percentages: List[str] = []
) -> pd.DataFrame:
    statcast_content = requests.get(ROOT_URL + url, timeout=None).content
    return get_statcast_data_from_csv(
        statcast_content.decode('utf-8'),
        null_replacement=null_replacement,
        known_percentages=known_percentages
    )


def get_statcast_data_from_csv(
        csv_content: str,
        null_replacement: Union[str, int, float, datetime] = np.nan,
        known_percentages: List[str] = []
    ) -> pd.DataFrame:
    data = pd.read_csv(io.StringIO(csv_content))
    return postprocessing.try_parse_dataframe(
        data,
        parse_numerics=False,
        null_replacement=null_replacement,
        known_percentages=known_percentages
    )
