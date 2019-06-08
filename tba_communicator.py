"""Sends web requests to The Blue Alliance (TBA) APIv3

Caches data to prevent duplicate data retrieval from the TBA API.

API documentation: https://www.thebluealliance.com/apidocs/v3"""
# External imports
import json
import requests
import time
# Internal imports
import utils

EVENT_CODE = '2019carv'

with open(utils.create_file_path('data/api_keys/tba_key.txt')) as file:
    API_KEY = file.read()
# Removes trailing newline (if it exists) from file data.
# Many file editors will automatically add a newline at the end of files.
API_KEY = API_KEY.rstrip('\n')

def make_request(api_url, show_output=True, acceptable_cache_age=0):
    """Sends a single web request to the TBA API v3 and caches result.

    api_url is the url of the API request (the path after '/api/v3')
    show_output shows print statements about the status of the
    request.  Defaults to True.
    acceptable_cache_age is the maximum age (in seconds) of data that
    can be pulled from the cache.  Pulling from the cache is disabled by
    default."""
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

    # Returns the cached request if it was pulled within the
    # 'acceptable_cache_age' limit.
    last_request_time = cached_requests.get(api_url, {}).get('last_requested', 0)
    if (time.time() - last_request_time) < acceptable_cache_age:
        return cached_requests[api_url]['data']

    # 'cache_last_modified' is the time that the data in the cache was
    # published to TBA's API.
    cache_last_modified = cached_requests.get(api_url, {}).get('last_modified')
    if cache_last_modified is not None:
        request_headers['If-Modified-Since'] = cache_last_modified

    if show_output is True:
        print(f'Retrieving data from TBA...\nURL: {api_url}')
    while True:
        try:
            request_time = time.time()
            request = requests.get(full_url, headers=request_headers)
        except requests.exceptions.ConnectionError:
            # Errors will always be shown, even if 'show_output' is False.
            print('Error: No internet connection.  Trying again in 3 seconds...')
        else:
            if show_output is True:
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
            'last_requested': request_time,
            'last_modified': request.headers['Last-Modified'],
            'data': request.json(),
        }
        with open(utils.create_file_path('data/cache/tba/tba.json'), 'w') as file_:
            json.dump(cached_requests, file_)
        return request.json()
    else:
        # Errors will always be shown, even if 'show_output' is False.
        print(f'Request failed with status code {request.status_code}')
        return {}

# TODO: Research better methods to pass optional arguments through functions
def request_match(match_key, show_output=True, acceptable_cache_age=0):
    """Requests data for a single match from the TBA API.

    match_key is a string.  (e.g. '2019caoc_qm29', '2019caoc_qf3m1')"""
    return make_request(f'match/{match_key}', show_output, acceptable_cache_age)

def request_rankings(show_output=True, acceptable_cache_age=0):
    """Requests the team rankings for an event from the TBA API."""
    return make_request(f'event/{EVENT_CODE}/rankings', show_output, acceptable_cache_age)

def request_matches(show_output=True, acceptable_cache_age=0):
    """Requests the match schedule from the TBA API."""
    return make_request(f'event/{EVENT_CODE}/matches/simple', show_output, acceptable_cache_age)

def request_match_keys(show_output=True, acceptable_cache_age=0):
    """Requests match keys (names) from the TBA API.

    Match key format: {event_code}_{match_number}
    (e.g. '2019caoc_qm29' [qualification match 29],
    '2019caoc_qf3m1' [quarter finals 3-1])"""
    return make_request(f'event/{EVENT_CODE}/matches/keys', show_output, acceptable_cache_age)

def request_teams(show_output=True, acceptable_cache_age=0):
    """Requests the team list from the TBA API."""
    return make_request(f'event/{EVENT_CODE}/teams/simple', show_output, acceptable_cache_age)
