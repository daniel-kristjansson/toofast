#!/usr/bin/python
"""
This program assumes a directory of CSV files with a peculiar format.

The format of the files is a set of lines called a header containing lines like this:
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

This peculiar format comes from a sheet which is optimized for human input, not
for ease of parsing.

The job of this program to take this data and compute various statistics which are
useful to show whether or not there is speeding on a particular road.

The program groups the data into 15 minute intervals and then computes statistics on
that data.
"""
import logging
import csv
import time
import datetime
import os
import sys
import timestring

# Headers for each CSV. Metadata about a particular set of times and location for a speed study.
FILE_HEADERS = ["name", "date", "location", "direction", "weather", "speed limit"]
# Headers for each vehicle column
VEHICLE_HEADERS = ['vehicle', 'time', 'speed']
# To avoid data entry errors spoiling our data, we filter out very slow or very fast vehicle data
MINIMUM_SPEED = 10
MAXIMUM_SPEED = 99

def extract_file_header(row):
    '''
    Extracts a single header line from our wacky CSV file format.

    This matches anything of the form: ^[,*]('name'|'date'|etc)[.*],(.*)[,*]$

    Where the first capture is any of the valid file headers and the second capture is
    the value that follows. This uses a CSV parser so CSV quoting is allowed even though
    not reflected in the psudo regular expression above. This is also not case sensitive.

    A dictionary containing the key and the extracted value is returned, or an empty
    dictionary if no matching key is found.

    '''
    for header in FILE_HEADERS:
        for idx in xrange(len(row)):
            if row[idx] and header == row[idx][0:len(header)].lower():
                return {header: row[idx+1]}
    return {}

def read_file_header(filename, csv_reader):
    '''
    Returns all the file headers in FILE_HEADER + the filename as dictionary entries

    An exception is raised if all file headers are not found.
    '''
    header_data = {}
    for row in csv_reader:
        header_data.update(extract_file_header(row))
        if len(header_data) == len(FILE_HEADERS):
            header_data["filename"] = filename
            return header_data
    raise Exception("Unable to parse header for file {}".format(filename))

def is_null_vehicle(cur):
    '''Returns True if and only if we've seen a header or a empty vehicle entry'''
    for key, value in cur.iteritems():
        if not value or value.lower() == key:
            return True
    return False

def is_valid_vehicle(cur):
    '''Returns True if and only if we should treat this as a valid entry'''
    if is_null_vehicle(cur):
        return False
    if not cur.get("vehicle", "not integer").isdigit():
        return False
    if not cur.get("speed", "not integer").isdigit():
        return False
    if float(cur.get("speed")) < MINIMUM_SPEED or float(cur.get("speed")) > MAXIMUM_SPEED:
        return False
    return True

def extract_data_row(file_header, header_info, row, line_num):
    VEHICLE_HEADERS = ['vehicle', 'time', 'speed']
    data = []
    cur = {}
    for idx in xrange(len(row)):
        if idx in header_info:
            cur[header_info[idx]] = row[idx]
        if len(cur) == len(VEHICLE_HEADERS):
            if is_valid_vehicle(cur):
                cur.update(file_header)
                cur["datetime"] = timestring.Date(file_header['date'] + " " + cur['time'])
                cur["timeofday"] = timestring.Date("1/1/2016" + " " + cur['time'])
                data += [cur]
            elif not is_null_vehicle(cur):
                logging.info("'{}':{:<4} Invalid vehicle {}".format(
                    file_header["filename"], line_num, cur))
            cur = {}
    return data

def extract_header_info(row):
    return {idx: header for header in VEHICLE_HEADERS for idx in xrange(len(row))
            if row[idx] and header == row[idx][0:len(header)].lower()}

def read_data(file_header, csv_reader):
    header_info = None
    data = []
    for row in csv_reader:
        if header_info:
            row_data = extract_data_row(file_header, header_info, row, csv_reader.line_num)
            if row_data:
                data += row_data
            elif extract_header_info(row):
                header_info = None
        if not header_info:
            header_info = extract_header_info(row)
    return data

def read_data_file(filename):
    '''Open a single CSV file and reads the data in the file'''
    with open(filename, 'rb') as speed_file:
        speed_reader = csv.reader(speed_file)
        header = read_file_header(filename, speed_reader)
        data = read_data(header, speed_reader)
        return data

def read_data_directory(data_dir):
    '''Reads the CSV data in all the files in a directory'''
    data = []
    for filename in os.listdir(data_dir):
        full_filename = data_dir + "/" + filename
        try:
            data += read_data_file(full_filename)
        except:
            logging.exception("Exception reading %s", full_filename)
            raise
    return data

def bucket_data(data, block_duration, ignore_date=False):
    '''Buckets our data by time of day'''
    timekey = "timeofday" if ignore_date else "datetime"
    datetimes = [val[timekey] for val in data]
    min_datetime = min(datetimes) + 0  # forces copy
    min_datetime.minute = 0
    max_datetime = max(datetimes) + block_duration
    my_datetime = min_datetime
    buckets = []
    while my_datetime < max_datetime:
        end_datetime = my_datetime + block_duration
        bucket = [vehicle for vehicle in data
                  if vehicle[timekey] >= my_datetime and vehicle[timekey] < end_datetime]
        if bucket:
            buckets.append({"name": my_datetime, "data": bucket})
        my_datetime = end_datetime

    return buckets

def compute_statistics(buckets):
    '''Computes all the statistics we might want to know about a time series'''
    stats = {}
    for bucket in buckets:
        speeds = sorted([float(val["speed"]) for val in bucket["data"]])
        if not speeds:
            continue
        stats[bucket['name']] = {
            "limit": val["speed limit"],
            "count_legal": len([spd for spd in speeds if spd <= float(val["speed limit"])]),
            "%legal": 100.0 * len([spd for spd in speeds if spd <= float(val["speed limit"])]) / len(speeds),
            "min": float(speeds[0]),
            "max": float(speeds[-1]),
            "count": len(speeds),
            "85%": float(speeds[int(len(speeds) * 0.85)]),
            "99%": float(speeds[int(len(speeds) * 0.99)]),
            "diff": float(speeds[-1]) - float(speeds[0]),
            "mean": float(sum(speeds)) / len(speeds),
            "50%": float(speeds[int(len(speeds) * 0.50)]),
        }
    return stats

def group_statistics(stats):
    '''TBD'''
    return stats

def output_statistics(output_file, stats):
    '''Writes statistics to an output CSV file'''
    rows = sorted(stats.keys())
    if not rows:
        return

    writer = csv.writer(output_file)
    stats_keys = sorted(stats[rows[0]].keys())
    writer.writerow(["when"] + stats_keys)

    for row in rows:
        values = [stats[row][key] for key in stats_keys]
        when = ["{}:{}:{}".format(row.hour, row.minute, row.second)]
        writer.writerow(when + values)

def main():
    '''Reads a directory of speed data and outputs relevant statistics'''
    logging.getLogger('').setLevel(logging.DEBUG)

    data = read_data_directory("sample_data")
    buckets = bucket_data(data, datetime.timedelta(minutes=15).seconds, ignore_date=True)
    stats = compute_statistics(buckets)
    grouped_stats = group_statistics(stats)
    output_statistics(sys.stdout, grouped_stats)

if __name__ == "__main__":
    main()
