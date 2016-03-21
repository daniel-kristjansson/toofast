"""
Analyse our speeding data
"""
import math


def bucket_data(data, block_duration):
    '''Buckets our data by time of day'''
    timekey = "datetime"
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
        speed_limit = float(bucket["data"][0]["speed limit"])
        stats[bucket['name']] = {
            "limit": speed_limit,
            "count_legal": len([spd for spd in speeds if spd <= speed_limit]),
            "%legal": 100.0 * len([spd for spd in speeds if spd <= speed_limit]) / len(speeds),
            "min": float(speeds[0]),
            "max": float(speeds[-1]),
            "count": len(speeds),
            "85%": float(speeds[int(math.floor(len(speeds) * 0.85))]),
            "99%": float(speeds[int(math.floor(len(speeds) * 0.99))]),
            "diff": float(speeds[-1]) - float(speeds[0]),
            "mean": float(sum(speeds)) / len(speeds),
            "50%": float(speeds[int(math.floor(len(speeds) * 0.50))]),
        }
    return stats


def group_statistics(stats):
    '''TBD'''
    return stats
