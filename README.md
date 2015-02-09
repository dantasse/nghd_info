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
