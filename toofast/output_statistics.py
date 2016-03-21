'''Output our statistics'''
import csv


def output_csv(output_file, stats):
    '''Writes statistics to an output CSV file'''
    rows = sorted(stats.keys())
    if not rows:
        return

    writer = csv.writer(output_file)
    stats_keys = sorted(stats[rows[0]].keys())
    writer.writerow(["when"] + stats_keys)

    for row in rows:
        values = [stats[row][key] for key in stats_keys]
        writer.writerow([str(row)] + values)
