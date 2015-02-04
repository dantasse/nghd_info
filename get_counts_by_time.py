#!/usr/bin/env python

# Counts all the tweets by .001-degree bin, and by neighborhood. For each bin,
# for each hour, returns the number of tweets that have happened there.

from collections import Counter, defaultdict
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, argparse, pymongo, cProfile, pprint


db = pymongo.MongoClient('localhost', 27017)['tweet']

def load_point_nghd_map(point_map_filename):
    point_nghd_map = {} # (lat, lon) -> neighborhood
    reader = DictReader(open(point_map_filename))
    for line in reader:
        point_nghd_map[(float(line['lat']), float(line['lon']))] = line['nghd']
    return point_nghd_map

def run_all():
    parser = argparse.ArgumentParser()
    parser.add_argument('--point_map_file', '-p', default='point_map.csv')
    parser.add_argument('--nghds_outfile', default='outputs/nghds_num_tweets_by_hour.csv')
    parser.add_argument('--bins_outfile', default='outputs/bins_num_tweets_by_hour.csv')
    args = parser.parse_args()

    point_nghd_map = load_point_nghd_map(args.point_map_file)

    bin_hr_counts = Counter() # (lat, lon, hr) -> count
    nghd_hr_counts = Counter() # (nghd, hr) -> count

    ctr = 0
    for tweet in db.tweet_pgh.find():
        ctr += 1
        if ctr % 1000 == 0:
            print '%d tweets processed' % ctr
        lat = tweet['coordinates']['coordinates'][1]
        lon = tweet['coordinates']['coordinates'][0]
        (lat, lon) = (round(float(lat), 3), round(float(lon), 3))
        if (lat, lon) in point_nghd_map:
            nghd = point_nghd_map[(lat, lon)]
        else:
            nghd = 'Outside Pittsburgh'

        hr = util.util.get_tweet_hour(tweet)
        bin_hr_counts[(lat, lon, hr)] += 1
        nghd_hr_counts[(nghd, hr)] += 1

    pprint.pprint(nghd_hr_counts)
    bin_writer = DictWriter(open(args.bins_outfile, 'w'),
        ['lat', 'lon', 'hour', 'count'])
    for bin_hr, count in bin_hr_counts.items():
        bin_writer.writerow({'lat': bin_hr[0], 'lon': bin_hr[1],
            'hour': bin_hr[2], 'count': count})
 
    nghd_writer = DictWriter(open(args.nghds_outfile, 'w'),
        ['nghd', 'hour', 'count'])
    for nghd_hr, count in nghd_hr_counts.items():
        nghd_writer.writerow({'nghd': nghd_hr[0], 'hour': nghd_hr[1], 'count': count})
 
if __name__ == '__main__':
    cProfile.run("run_all()")
