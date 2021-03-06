#!/usr/bin/env python
"""
Imports speed study data and outputs a report based on that data.

Usage:
    speeders.py [--debug] INPUT_DIRECTORY [--interval=INTERVAL] [--detail] [--min-count=MIN]
    speeders.py (-h | --help)

Options:
    -h --help            Show this screen
    --debug              Log in debug level
    --interval=INTERVAL  Sampling interval in minutes [default: 15]
    --min-count=MIN      Minumum number of data points to require before we compute statistics [default: 0]
    --detail             Request speed detail report instead of aggregate statistics

The default statistics report is broken down into interval spaced time periods
and data from all days in the input data is combined inteligently to produce
the report.

If you request a detailed report a breakdown of speeds recorded for each time period
is produced instead of the default statistics report report.

Output is in the form of a CSV file sent to the standard output.
"""
import logging
import datetime
import sys
from docopt import docopt
from toofast.parse_input import read_data_directory
from toofast.output_statistics import output_csv
from toofast.analyse_data import (
    bucket_data, compute_statistics, group_statistics, filter_statistics, count_speeds)


def init_logging(level):
    '''Initialize logging'''
    logging.getLogger('').setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)


def main():
    '''Reads a directory of speed data and outputs relevant statistics'''
    args = docopt(__doc__)
    init_logging(logging.DEBUG if args["--debug"] else logging.INFO)

    logging.debug("reading in data")
    data = read_data_directory(args["INPUT_DIRECTORY"])

    logging.debug("bucketing data")
    delta = datetime.timedelta(minutes=int(args["--interval"] or 15)).seconds
    buckets = bucket_data(data, delta)

    logging.debug("computing statistics")
    stats = compute_statistics(buckets)
    logging.debug("grouping statistics")
    grouped_stats = group_statistics(stats)
    logging.debug("filtering statistics")
    final_stats = filter_statistics(grouped_stats, min_count=int(args.get("--min-count") or 0))

    if args["--detail"]:
        final_stats = {key: count_speeds(stats["_speeds"])
                       for key, stats in final_stats.iteritems()}

    logging.debug("outputing statistics")
    output_csv(sys.stdout, final_stats)
    logging.debug("done")


if __name__ == "__main__":
    main()
