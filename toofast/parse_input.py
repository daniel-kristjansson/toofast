'''Handles Parsing of CSV Input'''

import logging
import csv
import os
import timestring
from .constants import (
    FILE_HEADERS, VEHICLE_HEADERS, MINIMUM_SPEED, MAXIMUM_SPEED)


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
                return {header: row[idx + 1]}
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
    '''
    Extracts one row of speed data given a header info telling us the meaning of each column.

    We expect the file header to contain any meta data to add to each complete set of vehicle info.
    We expect the header info to give a VEHICLE_HEADER key for each meaningful row of data.
    We expect the row to contain one or more vehicles.

    The return value is a list of vehicle dictionaries where a vehicle consists of each of the keys
    in VEHICLE_HEADER with their values plus any key value pairs in the file_header.

    Any unexpected data is logged at the info level.
    '''
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
                msg = "'{}':{:<4} Invalid vehicle {}".format(
                    file_header["filename"], line_num, cur)
                logging.info(msg)  # pylint wants me to use % but I want prettier printing
            cur = {}
    return data


def extract_header_info(row):
    '''
    Returns a header_dictionary for use by the extract_data_row function.

    The header info is a dictionary where the keys are column indices and the values are the
    VEHICLE_HEADER keys which map to those columns.

    '''
    return {idx: header for header in VEHICLE_HEADERS for idx in xrange(len(row))
            if row[idx] and header == row[idx][0:len(header)].lower()}


def read_vehicle_data(file_header, csv_reader):
    '''Reads the vehicle data in a CSV file'''
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


def read_data_file(filename):  # pragma: no cover
    '''Open a single CSV file and reads the data in the file'''
    with open(filename, 'rb') as speed_file:
        speed_reader = csv.reader(speed_file)
        header = read_file_header(filename, speed_reader)
        data = read_vehicle_data(header, speed_reader)
        return data


def read_data_directory(data_dir):  # pragma: no cover
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
