#!/usr/bin/env python

# Functions to tell which census tract, census block group, and census block
# a lat/lon point is in.

import shapely.geometry, geojson

# load blocks, groups, and tracts
print "Importing json files from census.py"
tracts = geojson.load(open('geodata/Pittsburgh_Tracts.json')).features
for tract in tracts:
    tract['shape'] = shapely.geometry.asShape(tract.geometry)
pittsburgh_outline = tracts[0]['shape']
for tract in tracts:
    pittsburgh_outline = pittsburgh_outline.union(tract['shape'])
groups = geojson.load(open('geodata/Pittsburgh_Block_Groups.json')).features
for group in groups:
    group['shape'] = shapely.geometry.asShape(group.geometry)
blocks = geojson.load(open('geodata/Pittsburgh_Blocks.json')).features
for block in blocks:
    block['shape'] = shapely.geometry.asShape(block.geometry)
print "Done importing json files from census.py"

# Returns a Census tract name (NAME10), which is a string of a number, like "605"
def get_tract_name(lat, lon):
    point = shapely.geometry.Point(lon, lat)
    if not pittsburgh_outline.contains(point):
        return 'Outside Pittsburgh'
    for tract in tracts:
        if tract['shape'].contains(point):
            # Move this to the front of the queue so it's checked first next time
            tracts.remove(tract)
            tracts.insert(0, tract)
            return tract.properties['NAME10']
    return 'Outside Pittsburgh'

# Returns a census block group ID (GEOID10), like '420030305002'.
def get_group_ID(lat, lon):
    point = shapely.geometry.Point(lon, lat)
    if not pittsburgh_outline.contains(point):
        return 'Outside Pittsburgh'
    for group in groups:
        if group['shape'].contains(point):
            # Move this to the front of the queue so it's checked first next time
            groups.remove(group)
            groups.insert(0, group)
            return group.properties['GEOID10']
    return 'Outside Pittsburgh'

# Returns a census block ID (BLOCKCE10), like '2022'.
def get_block_name(lat, lon):
    point = shapely.geometry.Point(lon, lat)
    if not pittsburgh_outline.contains(point):
        return 'Outside Pittsburgh'
    for block in blocks:
        if block['shape'].contains(point):
            # Move this to the front of the queue so it's checked first next time
            blocks.remove(block)
            blocks.insert(0, block)
            return block.properties['BLOCKCE10']
    return 'Outside Pittsburgh'

