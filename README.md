# Analyses Speed Study Data

# Initial Requirements

## Problem
The speed study data I have is in a Google spreadsheet: [Sample Data](https://goo.gl/yvidBb)
I can export each sheet as a CSV and then read that in as my input.

The format of the spreadsheed export CSV looks something like this:

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

## The data to compute is:
* The max, min, 99%, and 85% speed for each 15 minute time period. [DONE]
* The convolution of the speeding data with the AAA injury and fatality tables [WON'T DO, too wonky for target audience]
* The same data with outliers removed [NTH]
* The same data with and without rain [NTH]
* The effect of rain in MPH on speeding [NTH]

## A second detail report will compute: [NEW REQUIREMENT]
* A breakdown of speeds in a particular 15 minute time period.

## Output
Should be a CSV for easy charting.

## Other criteria:
* All the rejected lines of the csv should be logged [DONE, sent to stderr]
* It should be possible to specify a minimum number of data points before statistics are computed for a time period. [DONE]
* The program should accept command line parameters to determine what to compute, so that if I need to change the time period or percentage I want to compute this can be done easily. [DONE, the interval was the only thing it really made sense to allow as a pass in]
