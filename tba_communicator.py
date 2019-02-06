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
