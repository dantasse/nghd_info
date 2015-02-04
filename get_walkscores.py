#!/usr/bin/env python

# Scripts to search for Walkscores of a grid of points around the Pittsburgh
# area.

import ConfigParser, argparse, numpy, urllib2, json, requests, time, csv

if __name__ == '__main__':

    config = ConfigParser.ConfigParser()
    config.read('config.txt')
    walkscore_api_key = config.get('walkscore', 'api_key')

    parser = argparse.ArgumentParser()
    # Defaults are rough Pittsburgh boundaries.
    parser.add_argument('--min_lat', type=float, default=40.241667)
    parser.add_argument('--max_lat', type=float, default=40.641667)
    parser.add_argument('--min_lon', type=float, default=-80.2)
    parser.add_argument('--max_lon', type=float, default=-79.8)
    parser.add_argument('--outfile', default='walkscores.csv')
    parser.add_argument('--sleep_time', type=int, default=2,
        help='how long, in seconds, to sleep between each request')
    args = parser.parse_args()


    # Write things along the way in case anything goes wrong - dictwriter will
    # make for a cleaner end result, but this way at least you have something.
    jsonfile = open('json_walkscores.csv', 'w')
    lines = []
    for lat in numpy.arange(args.min_lat, args.max_lat, .005):
        for lon in numpy.arange(args.min_lon, args.max_lon, .005):
            params = {'format': 'json', 'lat': lat, 'lon': lon,
                'wsapikey': walkscore_api_key}
            res = requests.get('http://api.walkscore.com/score', params=params).json()
            # Remove extra garbage included in every response we don't need:
            del res['logo_url']
            del res['more_info_icon']
            del res['more_info_link']
            del res['ws_link']
            jsonfile.write(str(res) + '\n')
            print res
            lines.append(res)
            time.sleep(args.sleep_time)

    fieldnames = ['snapped_lat', 'snapped_lon', 'status', 'walkscore', 'description', 'updated']
    writer = csv.DictWriter(open(args.outfile, 'w'), fieldnames=fieldnames)
    writer.writeheader()
    for line in lines:
        line = {'snapped_lat': line['snapped_lat'], 'snapped_lon': line['snapped_lon'],
            'status': line['status'], 'walkscore': line['walkscore'],
            'description': line['description'], 'updated': line['updated']}
        writer.writerow(line)
        
