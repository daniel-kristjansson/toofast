'''Output our statistics'''
import csv


def output_csv(output_file, stats):
    '''
    Writes statistics to an output CSV file

    This assumes stats is a dictonary of the form:
    {
       "when 1": { "key1": "value1",  "key2": "value2" }
       "when 2": { "key1": "value1",  "key3": "value3" }
    }

    All the keys plus the when column are extracted to become the header of the CSV.
    Then the values from each sub dictionary in the stats data are extracted one to a row.
    You can also be assured that the keys will be sorted into a stable ordering.

    Finally, you may store private data in the internal dictionaries so long as the
    key it is stored under is prefixed the an underscore "_".

    In this example:

    when,key1,key2,key3
    when 1,value1,value2,
    when 2,value1,,value3
    '''
    rows = sorted(stats.keys())
    if not rows:
        return

    writer = csv.writer(output_file)
    stats_key_set = set([key for row in rows for key in stats[row].keys() if key[0:1] != "_"])
    stats_keys = sorted(list(stats_key_set))
    writer.writerow(["when"] + stats_keys)

    for row in rows:
        values = [stats[row].get(key, "") for key in stats_keys]
        writer.writerow([str(row)] + values)
