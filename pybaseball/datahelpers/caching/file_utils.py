import os
import pathlib
import shutil

# Splitting this out for testing with no side effects
def _mkdir(directory: str) -> None:
    return pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

# Splitting this out for testing with no side effects
def _remove(filename: str) -> None:
    return os.remove(filename)

# Splitting this out for testing with no side effects
def _rmtree(directory: str) -> None:
    return shutil.rmtree(directory)
