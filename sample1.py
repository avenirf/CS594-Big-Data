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
from pymongo import MongoClient



API_HOST = 'api.yelp.com'
# DEFAULT_TERM = 'dinner'
DEFAULT_TERM = 'food'
DEFAULT_LOCATION = '91106'
SEARCH_LIMIT = 20
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = '0nVi37zNSCDUv_NQwx0dqw'
CONSUMER_SECRET = '78XSQwSkVeWkt8FzWt4gnTijbR8'
TOKEN = 'V5PV0jpUWL3j0msgu6F2_Tgp69_FVBnR'
TOKEN_SECRET = 'FmP1XbMj1_jKWBAtIpydcdNTSlY'

#connect to pymongo
connection = MongoClient()
db = connection.yelp.places


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
    
    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
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

def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(term, location)

    businesses = response.get('businesses')

    if not businesses:
        print u'No businesses for {0} in {1} found.'.format(term, location)
        return
        
    print u'{0} businesses found ...'.format(
        len(businesses)
    )
    # print type(businesses)
    for business in businesses:
    	business_id = business['id']
    	response = get_business(business_id)

        categories = business['categories']
        rating = business['rating']
        review_count = business['review_count']

        post = {"id:" : business_id, "categories": categories, "rating": rating, "review_count": review_count}
        db.insert(post)

    	print u'Result for business "{0}" found:'.format(business_id)
    	print u'Categories: "{0}" '.format(business['categories'])
    	print u'Rating: "{0}" '.format(business['rating'])
#     	print u'Postal Code: "{0}" '.format(business['postal_code'])
    	print u'Review Count: "{0}" '.format(business['review_count'])
    	print ""
    	
    	
#     	pprint.pprint(response, indent=2)


def main():


    restaurants = {}

    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM, type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location', default=DEFAULT_LOCATION, type=str, help='Search location (default: %(default)s)')

    input_values = parser.parse_args()
    print input_values.location
    print input_values.term
    zipCodes = []
    # Los Angeles 90001-90103
    for codes in range(90001,90040):
        zipCodes.append(codes)
    # zipCodes = ['91101','91102','91103']
    # print zipCodes
    # removing invalid zip codes
    # zipCodes.remove(90085)
    # zipCodes.remove(90092)
    # zipCodes.remove(90097)
    # zipCodes.remove(90098)
    # zipCodes.remove(90100)
    # zipCodes.remove(90102)

    print zipCodes
    print len(zipCodes)
    for code in zipCodes:
        print code
        try:
            query_api(input_values.term, str(code))
        except urllib2.HTTPError as error:
            sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))

    db.find().count()
    # try:
    #     query_api(input_values.term, input_values.location)
    # except urllib2.HTTPError as error:
    #     sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))


if __name__ == '__main__':
    main()