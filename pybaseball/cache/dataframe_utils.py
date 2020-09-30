import pandas as pd

def load_df(filename: str) -> pd.DataFrame:
    if filename.endswith('csv'):
        data = pd.read_csv(filename)
    elif filename.endswith('parquet'):
        data = pd.read_parquet(filename)
    else:
        raise ValueError(f"Cache frame {filename} has an unsupported extension.")
    data.drop(
        data.columns[data.columns.str.contains('unnamed', case=False)],
        axis=1,
        inplace=True
    )
    return data

def save_df(data: pd.DataFrame, filename: str) -> None:
    if filename.endswith('csv'):
        data.to_csv(filename)
    elif filename.endswith('parquet'):
        data.to_parquet(filename)
    else:
        raise ValueError(f"DataFrame {filename} is an unsupported type")
