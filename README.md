# nghd\_info
Info about Pittsburgh neighborhoods.

Starting with point\_map.csv, which will put a .001-degree grid all over
Pittsburgh, so you can quickly map points to census tracts, block groups,
blocks, and neighborhoods.

We'll create a bunch of CSV files in output/. Then maybe there will be some
method that combines them all into one big csv? I figure this is better because
then if one of them is time-consuming, you don't have to re-create that every
time you re-create anything.

demographics/ is from pghsnap.com, or http://www.pittsburghpa.gov/dcp/snap/
Demographic data from the census. Also `demographics/blocks_housing` which is
from America Fact Finder.

TODO: should I be organizing all these data files into the same place?

# Scripts
yelp_search.py: steals data from Yelp and generates outputs/bins_pgh_venue_categories.json.

get_venues_users.py: looks up bins_pgh_venue_categories.json and bins_num_tweets.csv to generate bins_uniq_user_venue.json


# Outputs
bins_num_tweets.csv: Stores the number of tweets and unique number of tweeters in each bin.

bins_pgh_venue_categories.json: Stores an array of dictionaries which has bins and categories.

bins_uniq_user_venue.json: Stores a dictionary that maps each bin to venue frequencies 
  and the number of unique users in that bin.
