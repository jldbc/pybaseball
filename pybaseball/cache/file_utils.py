import os
import pathlib
import shutil
from typing import Dict
import json

import pandas as pd

# Splitting this out for testing with no side effects
def _mkdir(directory: str) -> None:
    return pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

# Splitting this out for testing with no side effects
def _remove(filename: str) -> None:
    return os.remove(filename)

# Splitting this out for testing with no side effects
def _rmtree(directory: str) -> None:
    return shutil.rmtree(directory)

def safe_jsonify(directory: str, filename: str, data: Dict) -> None:
    _mkdir(directory)
    fname = os.path.join(directory, filename)
    with open (fname, 'w') as f:
        json.dump(data, f)

def load_json(filename: str) -> Dict:
    with open(filename) as f:
        data = json.load(f)
    return data
