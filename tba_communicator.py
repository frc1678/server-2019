"""Sends web requests to The Blue Alliance (TBA) API."""
# External imports
import requests
import time
# Internal imports
import utils

EVENT_CODE = '2018cafr'

with open(utils.create_file_path('data/api_keys/tba_key.txt')) as file:
    API_KEY = file.read()
# Removes trailing newline (if it exists) from file data.
# Many file editors will automatically add a newline at the end of files.
API_KEY = API_KEY.rstrip('\n')

def make_request(api_url, last_modified_header=None):
    """Sends a single web request to the TBA v3 API.

    api_url is the url of the API request (the path after '/api/v3')
    last_modified_header (optional) will allow the TBA API to respond
    with a 304 status code if the data has not been modified since the
    last time it was retrieved."""
    base_url = 'https://www.thebluealliance.com/api/v3/'
    full_url = base_url + api_url
    request_headers = {'X-TBA-Auth-Key': API_KEY}
    if last_modified_header is not None:
        request_headers['If-Modified-Since'] = last_modified_header
    return requests.get(full_url, headers=request_headers)

LAST_MATCH_SCHEDULE_REQUEST = {}
def request_match_schedule():
    """Requests the match schedule from the TBA API."""
    print('Retrieving data from TBA...')
    while True:
        try:
            request = make_request(f'event/{EVENT_CODE}/matches/simple', \
                LAST_MATCH_SCHEDULE_REQUEST.get('Last-Modified'))
        except requests.exceptions.ConnectionError:
            print('Error: No internet connection.  Trying again in 3 seconds...')
        else:
            print('TBA data successfully retrieved.')
            break
        time.sleep(3)

    # A 304 status code means the data was not modified since our last
    # request, and we can pull it from the cache.
    if request.status_code == 304:
        return LAST_MATCH_SCHEDULE_REQUEST['data']
    # A 200 status code means the request was successful
    elif request.status_code == 200:
        # Updates local cache
        LAST_MATCH_SCHEDULE_REQUEST['Last-Modified'] = \
            request.headers['Last-Modified']
        LAST_MATCH_SCHEDULE_REQUEST['data'] = request.json()

        return request.json()
    else:
        print(f'Request failed with status code:{request.status_code}')
        return {}
