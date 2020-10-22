import argparse
import os
from datetime import date
import multiprocessing
import pandas as pd
from pybaseball.utils import date_range
from pybaseball import statcast

NUM_THREADS = 8
RESULTS_FILE = "statcast_dates.csv"


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-year", default=2008, required=False, type=int)
    parser.add_argument("--max-year", default=2020, required=False, type=int)
    return parser.parse_args()


def initialize_file():
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w") as fh:
            fh.write("date,num_records\n")


def get_records_count(date_str):
    print("doing", date_str)
    df = statcast(date_str, date_str)
    return date_str, len(df)


def get_dates(min_year, max_year):
    lo = date(min_year, 3, 1)
    hi = date(max_year, 11, 10)

    def date_to_str(d):
        return d[0].strftime("%Y-%m-%d")

    dates = [
        date_to_str(d)
        for d in date_range(lo, hi, 1)
        if date_to_str(d) not in already_done
    ]
    return dates


def get_date_records(dates):
    with multiprocessing.Pool(NUM_THREADS) as mp:
        res = mp.map(get_records_count, dates)
    return res


def update_date_records(date_records):
    res_df = pd.DataFrame(date_records).rename({0: "date", 1: "num_records"}, axis=1)
    return pd.concat((cache, res_df), axis=0)


def save_records(records):
    records.to_csv(RESULTS_FILE, index=False)


def get_rolling_counts(df, lag):
    return pd.concat(
        (df, df.rolling(lag).sum().rename({"num_records": "rolling_counts"}, axis=1)),
        axis=1,
    )


def analyze_records(records):
    """
    Computes max number of records for rolling window from 1 to 7
    returns a dictionary with key=season, values=min and max valid date
    """
    max_window = 7
    for lag in range(1, max_window + 1):
        ana_df = (
            get_rolling_counts(records, lag)
            .sort_values("rolling_counts", ascending=False)
            .assign(lag=lag)
        )
        print(ana_df.head(1))

    records = records.assign(year=lambda row: pd.to_datetime(row.date).dt.year)
    result = (
        records.query("num_records > 0").groupby("year").agg({"date": ["min", "max"]})
    )
    result.columns = ["min_valid_date", "max_valid_date"]
    return result


def main():
    args = _parse_args()
    dates = get_dates(args.min_year, args.max_year)
    date_records = get_date_records(dates)
    date_records = update_date_records(date_records)
    save_records(date_records)
    valid_dates = analyze_records(date_records)
    valid_dates.to_json("statcast_valid_dates.json", orient="index")
    print(valid_dates)


if __name__ == "__main__":
    initialize_file()
    cache = pd.read_csv(RESULTS_FILE)
    already_done = set(cache.date)
    main()
