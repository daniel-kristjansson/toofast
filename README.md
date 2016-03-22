# Analyses Speed Study Data

# Introduction

This program was created to analyse the speed study data collected manually first on paper and
then in a google spreadsheet [Sample Data](https://goo.gl/yvidBb).

Consequently we needed to read in this data and found that
exporting each sheet as a CSV was the simplest approach.

This program reads a directory of files containing such CSV
files and then outputs one of two types of reports.

The first type is a statistics only report, and it provides
the statistics people are concerned about when evaluating
whether there is a speeding problem on a street that might
need to be addressed.

Various statistics tell us different things
 * 99% data shows us when there should be enforcement.
 * 85% data when more than 5 mph above the speed limit shows us that reengineering is called for.
 * min and max show us if there is a large differential in speed
 * diff is the actual difference between the min and max for convenience

# How to install

mkvirtualenv myenv
pip install -e .

# How to use

## To get basic help
  speeders.py --help

## To run a statistical analysis on some sample data and put it in a file
  speeders.py sample_data > my_cool_output.csv

## To run a statistical analysis on some sample data with 30 minute intervals
  speeders.py sample_data --interval 30

## To get speed detail on some sample data
  speeders.py sample_data --detail

## Other options

You can also run with debugging or set the minimum number of
samples in an interval before we compute statistics.

You can also combine the options above to get different reports.

The output CSV can be consumed by various other utilities for graphics the data.

## Notes

Any vehicle data the program can't ingest results in a log line containing the file
and problematic line of the file.

Any header data the program can't ingest will exit the program and log the name of
the problematic file.

All logging is to stderr and all output to stdout.

# Initial Requirements

## Details on the input file format

The format of the spreadsheed export CSV looks like this:

```
,,,,,,,,,,,
,Name[s],Daniel K & Julie T,,,,,,,,,
,Date,8/10/2015,,,,,,,,,
,Location,Rogers Ave & Midwood St,,,,,,,,,
,Direction,North,,,,,,,,,
,Weather,Sunny,,,,,,,,,
,Speed Limit,25,,,,,,,,,
,,,,,,,,,,,
,Vehicle,Time,Speed,,Vehicle,Time,Speed,,Vehicle,Time,Speed
,1,6:56,44,,1,7:16,38,,1,7:31,31
,,,,,,,,,,,
,Vehicle,Time,Speed,,Vehicle,Time,Speed,,Vehicle,Time,Speed
,1,7:49,25,,1,8:05,29,,1,8:22,30
```

This peculiar format comes from a sheet which is optimized for human input,
not for ease of parsing.
