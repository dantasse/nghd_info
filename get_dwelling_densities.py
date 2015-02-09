#!/usr/bin/env python

# Calculates dwelling density - dwellings per acre.
# (maybe this should be dwellings per residential acre? not sure.)
# According to Jane Jacobs, 0-6 per acre works for suburbs, 10-20 for semi-
# suburbs, 20-100 is this "in between" where people are strangers but there
# is no vitality, and 100+ tends to work out nicely.

import csv, argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--area_file', default='demographics/population_density.csv')
    parser.add_argument('--housing_file', default='demographics/housing.csv')
    parser.add_argument('--zoning_file', default='demographics/zoning.csv')
    parser.add_argument('--outfile', default='outputs/nghds_dwelling_densities.csv')
    args = parser.parse_args()

    housing_numbers = {} # string neighborhood name -> int number of dwellings.
    pct_residential = {} # string neighborhood name -> % residential (btwn 0-1).
    num_acres = {} # string neighborhood name -> float number of acres.
    for line in csv.DictReader(open(args.housing_file)):
        housing_numbers[line['Neighborhood']] = int(line['Total # Units (2010)'].replace(',', ''))

    for line in csv.DictReader(open(args.zoning_file)):
        num_acres[line['Neighborhood']] = float(line['Land Area (acres)'].replace(',',''))
        pct_resid_only = float(line['Residential'].replace('%','')) * .01
        pct_mixed_comm = float(line['Mixed Use / Commercial'].replace('%','')) * .01
        pct_mixed_ind = float(line['Mixed Use / Industrial'].replace('%','')) * .01
        pct_special = float(line['Special Land Use'].replace('%','')) * .01

        # I guess mixed use/commercial counts as say 0.75 residential? (because
        # what's the use mixed with? gotta be residential, right?)
        # Mixed/industrial and Special are both .25? These are all wild out of
        # a hat numbers, but we have to somehow account for the fact that, say,
        # 90% of downtown is "special", etc.
        pct_residential[line['Neighborhood']] = pct_resid_only + \
            0.75 * pct_mixed_comm + 0.25 * pct_mixed_ind + 0.25 * pct_special

    writer = csv.DictWriter(open(args.outfile, 'w'), ['nghd', 'units_per_acre_residential'])
    writer.writeheader()

    for line in csv.DictReader(open(args.area_file)):
        nghd = line['Neighborhood']
        acres = float(line['Land Area (acres)'].replace(',',''))
        if acres != num_acres[nghd]:
            print "acres mismatch for %s, %.02f, %.02f" % (nghd, acres, num_acres[nghd])

        density = housing_numbers[nghd] / (acres * pct_residential[nghd])
        pct_resid = pct_residential[nghd]
        # print '%s\tacres: %d\tpct_resid: %.02f\tdensity: %.02f' % (nghd, acres, pct_resid, density)
        writer.writerow({'nghd': nghd, 'units_per_acre_residential': '%.02f' % density})

