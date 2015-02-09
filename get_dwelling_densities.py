#!/usr/bin/env python

# Calculates dwelling density - dwellings per acre.
# (maybe this should be dwellings per residential acre? not sure.)
# According to Jane Jacobs, 0-6 per acre works for suburbs, 10-20 for semi-
# suburbs, 20-100 is this "in between" where people are strangers but there
# is no vitality, and 100+ tends to work out nicely.

import csv, argparse, ujson
from collections import defaultdict

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--area_file', default='demographics/population_density.csv')
    parser.add_argument('--housing_file', default='demographics/housing.csv')
    parser.add_argument('--zoning_file', default='demographics/zoning.csv')
    parser.add_argument('--tract_block_group_file', default='demographics/tract_block_group.csv')
    parser.add_argument('--blocks_housing_file', default='demographics/blocks_housing.csv')
    parser.add_argument('--blocks_file', default='geodata/Pittsburgh_Blocks.json')
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

    blockgroup_nghd = {} # int block group number -> string neighborhood name
    blockgroup_file = open(args.tract_block_group_file)
    for line in csv.DictReader(blockgroup_file):
        nghd = line['HOOD']
        census_code = int(line['CENSUS CODE'])
        blockgroup_nghd[census_code] = nghd
    blockgroup_file.close()
    # print blockgroup_nghd

    blocks_json = ujson.load(open(args.blocks_file))
    block_acres = {} # int block number -> float number of acres
    for feature in blocks_json['features']:
        block_props = feature['properties']
        block_acres[int(block_props['GEOID10'])] = float(block_props['Acres'])

    nghd_resid_acres = defaultdict(float) # string nghd -> num residential acres
    nghd_dwellings = defaultdict(int) # string nghd -> num dwellings
    for line in csv.DictReader(open(args.blocks_housing_file)):
        dwellings = int(line['D001'])
        if dwellings == 0:
            # Ignore these blocks b/c probably not residential.
            continue
        block = line['GEO.id2']
        block_id = int(line['GEO.id2'])
        blockgroup = int(block[0:-3])
        if blockgroup not in blockgroup_nghd:
            # print str(blockgroup) + " not in Pittsburgh"
            # Ignore all the non-pgh ones.
            continue

        nghd = blockgroup_nghd[blockgroup]
        acres = block_acres[block_id]
        nghd_dwellings[nghd] += dwellings
        nghd_resid_acres[nghd] += acres
        

    for line in csv.DictReader(open(args.area_file)):
        nghd = line['Neighborhood']
        acres = float(line['Land Area (acres)'].replace(',',''))
        if acres != num_acres[nghd]:
            print "acres mismatch for %s, %.02f, %.02f" % (nghd, acres, num_acres[nghd])

        density = housing_numbers[nghd] / (acres * pct_residential[nghd])
        pct_resid = pct_residential[nghd]
        # print '%s\tacres: %d\tpct_res: %.02f\tdensity: %.02f' % (nghd, acres, pct_resid, density)

        density_from_blocks = nghd_dwellings[nghd] * 1.0 / (nghd_resid_acres[nghd] + .001)
        # print '%.02f\t%.02f\t%s' % (density, density_from_blocks, nghd)
        # Turns out density from blocks is even lower than from nghd-level, so
        # let's continue to use the nghd-level stats.
        writer.writerow({'nghd': nghd, 'units_per_acre_residential': '%.02f' % density})

