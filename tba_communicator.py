"""Sends web requests to The Blue Alliance (TBA) API.

Caches data to prevent duplicate data retrieval from the TBA API."""
# External imports
import json
import requests
import time
# Internal imports
import utils

EVENT_CODE = '2019cafr'

with open(utils.create_file_path('data/api_keys/tba_key.txt')) as file:
    API_KEY = file.read()
# Removes trailing newline (if it exists) from file data.
# Many file editors will automatically add a newline at the end of files.
API_KEY = API_KEY.rstrip('\n')

def make_request(api_url):
    """Sends a single web request to the TBA API v3 and caches result.

    api_url is the url of the API request (the path after '/api/v3')"""
    base_url = 'https://www.thebluealliance.com/api/v3/'
    full_url = base_url + api_url
    request_headers = {'X-TBA-Auth-Key': API_KEY}

    # This cache is used with TBA's 'Last-Modified' and
    # 'If-Modified-Since' headers to prevent duplicate data downloads.
    # If the data has not changed since the last request, it will be
    # pulled from the cache.
    # Documentation of the 'Last-Modified' and 'If-Modified-Since' headers:
    # https://www.thebluealliance.com/apidocs#apiv3
    try:
        with open(utils.create_file_path('data/cache/tba/tba.json'), 'r') as file_:
            cached_requests = json.load(file_)
    except FileNotFoundError:
        cached_requests = {}

    # 'cache_last_modified' is the time that the data in the cache was
    # published to TBA's API.
    cache_last_modified = cached_requests.get(api_url, {}).get('last_modified')
    if cache_last_modified is not None:
        request_headers['If-Modified-Since'] = cache_last_modified

    print('Retrieving data from TBA...')
    while True:
        try:
            request = requests.get(full_url, headers=request_headers)
        except requests.exceptions.ConnectionError:
            print('Error: No internet connection.  Trying again in 3 seconds...')
        else:
            print('TBA data successfully retrieved.')
            break
        time.sleep(3)

    # A 304 status code means the data was not modified since our last
    # request, and we can pull it from the cache.
    if request.status_code == 304:
        return cached_requests[api_url]['data']
    # A 200 status code means the request was successful
    elif request.status_code == 200:
        # Updates local cache
        cached_requests[api_url] = {
            'last_modified': request.headers['Last-Modified'],
            'data': request.json(),
        }
        with open(utils.create_file_path('data/cache/tba/tba.json'), 'w') as file_:
            json.dump(cached_requests, file_)

        return request.json()
    else:
        print(f'Request failed with status code {request.status_code}')
        return {}

def request_matches():
    """Requests the match schedule from the TBA API."""
    return make_request(f'event/{EVENT_CODE}/matches/simple')

def request_teams():
    """Requests the team list from the TBA API."""
    return make_request(f'event/{EVENT_CODE}/teams/simple')
