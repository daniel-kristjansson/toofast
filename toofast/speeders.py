#!/usr/bin/python
"""
This program assumes a directory of CSV files with a peculiar format.

The format of the files is a set of lines called a header containing
lines like this:
,,,,,,,,,,,
,Name[s],Daniel K & Julie T,,,,,,,,,
,Date,8/10/2015,,,,,,,,,
,Location,Rogers Ave & Midwood St,,,,,,,,,
,Direction,North,,,,,,,,,
,Weather,Sunny,,,,,,,,,
,Speed Limit,25,,,,,,,,,
,,,,,,,,,,,

This header if followed by lines containing data which look like this:
,Vehicle,Time,Speed,,Vehicle,Time,Speed,,Vehicle,Time,Speed
,1,6:56,44,,1,7:16,38,,1,7:31,31
,,,,,,,,,,,
,Vehicle,Time,Speed,,Vehicle,Time,Speed,,Vehicle,Time,Speed
,1,7:49,25,,1,8:05,29,,1,8:22,30

This peculiar format comes from a sheet which is optimized for human input,
not for ease of parsing.

The job of this program to take this data and compute various statistics which
are useful to show whether or not there is speeding on a particular road.

The program groups the data into 15 minute intervals and then computes
statistics on that data.
"""
import logging
import datetime
import sys
from parse_input import read_data_directory
from output_statistics import output_csv
from analyse_data import (
    bucket_data, compute_statistics, group_statistics)

def main():
    '''Reads a directory of speed data and outputs relevant statistics'''
    logging.getLogger('').setLevel(logging.DEBUG)

    data = read_data_directory("sample_data")
    buckets = bucket_data(
        data, datetime.timedelta(minutes=15).seconds, ignore_date=True)
    stats = compute_statistics(buckets)
    grouped_stats = group_statistics(stats)
    output_csv(sys.stdout, grouped_stats)

if __name__ == "__main__":
    main()
