import warnings
from typing import Optional

import pandas as pd

from .datasources.fangraphs import fg_pitching_data


# This is just a pass through for the new, more configurable function
pitching_stats = fg_pitching_data
