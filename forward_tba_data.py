#!/usr/bin/python3.6
"""Forwards data from TBA (The Blue Alliance) to Teams, TIMDs, and Matches.

Called by server.py"""
# External imports
import json
# Internal imports
import tba_communicator
import utils

def update_json_file(file_path, updated_data):
    """Updates file data in a JSON file.  (Preserves old data)

    file_path is the absolute path of the file to be updated (string)
    updated_data is the data to add to the JSON file (dict)"""
    try:
        with open(file_path, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        file_data = {}
    # Used for nested dictionaries (i.e. 'calculatedData')
    for key, value in updated_data.items():
        if isinstance(value, dict):
            file_data[key] = file_data.get(key, {})
            file_data[key].update(value)
        else:
            file_data[key] = value
    with open(file_path, 'w') as file:
        json.dump(file_data, file)

def save_data(file_path, data):
    """Saves data in 'cache' and 'upload_queue' directories.

    file_path is the relative file path from inside the 'cache' or
    'upload_queue' folder. (string)
    data is the data to save."""
    # Removes preceding slash
    if file_path[0] == '/':
        file_path = file_path[1:]
    update_json_file(utils.create_file_path(f'data/cache/{file_path}'), data)
    update_json_file(utils.create_file_path(
        f'data/upload_queue/{file_path}'), data)


# Team data
RANKINGS = tba_communicator.request_rankings()['rankings']
for team in RANKINGS:
    # Removes preceding 'frc'
    # (e.g. 'frc1678' becomes '1678')
    team_number = team['team_key'][3:]
    team_data = {
        'actualRPs': team['extra_stats'][0],
        'matchesPlayed': team['matches_played'],
        'calculatedData': {
            'actualSeed': team['rank'],
        },
    }
    save_data(f'teams/{team_number}.json', team_data)

