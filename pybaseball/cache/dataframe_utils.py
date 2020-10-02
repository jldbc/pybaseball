import pandas as pd


def load_df(filename: str) -> pd.DataFrame:
    if filename.lower().endswith('csv'):
        data = pd.read_csv(filename, index_col=0)
    elif filename.lower().endswith('parquet'):
        data = pd.read_parquet(filename)
    else:
        raise ValueError(f"Cache frame {filename} has an unsupported extension.")
    return data


def save_df(data: pd.DataFrame, filename: str) -> None:
    if filename.lower().endswith('csv'):
        data.to_csv(filename)
    elif filename.lower().endswith('parquet'):
        data.to_parquet(filename)
    else:
        raise ValueError(f"DataFrame {filename} is an unsupported type")
