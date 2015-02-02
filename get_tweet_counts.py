#!/usr/bin/env python

# Counts all the tweets by .01-degree bin, and by neighborhood. For each bin,
# prints out how many tweets have occurred in that bin, and how many unique
# tweeters have tweeted there.

from collections import Counter, defaultdict
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, argparse, pymongo, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name

def run_all():
    parser = argparse.ArgumentParser()
    parser.add_argument('--munis_file', '-m', default='geodata/Allegheny_Munis.json',
        help='GeoJSON file with Allegheny county municipal boundaries')
    parser.add_argument('--neighborhoods_file', '-n', default='geodata/Pittsburgh_Neighborhoods.json',
        help='GeoJSON file with neighborhood boundaries')
    parser.add_argument('--point_map_file', '-p', default='point_map.csv')
    parser.add_argument('--neighborhoods_outfile', default='outputs/nghds_num_tweets.csv')
    parser.add_argument('--bins_outfile', default='outputs/bins_num_tweets.csv')
    args = parser.parse_args()

    nghds = util.neighborhoods.load_nghds(args.neighborhoods_file)
    munis = util.neighborhoods.load_allegheny_munis(args.munis_file)

    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open(args.point_map_file)):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

    bin_tweets = Counter()
    bin_users = defaultdict(set)
    nghd_tweets = Counter()
    nghd_users = defaultdict(set)

    nghds_writer = DictWriter(open(args.neighborhoods_outfile, 'w'),
        ['nghd', 'num_tweets', 'num_users'])
    nghds_writer.writeheader()
    bins_writer = DictWriter(open(args.bins_outfile, 'w'),
        ['lat', 'lon', 'num_tweets', 'num_users'])
    bins_writer.writeheader()

    db = pymongo.MongoClient('localhost', 27017)['tweet']

    counter = 0
    for tweet in db.tweet_pgh.find():
        counter += 1
        if (counter % 1000) == 0:
            print str(counter) + ' tweets processed'
        coords = tweet['coordinates']['coordinates']
        bin = util.util.round_latlon(coords[1], coords[0])
        bin_tweets[bin] += 1
        bin_users[bin].add(tweet['user']['screen_name'])

        if bin in bins_to_nghds:
            nghd = bins_to_nghds[bin]
        else:
            nghd = 'Outside Pittsburgh'
        nghd_tweets[nghd] += 1
        nghd_users[nghd].add(tweet['user']['screen_name'])
    
    for nghd in nghd_tweets:
        nghds_writer.writerow({'nghd': nghd, 'num_tweets': nghd_tweets[nghd],
            'num_users': len(nghd_users[nghd])})
    for bin in bin_tweets:
        bins_writer.writerow({'lat': bin[0], 'lon': bin[1],
            'num_tweets': bin_tweets[bin], 'num_users': len(bin_users[bin])})

if __name__ == '__main__':
    cProfile.run("run_all()")
