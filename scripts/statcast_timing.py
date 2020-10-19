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
    if query_time > time_threshold:
        sys.stderr.write("query took {:.2f} seconds "
                         "which is greater than threshold of {:.2f}".format(query_time, time_threshold)
                         )
        sys.exit(1)
    else:
        sys.stdout.write("query took {:.2f} seconds "
                         "which is less than threshold of {:.2f}".format(query_time, time_threshold)
                         )

if __name__=='__main__':
    main()
