"""
Analyse our speeding data
"""
import math
from collections import defaultdict


def min_timekey(datetimes):
    '''Finds minumum times from a list'''
    min_datetime = min(datetimes) + 0  # + 0 forces copy
    min_datetime.minute = 0
    return min_datetime


def get_bucket_name(data_time, min_datetime, block_duration):
    '''Computes the bucket name based on the data point time'''
    sec_diff = data_time.to_unixtime() - min_datetime.to_unixtime()
    sec_diff = int(math.floor(sec_diff / block_duration)) * block_duration
    date = min_datetime + sec_diff
    return date.date.timetuple()


def bucket_data(data, block_duration):
    '''
    Buckets our data by time of day

    This returns a dictionary where the key is a time.struct_time
    corresponding to the begining of a bucket's time interval and
    the value is a list of vehicles that fall in the bucket of
    time starting at that time and ending before a block_duration
    number of seconds have elapsed.

    '''
    timekey = "datetime"
    min_datetime = min_timekey([val[timekey] for val in data])
    buckets = {}
    for vehicle in data:
        name = get_bucket_name(vehicle[timekey], min_datetime, block_duration)
        if buckets.get(name):
            buckets[name].append(vehicle)
        else:
            buckets[name] = [vehicle]
    return buckets


def compute_statistics(buckets):
    '''Computes all the statistics we might want to know about a time series'''
    stats = {}
    for name, bucket in buckets.iteritems():
        speeds = sorted([float(val["speed"]) for val in bucket])
        if not speeds:
            continue
        speed_limit = float(bucket[0]["speed limit"])
        max_speed_index = len(speeds) - 1
        stats[name] = {
            "limit": speed_limit,
            "count_legal": len([spd for spd in speeds if spd <= speed_limit]),
            "%legal": 100.0 * len([spd for spd in speeds if spd <= speed_limit]) / len(speeds),
            "min": float(speeds[0]),
            "max": float(speeds[-1]),
            "count": len(speeds),
            "85%": float(speeds[int(math.floor(max_speed_index * 0.85))]),
            "99%": float(speeds[int(math.floor(max_speed_index * 0.99))]),
            "diff": float(speeds[-1]) - float(speeds[0]),
            "mean": float(sum(speeds)) / len(speeds),
            "50%": float(speeds[int(math.floor(max_speed_index * 0.50))]),
            "_speeds": speeds
        }
    return stats


def count_speeds(speeds):
    '''
    Count the speeds in each 5 mph interval

    Returns dictionary with string keys at 5 mph intervals containing
    a count of values found between that value and 5 mph faster.

    i.e. {"10": 2, "15": 5, "20": 2}
    '''
    speedbuckets = defaultdict(int)
    for speed in speeds:
        speedbuckets[int(math.floor(speed / 5) * 5)] += 1
    return {"{}-{}".format(key, key + 5): value
            for key, value in speedbuckets.iteritems()}


def combine_stats(stats):
    '''Given a list of stats compute combined statistics'''
    count = sum([stat["count"] for stat in stats])
    count_legal = sum([stat["count_legal"] for stat in stats])
    inv_stat_cnt = 1.0 / len(stats)
    min_spd = min([stat["min"] for stat in stats])
    max_spd = max([stat["max"] for stat in stats])
    speeds = []
    for stat in stats:
        speeds += stat["_speeds"]
    return {
        "limit": stats[0]["limit"],
        "count_legal": count_legal,
        "count": count,
        "%legal": count_legal * 100.0 / count,
        "min": min_spd,
        "max": max_spd,
        "85%": sum([stat["85%"] for stat in stats]) * inv_stat_cnt,
        "99%": sum([stat["99%"] for stat in stats]) * inv_stat_cnt,
        "diff": max_spd - min_spd,
        "mean": sum([stat["mean"] for stat in stats]) * inv_stat_cnt,
        "50%": sum([stat["50%"] for stat in stats]) * inv_stat_cnt,
        "_speeds": speeds
    }


def group_statistics(stats):
    '''Group our statistics by time of day'''
    # remap stats by time of day tuple (hour,minute)
    tod_stat = {}
    for when, stat in stats.iteritems():
        tod = (when.tm_hour, when.tm_min)
        if tod_stat.get(tod):
            tod_stat[tod].append(stat)
        else:
            tod_stat[tod] = [stat]
    return {
        str("{:02}:{:02}:00".format(when[0], when[1])):
        combine_stats(group_stats) for when, group_stats in tod_stat.iteritems()}


def filter_statistics(stats, min_count):
    '''Filter out statistics that don't meet our criteria'''
    if min_count:
        return {when: stat for when, stat in stats.iteritems()
                if stat["count"] > min_count}
    else:
        return stats
