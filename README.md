# toofast
Analyses Speed Study Data

# Initial Requirements

# The data I have is in a Google spreadsheet: https://goo.gl/yvidBb
# I can export each sheet as a CSV and then read that in as my input.

# The data I want to compute is:
#  The max, min, 99%, and 85% speed for each 15 minute time period.
#  The convolution of the speeding data with the AAA injury and fatality tables
#  The same data with outliers removed
#  The same data with and without rain
#  The effect of rain in MPH on speeding

# I want the output as a CSV (so I can chart the data).

# Other criteria:
#  *  All the rejected lines of the csv should be logged (the headers and notes, etc)
#  *  It should be possible to specify a minimum number of data points before statistics are computed for a time period.
#  *  The program should accept command line parameters to determine what to compute, so that if I need to change the time period or percentage I want to compute this can be done easily.
