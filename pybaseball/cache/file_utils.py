import json
import os
import pathlib
import shutil
from typing import Any, Dict, List, Union, cast

import pandas as pd

JSONData = Union[List[Any], Dict[str, Any]]


# Splitting this out for testing with no side effects
def mkdir(directory: str) -> None:
    return pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


# Splitting this out for testing with no side effects
def remove(filename: str) -> None:
    return os.remove(filename)


def safe_jsonify(directory: str, filename: str, data: JSONData) -> None:
    mkdir(directory)
    fname = os.path.join(directory, filename)
    with open(fname, 'w') as f:
        json.dump(data, f)


def load_json(filename: str) -> JSONData:
    with open(filename) as f:
        return cast(JSONData, json.load(f))
