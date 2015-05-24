from csv import DictReader
import json

def round_latlon(lat, lon):
    if lat is None or lon is None:
        return (None, None)
    return (round(float(lat), 2), round(float(lon), 2))

bin_to_user_venue = {}
for line in DictReader(open('outputs/bins_num_tweets.csv')):
    bin = str(round_latlon(float(line['lat']), float(line['lon'])))
    num = int(line['num_users'])
    if bin in bin_to_user_venue:
        bin_to_user_venue[bin]['user'] += num
    else:
        bin_to_user_venue[bin] = {'user': num}
    
with open('outputs/bins_pgh_venue_categories.json', 'r') as f:
    bin_to_venue_categories = json.load(f)
    for bin_venues in bin_to_venue_categories:
        bin = str((bin_venues['bin'][0], bin_venues['bin'][1]))
        categories = bin_venues['categories']
        if bin in bin_to_user_venue:
            bin_to_user_venue[bin]['venue'] = categories
        else:
            continue

with open('outputs/bins_uniq_user_venue.json', 'a') as f:
    f.write(json.dumps(bin_to_user_venue))
