import argparse
import sys
import time
from pybaseball import statcast

DEFAULT_TIME_THRESHOLD = 30
DEFAULT_START_DATE = "2018-08-01"
DEFAULT_END_DATE = "2018-08-10"


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=False, default=DEFAULT_START_DATE)
    parser.add_argument("--end-date", required=False, default=DEFAULT_END_DATE)
    parser.add_argument("--time-threshold", "-t", required=False, type=float, default=DEFAULT_TIME_THRESHOLD)
    return parser.parse_args()


def main():
    args = _parse_args()
    start_time = time.time()
    _ = statcast(args.start_date, args.end_date)
    end_time = time.time()
    query_time = end_time-start_time
    threshold_exceeded = query_time > args.time_threshold
    print(f"query took {query_time: .1f} seconds (expected less than {args.time_threshold: .1f})")
    sys.exit(int(threshold_exceeded))

if __name__=='__main__':
    main()
