'''Constants'''
# Headers for each CSV. Metadata about a particular set of times
# and location for a speed study.
FILE_HEADERS = ["name", "date", "location", "direction", "weather", "speed limit"]
# Headers for each vehicle column
VEHICLE_HEADERS = ['vehicle', 'time', 'speed']
# To avoid data entry errors spoiling our data, we filter out very
# slow or very fast vehicle data
MINIMUM_SPEED = 10
MAXIMUM_SPEED = 99
