import warnings
from typing import Optional

import pandas as pd

from .datasources.fangraphs import fg_batting_data


# This is just a pass through for the new, more configurable function
batting_stats = fg_batting_data 
