# -*- coding: utf-8 -*-
"""
Yelp API v2.0 code sample.
This program demonstrates the capability of the Yelp API version 2.0
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/documentation for the API documentation.
This program requires the Python oauth2 library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2

from collections import Counter, defaultdict

API_HOST = 'api.yelp.com'
DEFAULT_TERM = ''
DEFAULT_LOCATION = ''
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = '79XAvpb_7jLcrfETd10Ulg'
CONSUMER_SECRET = '86SyUjiWC3BqDLe0-3D1SALnAh8'
TOKEN = 'ca9rhwH498vszAPPCmHbUoQvvsIBFn0c'
TOKEN_SECRET = 'umFAEI5VGARRIh3rhPUkg6Hczvs'


def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    #print u'Querying {0} ...'.format(signed_url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(bounds):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'bounds': bounds
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)

def query_api():
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bin_categories = defaultdict(dict)

    bin_count = 0
    venue_count = 0

    for bin_lng in range(-80200, -79800):
        for bin_lat in range(40240, 40640):
            bin_count += 1
            if bin_count % 200 == 0:
                print "Bin Count " + str(bin_count) + ', (' + str(bin_lng) + "," + str(bin_lat) + ")"

            ne = (float(bin_lat)/1000, float(bin_lng)/1000)
            sw = (float(bin_lat + 1)/1000 , float(bin_lng - 1)/1000)
            bin = ne
            sw = ','.join([str(x) for x in sw])
            ne = ','.join([str(x) for x in ne])
            bounds = sw + '|' + ne
          
            response = search(bounds)
            businesses = response.get('businesses')

            if businesses:
                for venue in businesses:
                    category = None
                    if 'categories' in venue and len(venue['categories']) > 0:
                        category = venue['categories'][0][0]
                    if not category:
                        continue

                    if bin not in bin_categories:
                        bin_categories[bin][category] = 1
                    else:
                        if category in bin_categories[bin]:
                            bin_categories[bin][category] += 1
                        else:
                            bin_categories[bin][category] = 1
            else:
                print "No Businesses."
            #pprint.pprint(response, indent=2)

    with open("outputs/bins_pgh_venue_categories.json", 'a') as f:
        res = []
        for k, v in bin_categories.items():
            res.append({'bin': k, 'categories': v})
        f.write(json.dumps(res))

def main():
    try:
        query_api()
    except urllib2.HTTPError as error:
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))


if __name__ == '__main__':
    main()
