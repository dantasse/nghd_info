#!/usr/bin/env python

# Makes a JSON of lat, lon -> neighborhood name. For easier classification of
# neighborhood - you don't have to figure out which neighborhood each point is
# in, just round it off to 3 decimal places and then look it up in the
# point map.

import argparse, numpy, csv
import util.util, util.neighborhoods

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--granularity', '-g', type=float, default=.001)
    parser.add_argument('--outfile', '-o', default='point_map.csv')
    args = parser.parse_args()

    nghds = util.neighborhoods.load_nghds('geodata/Pittsburgh_Neighborhoods.json')
    munis = util.neighborhoods.load_allegheny_munis('geodata/Allegheny_Munis.json')

    writer = csv.DictWriter(open(args.outfile, 'w'), ['lat', 'lon', 'nghd'])
    writer.writeheader()

    counter = 0
    for lat in numpy.arange(40.241667, 40.641667, args.granularity):
        for lon in numpy.arange(-80.2, -79.8, args.granularity):
            lat = round(lat, 3)
            lon = round(lon, 3)
            nghd = util.neighborhoods.get_neighborhood_or_muni_name(nghds, munis, lon, lat)
            writer.writerow({'lat': lat, 'lon': lon, 'nghd': nghd})
            counter += 1
            if counter % 1000 == 0:
                print counter

