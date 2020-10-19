import sys
import time
from pybaseball import statcast

EXPECTED_TIME_THRESHOLD = 30
START_DATE = "2018-08-01"
END_DATE = "2018-08-10"

def main():
    if len(sys.argv) == 2:
        time_threshold = float(sys.argv[1])
    else:
        time_threshold = EXPECTED_TIME_THRESHOLD

    start_time = time.time()
    _ = statcast(START_DATE, END_DATE)
    end_time = time.time()
    query_time = end_time-start_time
    diagnostic_messages = f"query took {query_time: .1f} seconds which is", f"threshold of {time_threshold: .1f}\n"
    if query_time > time_threshold:
        sys.stderr.write("{0} greater than {1}".format(*diagnostic_messages))
        sys.exit(1)
    else:
        sys.stdout.write("{0} less than {1}".format(*diagnostic_messages))

if __name__=='__main__':
    main()
